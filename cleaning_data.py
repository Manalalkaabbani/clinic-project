"""Assess and clean the CarePath SQL Server tables with Pandas.

By default, verified cleaning changes are applied to the existing ``dbo``
tables in one transaction. Full pre-cleaning backups are exported before any
database updates. Use ``--assessment-only`` to avoid database writes.

Run from the project root:
    python cleaning_data.py

An optional as-of date makes future-date checks reproducible:
    python cleaning_data.py --as-of 2026-09-26

To assess without changing SQL Server:
    python cleaning_data.py --assessment-only
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import date, datetime, time
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine, URL


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = BASE_DIR / "analysis_outputs" / "cleaning_data"

# These are the eight SQL Server tables used by the Flask application.
TABLES = (
    "departments",
    "doctors",
    "insurance_providers",
    "patients",
    "appointments",
    "diagnoses",
    "billing",
    "lab_tests",
)

PRIMARY_KEYS = {
    "departments": "department_id",
    "doctors": "doctor_id",
    "insurance_providers": "insurance_id",
    "patients": "patient_id",
    "appointments": "appointment_id",
    "diagnoses": "diagnosis_id",
    "billing": "billing_id",
    "lab_tests": "lab_test_id",
}

DATE_COLUMNS = {
    "dob",
    "registration_date",
    "appointment_date",
    "diagnosis_date",
    "billing_date",
    "test_date",
}

STRING_COLUMNS = {
    "departments": ["name"],
    "doctors": ["first_name", "last_name", "specialty"],
    "insurance_providers": ["provider_name", "coverage_type", "contact_phone"],
    "patients": ["first_name", "last_name", "gender", "city"],
    "appointments": ["status", "reason_for_visit"],
    "diagnoses": ["diagnosis_code", "description", "severity"],
    "billing": ["payment_status", "payment_method"],
    "lab_tests": ["test_type", "result_status"],
}

# Repeated billing, diagnosis, and lab-test keys can be real events. They are
# reported for review, not deleted.
BUSINESS_KEYS = {
    "appointments": (
        ["patient_id", "doctor_id", "appointment_date", "appointment_time"],
        "Same patient, doctor, date, and time may be a scheduling duplicate; retain for review.",
    ),
    "diagnoses": (
        ["appointment_id", "diagnosis_code"],
        "An appointment may contain repeated diagnoses; retain for clinical review.",
    ),
    "billing": (
        ["diagnosis_id"],
        "A diagnosis may have multiple billing entries; retain as separate transactions.",
    ),
    "lab_tests": (
        ["diagnosis_id", "test_type", "test_date"],
        "Repeated tests may be separate orders; retain as separate events.",
    ),
}

FOREIGN_KEYS = (
    ("doctors", "department_id", "departments", "department_id"),
    ("patients", "insurance_id", "insurance_providers", "insurance_id"),
    ("appointments", "patient_id", "patients", "patient_id"),
    ("appointments", "doctor_id", "doctors", "doctor_id"),
    ("diagnoses", "appointment_id", "appointments", "appointment_id"),
    ("diagnoses", "patient_id", "patients", "patient_id"),
    ("diagnoses", "doctor_id", "doctors", "doctor_id"),
    ("billing", "diagnosis_id", "diagnoses", "diagnosis_id"),
    ("lab_tests", "diagnosis_id", "diagnoses", "diagnosis_id"),
)

MISSING_DECISIONS = {
    ("insurance_providers", "contact_phone"): (
        "Optional contact information was not supplied.",
        "Retain as missing; a phone number cannot safely be inferred.",
    ),
    ("patients", "dob"): (
        "Date of birth is absent for some patient records.",
        "Retain as missing; do not invent age or date of birth.",
    ),
    ("patients", "gender"): (
        "Gender is absent for some patient records.",
        "Retain as missing; it cannot be inferred from names or other fields.",
    ),
    ("patients", "city"): (
        "City is absent for some patient records.",
        "Retain as missing; do not assign a default location.",
    ),
    ("patients", "insurance_id"): (
        "No insurer is linked to these patients; this represents self-pay or no recorded insurance.",
        "Retain as missing; it has business meaning and is not a broken relationship.",
    ),
    ("patients", "registration_date"): (
        "The date was not supplied for some records; some additional dates may be after the run's as-of date.",
        "Retain missing values. Set future registration dates to missing because the actual date is unknown; report the original values.",
    ),
    ("appointments", "appointment_date"): (
        "The appointment date is absent for some records.",
        "Retain as missing; do not remove the appointment or invent a date.",
    ),
    ("appointments", "appointment_time"): (
        "The appointment time is absent for some records.",
        "Retain as missing; an appointment can still be useful by date/status.",
    ),
    ("appointments", "status"): (
        "The appointment outcome/status was not recorded.",
        "Retain as missing; do not infer whether the visit was completed or missed.",
    ),
    ("appointments", "reason_for_visit"): (
        "The optional visit reason is absent.",
        "Retain as missing; the appointment remains usable for scheduling analysis.",
    ),
    ("diagnoses", "description"): (
        "The diagnosis description is absent for some records.",
        "Retain as missing; exclude those values from description-specific analysis rather than inventing a diagnosis.",
    ),
    ("diagnoses", "severity"): (
        "Severity is absent for some records.",
        "Retain as missing; do not infer clinical severity.",
    ),
    ("diagnoses", "diagnosis_date"): (
        "The diagnosis date is absent for some records.",
        "Retain as missing; exclude from date-based trends where no date is available.",
    ),
    ("billing", "amount"): (
        "The amount is not recorded for some billing entries.",
        "Retain as missing; financial values must not be imputed with zero, mean, or median.",
    ),
    ("billing", "payment_status"): (
        "The payment status is not recorded for some billing entries.",
        "Retain as missing and count separately as unspecified; do not guess a status.",
    ),
    ("billing", "payment_method"): (
        "The payment method is not recorded for some billing entries.",
        "Retain as missing; do not infer the payment method.",
    ),
    ("billing", "billing_date"): (
        "The billing date is absent for some records.",
        "Retain as missing; exclude from date-based revenue trends.",
    ),
    ("lab_tests", "result_status"): (
        "The result status is absent for some tests.",
        "Retain as missing; do not assume a result or interpret it as normal.",
    ),
    ("lab_tests", "test_date"): (
        "The test date is absent for some records.",
        "Retain as missing; exclude from date-based trends.",
    ),
}

SPECIAL_CASE_VALUES = {
    ("departments", "name"): {
        "urology": "Urology",
        "gastroenterology": "Gastroenterology",
    },
    ("patients", "city"): {
        "beni suef": "Beni Suef",
        "port said": "Port Said",
        "shubra el-kheima": "Shubra El-Kheima",
    },
    ("insurance_providers", "provider_name"): {
        "al salam insurance": "Al Salam Insurance",
    },
    ("insurance_providers", "coverage_type"): {
        "null": "Unknown",
    },
}


def make_engine() -> Engine:
    """Create the same SQL Server connection used by the RCM backend."""
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return create_engine(database_url, pool_pre_ping=True)

    return create_engine(
        URL.create(
            "mssql+pyodbc",
            host=r"MAROZZ\SQLEXPRESS",
            database="HealthCare",
            query={
                "driver": "ODBC Driver 18 for SQL Server",
                "trusted_connection": "yes",
                "Encrypt": "yes",
                "TrustServerCertificate": "yes",
                "Application Name": "CarePath Data Cleaning",
            },
        ),
        pool_pre_ping=True,
    )


def load_data(connection: Connection) -> dict[str, pd.DataFrame]:
    """Load all application tables through an existing SQL Server connection."""
    return {
        table: pd.read_sql_query(
            text(
                f"SELECT * FROM dbo.[{table}] "
                f"ORDER BY [{PRIMARY_KEYS[table]}]"
            ),
            connection,
        )
        for table in TABLES
    }


def export_source_backups(
    frames: dict[str, pd.DataFrame],
    output_dir: Path,
    as_of_date: pd.Timestamp,
) -> Path:
    """Export full, timestamped CSV and Pickle backups before database writes."""
    backup_dir = (
        output_dir
        / "backups"
        / f"source_before_cleaning_{datetime.now():%Y%m%d_%H%M%S_%f}_{uuid4().hex[:8]}"
    )
    backup_dir.mkdir(parents=True, exist_ok=False)
    manifest: dict[str, Any] = {
        "database": "HealthCare",
        "schema": "dbo",
        "as_of_date": str(as_of_date.date()),
        "backup_created_at": datetime.now().isoformat(timespec="seconds"),
        "purpose": "Full source snapshot exported before in-place cleaning.",
        "tables": {},
    }

    for table, frame in frames.items():
        csv_path = backup_dir / f"{table}.csv"
        pickle_path = backup_dir / f"{table}.pkl"
        frame.to_csv(csv_path, index=False, na_rep="__SQL_NULL__")
        frame.to_pickle(pickle_path)

        restored = pd.read_pickle(pickle_path)
        if restored.shape != frame.shape or list(restored.columns) != list(frame.columns):
            raise RuntimeError(f"Backup verification failed for dbo.{table}.")

        manifest["tables"][table] = {
            "rows": len(frame),
            "columns": list(frame.columns),
            "csv": csv_path.name,
            "csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
            "pickle": pickle_path.name,
            "pickle_sha256": hashlib.sha256(pickle_path.read_bytes()).hexdigest(),
        }

    manifest_path = backup_dir / "backup_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return backup_dir


def _same_scalar(left: Any, right: Any) -> bool:
    left_missing = pd.isna(left)
    right_missing = pd.isna(right)
    if left_missing and right_missing:
        return True
    if left_missing or right_missing:
        return False
    return bool(left == right)


def apply_cleaning_in_place(
    engine: Engine,
    before: dict[str, pd.DataFrame],
    cleaned: dict[str, pd.DataFrame],
    as_of_date: pd.Timestamp,
    commit_changes: bool = True,
) -> dict[str, int]:
    """Apply approved corrections and optionally roll back after verification."""
    update_counts: dict[str, int] = {}

    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            for table, frame in before.items():
                expected_rows = len(frame)
                actual_rows = connection.execute(
                    text(f"SELECT COUNT_BIG(*) FROM dbo.[{table}]")
                ).scalar_one()
                if actual_rows != expected_rows:
                    raise RuntimeError(
                        f"dbo.{table} changed after assessment "
                        f"(expected {expected_rows:,} rows, found {actual_rows:,}); "
                        "no cleaning updates were committed. Rerun the assessment."
                    )

            for table, columns in STRING_COLUMNS.items():
                primary_key = PRIMARY_KEYS[table]
                for column in columns:
                    original = before[table]
                    target = cleaned[table]
                    changes: dict[tuple[str | None, str | None], list[int]] = {}

                    for record_id, old_value, new_value in zip(
                        original[primary_key],
                        original[column],
                        target[column],
                    ):
                        if _same_scalar(old_value, new_value):
                            continue
                        old_key = None if pd.isna(old_value) else str(old_value)
                        new_key = None if pd.isna(new_value) else str(new_value)
                        changes.setdefault((old_key, new_key), []).append(int(record_id))

                    for (old_value, new_value), record_ids in changes.items():
                        for offset in range(0, len(record_ids), 800):
                            batch = record_ids[offset : offset + 800]
                            id_parameters = {
                                f"id_{index}": record_id
                                for index, record_id in enumerate(batch)
                            }
                            id_placeholders = ", ".join(
                                f":id_{index}" for index in range(len(batch))
                            )
                            if old_value is None:
                                old_check = f"[{column}] IS NULL"
                                parameters = id_parameters
                            else:
                                old_check = (
                                    "CONVERT(varbinary(max), "
                                    f"CONVERT(nvarchar(max), [{column}])) = "
                                    "CONVERT(varbinary(max), "
                                    "CONVERT(nvarchar(max), :old_value))"
                                )
                                parameters = {**id_parameters, "old_value": old_value}

                            new_expression = "NULL" if new_value is None else ":new_value"
                            if new_value is not None:
                                parameters["new_value"] = new_value

                            result = connection.execute(
                                text(
                                    f"UPDATE dbo.[{table}] "
                                    f"SET [{column}] = {new_expression} "
                                    f"WHERE [{primary_key}] IN ({id_placeholders}) "
                                    f"AND {old_check}"
                                ),
                                parameters,
                            )
                            if result.rowcount != len(batch):
                                raise RuntimeError(
                                    f"Update verification failed for dbo.{table}."
                                    f"{column}: expected {len(batch)} rows, "
                                    f"updated {result.rowcount}. Transaction rolled back."
                                )
                            update_counts[table] = (
                                update_counts.get(table, 0) + result.rowcount
                            )

            future_ids = before["patients"].loc[
                pd.to_datetime(before["patients"]["registration_date"]).gt(as_of_date),
                "patient_id",
            ].astype(int).tolist()
            for offset in range(0, len(future_ids), 800):
                batch = future_ids[offset : offset + 800]
                parameters = {
                    f"id_{index}": patient_id
                    for index, patient_id in enumerate(batch)
                }
                placeholders = ", ".join(
                    f":id_{index}" for index in range(len(batch))
                )
                parameters["as_of_date"] = as_of_date.date()
                result = connection.execute(
                    text(
                        "UPDATE dbo.[patients] SET [registration_date] = NULL "
                        f"WHERE [patient_id] IN ({placeholders}) "
                        "AND [registration_date] > :as_of_date"
                    ),
                    parameters,
                )
                if result.rowcount != len(batch):
                    raise RuntimeError(
                        "Future registration-date verification failed; "
                        "transaction rolled back."
                    )
                update_counts["patients"] = (
                    update_counts.get("patients", 0) + result.rowcount
                )

            persisted = load_data(connection)
            _verify_persisted_values(cleaned, persisted)

            for table, expected_rows in (
                (table, len(frame)) for table, frame in before.items()
            ):
                actual_rows = len(persisted[table])
                if actual_rows != expected_rows:
                    raise RuntimeError(
                        f"Post-cleaning row-count verification failed for dbo.{table}; "
                        "transaction rolled back."
                    )

            if commit_changes:
                transaction.commit()
            else:
                transaction.rollback()
        except Exception:
            if transaction.is_active:
                transaction.rollback()
            raise

    return update_counts


def _verify_persisted_values(
    expected: dict[str, pd.DataFrame],
    persisted: dict[str, pd.DataFrame],
) -> None:
    """Verify every cleaned text and date field against rows reloaded from SQL."""
    for table, columns in STRING_COLUMNS.items():
        for column in columns:
            expected_values = expected[table][column].astype("string").reset_index(drop=True)
            persisted_values = persisted[table][column].astype("string").reset_index(drop=True)
            if not expected_values.equals(persisted_values):
                raise RuntimeError(
                    f"Post-update verification failed for dbo.{table}.{column}; "
                    "transaction rolled back."
                )

    for table, frame in expected.items():
        for column in DATE_COLUMNS.intersection(frame.columns):
            expected_values = pd.to_datetime(frame[column]).reset_index(drop=True)
            persisted_values = pd.to_datetime(
                persisted[table][column]
            ).reset_index(drop=True)
            if not expected_values.equals(persisted_values):
                raise RuntimeError(
                    f"Post-update date verification failed for dbo.{table}.{column}; "
                    "transaction rolled back."
                )


def _column_action(table: str, column: str) -> str:
    if (table, column) in MISSING_DECISIONS:
        decision = MISSING_DECISIONS[(table, column)][1]
    else:
        decision = "No missing-value imputation; preserve observed values."

    if column.endswith("_id"):
        return f"Cast identifier to nullable integer; retain keys. {decision}"
    if column in DATE_COLUMNS:
        return f"Parse as datetime; retain missing dates. {decision}"
    if table == "appointments" and column == "appointment_time":
        return f"Normalize to HH:MM:SS string; retain missing times. {decision}"
    if table == "billing" and column == "amount":
        return f"Cast to numeric; retain missing, zero, and outlier amounts. {decision}"
    if table == "insurance_providers" and column == "coverage_type":
        return (
            "Trim/collapse whitespace; standardize the observed literal 'NULL' "
            "placeholder to the existing 'Unknown' category."
        )
    if column in STRING_COLUMNS.get(table, []):
        return (
            "Use Pandas string dtype; trim/collapse whitespace and standardize "
            "case-only aliases when observed; retain missing text."
        )
    return decision


def _quality_report(
    frames: dict[str, pd.DataFrame],
    phase: str,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for table, frame in frames.items():
        for column in frame.columns:
            missing_count = int(frame[column].isna().sum())
            rows.append(
                {
                    "Phase": phase,
                    "Table": table,
                    "Column": column,
                    "Data Type": str(frame[column].dtype),
                    "Missing Count": missing_count,
                    "Missing %": round(
                        100 * missing_count / len(frame), 3
                    ) if len(frame) else 0.0,
                    "Unique Values": int(frame[column].nunique(dropna=True)),
                    "Cleaning Action": _column_action(table, column),
                }
            )
    return pd.DataFrame(rows)


def _duplicate_report(
    before: dict[str, pd.DataFrame],
    after: dict[str, pd.DataFrame] | None = None,
) -> pd.DataFrame:
    rows = []
    for table, original in before.items():
        cleaned = after[table] if after is not None else None
        primary_key = PRIMARY_KEYS[table]
        business_key, note = BUSINESS_KEYS.get(
            table, ([], "No additional business-key check configured.")
        )
        for phase, frame in (("Before", original), ("After", cleaned)):
            if frame is None:
                continue
            rows.append(
                {
                    "Table": table,
                    "Phase": phase,
                    "Duplicate Full Rows": int(frame.duplicated().sum()),
                    "Duplicate Primary Key Rows": int(
                        frame[primary_key].duplicated().sum()
                    ),
                    "Business Key": ", ".join(business_key) or "Not configured",
                    "Duplicate Business Key Rows": (
                        int(frame.duplicated(business_key).sum())
                        if business_key
                        else 0
                    ),
                    "Business Duplicate Interpretation": note,
                }
            )
    return pd.DataFrame(rows)


def _normalize_text_column(
    series: pd.Series,
) -> tuple[pd.Series, list[dict[str, Any]]]:
    """Collapse whitespace and choose the most common casing for aliases."""
    original = series.astype("string")
    normalized = original.str.replace(r"\s+", " ", regex=True).str.strip()
    normalized = normalized.mask(normalized.eq(""), pd.NA)

    non_missing = normalized.dropna()
    alias_map: dict[str, str] = {}
    if not non_missing.empty:
        keys = non_missing.str.casefold()
        for key, values in non_missing.groupby(keys):
            if values.nunique() > 1:
                counts = values.value_counts()
                alias_map[key] = str(counts.index[0])

    standardized = normalized.map(
        lambda value: alias_map.get(value.casefold(), value)
        if isinstance(value, str)
        else value
    ).astype("string")

    changes = pd.DataFrame(
        {"old": original, "new": standardized}
    )
    changes = changes.loc[
        changes["old"].notna()
        & changes["new"].notna()
        & changes["old"].ne(changes["new"])
    ]
    change_rows = [
        {
            "Old Value": old,
            "New Value": new,
            "Rows Changed": int(count),
        }
        for (old, new), count in changes.groupby(
            ["old", "new"], dropna=False
        ).size().items()
    ]
    return standardized, change_rows


def _normalize_appointment_time(series: pd.Series) -> pd.Series:
    def to_time_string(value: Any) -> Any:
        if pd.isna(value):
            return pd.NA
        if isinstance(value, time):
            return value.strftime("%H:%M:%S")
        if isinstance(value, datetime):
            return value.strftime("%H:%M:%S")
        parsed = pd.to_datetime(str(value), errors="coerce")
        if pd.isna(parsed):
            return pd.NA
        return parsed.strftime("%H:%M:%S")

    return series.map(to_time_string).astype("string")


def _clean_frames(
    before: dict[str, pd.DataFrame],
    as_of_date: pd.Timestamp,
) -> tuple[
    dict[str, pd.DataFrame],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    """Return cleaned copies, value changes, date issues, and new-missing decisions."""
    cleaned = {table: frame.copy(deep=True) for table, frame in before.items()}
    value_changes: list[dict[str, Any]] = []
    date_issues: list[dict[str, Any]] = []
    newly_missing: list[dict[str, Any]] = []
    future_registration_records: list[dict[str, Any]] = []

    for table, frame in cleaned.items():
        for column in STRING_COLUMNS[table]:
            frame[column], changes = _normalize_text_column(frame[column])
            value_changes.extend(
                {"Table": table, "Column": column, **change}
                for change in changes
            )

        if table == "appointments":
            frame["appointment_time"] = _normalize_appointment_time(
                frame["appointment_time"]
            )

        if table == "diagnoses":
            frame["diagnosis_code"] = frame["diagnosis_code"].str.upper()

        for (special_table, column), canonical_values in SPECIAL_CASE_VALUES.items():
            if table == special_table:
                normalized_lookup = {
                    key.casefold(): value for key, value in canonical_values.items()
                }
                original = frame[column].copy()
                frame[column] = frame[column].map(
                    lambda value: normalized_lookup.get(value.casefold(), value)
                    if isinstance(value, str)
                    else value
                ).astype("string")
                changed = original.notna() & frame[column].notna() & original.ne(frame[column])
                for old_value, new_value in zip(
                    original[changed], frame.loc[changed, column]
                ):
                    value_changes.append(
                        {
                            "Table": table,
                            "Column": column,
                            "Old Value": old_value,
                            "New Value": new_value,
                            "Rows Changed": 1,
                        }
                    )

        for column in DATE_COLUMNS.intersection(frame.columns):
            parsed = pd.to_datetime(frame[column], errors="coerce")
            invalid_parse = frame[column].notna() & parsed.isna()
            invalid_count = int(invalid_parse.sum())
            if invalid_count:
                date_issues.append(
                    {
                        "Table": table,
                        "Column": column,
                        "Issue": "Unparseable date",
                        "Rows": invalid_count,
                        "Action": "Set to NaT; original database value remains unchanged.",
                    }
                )

            future = parsed.gt(as_of_date)
            future_count = int(future.sum())
            if future_count:
                future_dates = parsed.loc[future]
                is_registration_date = (
                    table == "patients" and column == "registration_date"
                )
                if is_registration_date:
                    future_rows = frame.loc[
                        future, ["patient_id", column]
                    ]
                    future_registration_records.extend(
                        {
                            "patient_id": int(patient_id),
                            "original_registration_date": str(original_date),
                            "as_of_date": str(as_of_date.date()),
                        }
                        for patient_id, original_date in future_rows.itertuples(
                            index=False, name=None
                        )
                    )
                    parsed = parsed.mask(future)
                    action = (
                        "Set to NaT in cleaned data because the true registration "
                        "date cannot be confirmed; original values are preserved "
                        "in future_registration_dates.csv."
                    )
                    newly_missing.append(
                        {
                            "Table": table,
                            "Column": column,
                            "New Missing Count": future_count,
                            "Treatment": (
                                f"Set {future_count} future registration dates to NaT "
                                f"as of {as_of_date.date()}; original values are "
                                "preserved in future_registration_dates.csv."
                            ),
                        }
                    )
                else:
                    action = (
                        "Retain and flag for review; planned appointments or "
                        "future-dated imported events cannot be distinguished "
                        "reliably from invalid dates using this data alone."
                    )
                date_issues.append(
                    {
                        "Table": table,
                        "Column": column,
                        "Issue": (
                            "Future registration date"
                            if is_registration_date
                            else "Future-dated event"
                        ),
                        "Rows": future_count,
                        "Earliest": str(future_dates.min()),
                        "Latest": str(future_dates.max()),
                        "Action": action,
                    }
                )

            frame[column] = parsed

        for column in frame.columns:
            if column.endswith("_id"):
                frame[column] = pd.to_numeric(
                    frame[column], errors="coerce"
                ).astype("Int64")

        if table == "billing":
            frame["amount"] = pd.to_numeric(
                frame["amount"], errors="coerce"
            ).astype("Float64")

    return (
        cleaned,
        value_changes,
        date_issues,
        newly_missing,
        future_registration_records,
    )


def _numeric_report(
    frames: dict[str, pd.DataFrame],
    as_of_date: pd.Timestamp,
) -> pd.DataFrame:
    rows = []

    def add_numeric_summary(
        table: str,
        column: str,
        values: pd.Series,
        action: str,
    ) -> None:
        values = pd.to_numeric(values, errors="coerce").dropna()
        if values.empty:
            return
        q1 = float(values.quantile(0.25))
        q3 = float(values.quantile(0.75))
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        rows.append(
            {
                "Table": table,
                "Column": column,
                "Non-missing Values": int(values.size),
                "Minimum": float(values.min()),
                "Median": float(values.median()),
                "Mean": float(values.mean()),
                "Maximum": float(values.max()),
                "Zero Values": int(values.eq(0).sum()),
                "Negative Values": int(values.lt(0).sum()),
                "IQR Lower Bound": lower,
                "IQR Upper Bound": upper,
                "IQR Outlier Rows": int(
                    (values.lt(lower) | values.gt(upper)).sum()
                ),
                "Action": action,
            }
        )

    for table, frame in frames.items():
        for column in frame.select_dtypes(include=["number"]).columns:
            if column.endswith("_id"):
                continue
            add_numeric_summary(
                table,
                column,
                frame[column],
                "Flag only; retain observed values for business review.",
            )

    dob = pd.to_datetime(frames["patients"]["dob"], errors="coerce")
    birthday_not_reached = dob.dt.month.gt(as_of_date.month) | (
        dob.dt.month.eq(as_of_date.month)
        & dob.dt.day.gt(as_of_date.day)
    )
    age = (
        as_of_date.year
        - dob.dt.year
        - birthday_not_reached.astype("Int64")
    )
    add_numeric_summary(
        "patients",
        "age (derived from dob)",
        age,
        "Audit-only age derived from DOB and as-of date; flag IQR values, retain DOB.",
    )
    return pd.DataFrame(rows)


def _missing_analysis_report(
    before: dict[str, pd.DataFrame],
    after: dict[str, pd.DataFrame],
    newly_missing: list[dict[str, Any]],
) -> pd.DataFrame:
    added: dict[tuple[str, str], int] = {}
    added_notes: dict[tuple[str, str], list[str]] = {}
    for item in newly_missing:
        key = (item["Table"], item["Column"])
        added[key] = added.get(key, 0) + int(item["New Missing Count"])
        added_notes.setdefault(key, []).append(item["Treatment"])

    rows = []
    for table, frame in before.items():
        for column in frame.columns:
            old_count = int(frame[column].isna().sum())
            new_count = int(after[table][column].isna().sum())
            key = (table, column)
            if old_count == 0 and new_count == 0 and key not in added:
                continue
            reason, treatment = MISSING_DECISIONS.get(
                key,
                (
                    "A source value is missing or an explicit null placeholder was observed.",
                    "Retain as missing; do not infer a replacement.",
                ),
            )
            added_text = " ".join(added_notes.get(key, []))
            if added_text:
                treatment = f"{treatment} {added_text}"
            rows.append(
                {
                    "Table": table,
                    "Column": column,
                    "Before Missing": old_count,
                    "New Missing During Cleaning": added.get(key, 0),
                    "After Missing": new_count,
                    "Why Missing?": reason,
                    "Treatment and Rationale": treatment,
                }
            )
    return pd.DataFrame(rows)


def _text_consistency_report(
    before: dict[str, pd.DataFrame],
    after: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows = []
    for table, columns in STRING_COLUMNS.items():
        for column in columns:
            raw = before[table][column].astype("string")
            cleaned = after[table][column].astype("string")
            present = raw.dropna()
            normalized = present.str.replace(r"\s+", " ", regex=True).str.strip()
            groups = pd.DataFrame(
                {
                    "key": normalized.str.casefold(),
                    "raw": present,
                }
            ).groupby("key")["raw"].nunique()
            rows.append(
                {
                    "Table": table,
                    "Column": column,
                    "Leading or Trailing Whitespace Rows": int(
                        present.ne(present.str.strip()).sum()
                    ),
                    "Repeated Internal Whitespace Rows": int(
                        present.str.contains(r"\s{2,}", regex=True).sum()
                    ),
                    "Case/Whitespace Alias Groups": int(groups.gt(1).sum()),
                    "Unique Values Before": int(raw.nunique(dropna=True)),
                    "Unique Values After": int(cleaned.nunique(dropna=True)),
                    "Rows Changed": int(
                        raw.fillna("").ne(cleaned.fillna("")).sum()
                    ),
                }
            )
    return pd.DataFrame(rows)


def _foreign_key_report(
    frames: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows = []
    for child_table, child_column, parent_table, parent_column in FOREIGN_KEYS:
        child_values = frames[child_table][child_column].dropna()
        missing_targets = int(
            (~child_values.isin(frames[parent_table][parent_column])).sum()
        )
        rows.append(
            {
                "Table": child_table,
                "Column": child_column,
                "Referenced Table": parent_table,
                "Referenced Column": parent_column,
                "Missing Parent Rows": missing_targets,
            }
        )
    return pd.DataFrame(rows)


def _before_after_summary(
    before: dict[str, pd.DataFrame],
    after: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows = []
    for table in before:
        original = before[table]
        cleaned = after[table]
        rows.append(
            {
                "Table": table,
                "Before Rows": len(original),
                "After Rows": len(cleaned),
                "Before Columns": len(original.columns),
                "After Columns": len(cleaned.columns),
                "Rows Removed": len(original) - len(cleaned),
                "Before Missing Cells": int(original.isna().sum().sum()),
                "After Missing Cells": int(cleaned.isna().sum().sum()),
                "Before Duplicate Full Rows": int(original.duplicated().sum()),
                "After Duplicate Full Rows": int(cleaned.duplicated().sum()),
                "Before Duplicate Primary Keys": int(
                    original[PRIMARY_KEYS[table]].duplicated().sum()
                ),
                "After Duplicate Primary Keys": int(
                    cleaned[PRIMARY_KEYS[table]].duplicated().sum()
                ),
                "Before Dtypes": json.dumps(
                    {column: str(dtype) for column, dtype in original.dtypes.items()}
                ),
                "After Dtypes": json.dumps(
                    {column: str(dtype) for column, dtype in cleaned.dtypes.items()}
                ),
            }
        )
    return pd.DataFrame(rows)


def _write_summary(
    path: Path,
    before: dict[str, pd.DataFrame],
    after: dict[str, pd.DataFrame],
    as_of_date: pd.Timestamp,
    numeric_report: pd.DataFrame,
    value_changes: list[dict[str, Any]],
    date_issues: list[dict[str, Any]],
    backup_dir: Path | None,
    update_counts: dict[str, int],
    dry_run_database: bool,
) -> None:
    total_rows = sum(len(frame) for frame in before.values())
    before_missing = sum(int(frame.isna().sum().sum()) for frame in before.values())
    after_missing = sum(int(frame.isna().sum().sum()) for frame in after.values())
    before_duplicates = sum(int(frame.duplicated().sum()) for frame in before.values())
    after_duplicates = sum(int(frame.duplicated().sum()) for frame in after.values())

    amount_outliers = 0
    zero_amounts = 0
    if not numeric_report.empty:
        amount_rows = numeric_report.loc[
            (numeric_report["Table"] == "billing")
            & (numeric_report["Column"] == "amount")
        ]
        if not amount_rows.empty:
            amount_outliers = int(amount_rows.iloc[0]["IQR Outlier Rows"])
            zero_amounts = int(amount_rows.iloc[0]["Zero Values"])

    lines = [
        "DATA CLEANING SUMMARY",
        f"As-of date: {as_of_date.date()}",
        f"Tables assessed: {len(before)}",
        f"Rows assessed: {total_rows:,}",
        f"Missing cells before: {before_missing:,}",
        f"Missing cells after: {after_missing:,}",
        f"Exact duplicate rows before/after: {before_duplicates:,}/{after_duplicates:,}",
        "Rows removed: 0",
        "Text value changes recorded: "
        f"{sum(int(item['Rows Changed']) for item in value_changes):,}",
        "Future or unparseable date issue rows reported: "
        f"{sum(int(item['Rows']) for item in date_issues):,}",
        f"Zero billing amounts retained: {zero_amounts:,}",
        f"Billing amount IQR outliers retained for review: {amount_outliers:,}",
        "",
        "Missing financial, clinical, demographic, and scheduling values were not",
        "filled with guessed values. Missingness remains explicit in the cleaned",
        "DataFrames. Repeated business keys and outliers are reported, not deleted.",
        (
            "SQL UPDATE statements were verified and rolled back (database dry run)."
            if dry_run_database
            else "Existing dbo source tables were updated in one SQL transaction."
            if backup_dir is not None
            else "Assessment-only run; SQL Server tables were not modified."
        ),
        (
            f"Database field updates verified then rolled back: {sum(update_counts.values()):,}"
            if dry_run_database
            else f"Database field updates committed: {sum(update_counts.values()):,}"
            if backup_dir is not None
            else "Database field updates: not run (assessment-only)."
        ),
        f"Pre-cleaning backups: {backup_dir or 'not created (assessment-only run)'}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


CLEANED_DATAFRAMES: dict[str, pd.DataFrame] = {}


def run_cleaning(
    as_of_date: date | str | pd.Timestamp | None = None,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    engine: Engine | None = None,
    write_database: bool = True,
    dry_run_database: bool = False,
) -> dict[str, pd.DataFrame]:
    """Assess, back up, clean dbo tables in place, and return Pandas DataFrames."""
    normalized_as_of = pd.Timestamp(as_of_date or date.today()).normalize()
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    if dry_run_database and not write_database:
        raise ValueError("database dry-run requires write_database=True.")

    owns_engine = engine is None
    active_engine = engine or make_engine()
    try:
        with active_engine.connect() as connection:
            before = load_data(connection)

        # The full assessment and cleaned target are derived before any SQL UPDATE.
        before_quality = _quality_report(before, "Before")
        before_foreign_keys = _foreign_key_report(before)

        (
            after,
            value_changes,
            date_issues,
            newly_missing,
            future_registration_records,
        ) = _clean_frames(before, normalized_as_of)

        backup_dir = (
            export_source_backups(before, destination, normalized_as_of)
            if write_database
            else None
        )
        update_counts = (
            apply_cleaning_in_place(
                active_engine,
                before,
                after,
                normalized_as_of,
                commit_changes=not dry_run_database,
            )
            if write_database
            else {}
        )

        after_quality = _quality_report(after, "After")
        duplicate_report = _duplicate_report(before, after)
        numeric_report = _numeric_report(before, normalized_as_of)
        foreign_keys = _foreign_key_report(after)
        summary = _before_after_summary(before, after)
        missing_analysis = _missing_analysis_report(before, after, newly_missing)
        text_consistency = _text_consistency_report(before, after)

        before_quality.to_csv(destination / "quality_before.csv", index=False)
        after_quality.to_csv(destination / "quality_after.csv", index=False)
        pd.concat(
            [before_quality, after_quality], ignore_index=True
        ).to_csv(destination / "quality_report.csv", index=False)
        duplicate_report.to_csv(destination / "duplicate_report.csv", index=False)
        numeric_report.to_csv(destination / "numeric_outlier_report.csv", index=False)
        pd.concat(
            [
                before_foreign_keys.assign(Phase="Before"),
                foreign_keys.assign(Phase="After"),
            ],
            ignore_index=True,
        ).to_csv(destination / "foreign_key_report.csv", index=False)
        pd.DataFrame(
            value_changes,
            columns=["Table", "Column", "Old Value", "New Value", "Rows Changed"],
        ).to_csv(destination / "standardized_values.csv", index=False)
        pd.DataFrame(date_issues).to_csv(destination / "date_issues.csv", index=False)
        pd.DataFrame(newly_missing).to_csv(
            destination / "new_missing_values.csv", index=False
        )
        missing_analysis.to_csv(
            destination / "missing_value_analysis.csv", index=False
        )
        text_consistency.to_csv(
            destination / "text_consistency_report.csv", index=False
        )
        pd.DataFrame(future_registration_records).to_csv(
            destination / "future_registration_dates.csv", index=False
        )
        summary.to_csv(destination / "before_after_summary.csv", index=False)

        for table, frame in after.items():
            frame.to_csv(destination / f"{table}_cleaned.csv", index=False)

        _write_summary(
            destination / "data_cleaning_summary.txt",
            before,
            after,
            normalized_as_of,
            numeric_report,
            value_changes,
            date_issues,
            backup_dir,
            update_counts,
            dry_run_database,
        )
    finally:
        if owns_engine:
            active_engine.dispose()

    global CLEANED_DATAFRAMES
    CLEANED_DATAFRAMES = after

    print(f"Data quality assessment completed before cleaning.")
    print(f"As-of date: {normalized_as_of.date()}")
    print(f"Output folder: {destination}")
    if backup_dir:
        print(f"Pre-cleaning SQL backups: {backup_dir}")
        print(
            (
                "In-place SQL updates validated then rolled back: "
                if dry_run_database
                else "Committed in-place SQL updates: "
            )
            + f"{sum(update_counts.values()):,} field updates across "
            f"{sum(bool(count) for count in update_counts.values())} tables"
        )
    else:
        print("Assessment-only run; SQL Server tables were not modified.")
    print("\nBefore vs after:")
    print(
        summary[
            [
                "Table",
                "Before Rows",
                "After Rows",
                "Before Missing Cells",
                "After Missing Cells",
                "Before Duplicate Full Rows",
                "After Duplicate Full Rows",
            ]
        ].to_string(index=False)
    )
    print("\nData cleaning summary:")
    print((destination / "data_cleaning_summary.txt").read_text(encoding="utf-8"))
    print(
        "In Python, use the returned dictionary (or "
        "CLEANED_DATAFRAMES after run_cleaning()) for EDA and modeling."
    )
    return after


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Assess and clean the CarePath SQL Server data with Pandas."
    )
    parser.add_argument(
        "--as-of",
        type=date.fromisoformat,
        default=date.today(),
        help="Date for future-registration checks (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Folder for cleaned CSVs and reports (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--assessment-only",
        action="store_true",
        help="Assess and export cleaned CSVs without updating SQL Server.",
    )
    parser.add_argument(
        "--database-dry-run",
        action="store_true",
        help=(
            "Run the SQL updates and verification in a transaction, then roll "
            "back without changing the database."
        ),
    )
    args = parser.parse_args()
    if args.assessment_only and args.database_dry_run:
        parser.error("--assessment-only and --database-dry-run cannot be used together.")
    run_cleaning(
        as_of_date=args.as_of,
        output_dir=args.output_dir,
        write_database=not args.assessment_only,
        dry_run_database=args.database_dry_run,
    )


if __name__ == "__main__":
    main()
