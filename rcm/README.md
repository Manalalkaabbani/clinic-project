# ClinicRCM — Full-Stack Web Interface

A real client-server web application for the clinic project: a Flask REST API
backend and a React (Vite + Tailwind) frontend. The backend connects to the
local SQL Server `HealthCare` database using Windows integrated authentication.

Chain: **Departments → Doctors → Patients (via Insurance) → Diagnoses → Billing → Lab Tests**

## Folder structure

```
rcm/
  backend/
    app.py           # Flask REST API
    requirements.txt  # Python backend dependencies
  frontend/
    src/
      api.js
      App.jsx
      components/     # Sidebar, KpiCard, Badge, DataTable, Modal
      pages/           # Dashboard, Departments, Doctors, Patients, Diagnoses, Payments, LabTests
    package.json
```

## 1. Run the backend

```
cd rcm/backend
pip install -r requirements.txt
python app.py
```

This starts the API at **http://localhost:5000**. Leave this terminal running.

By default, the API connects to `MAROZZ\SQLEXPRESS`, database `HealthCare`,
using ODBC Driver 18 and Windows integrated authentication. Override the
connection with the `DATABASE_URL` environment variable if needed. The SQL
Server ODBC driver must be installed on the machine.

## 2. Run the frontend

Open a **second** terminal:

```
cd rcm/frontend
npm install
npm run dev
```

This starts the app at **http://localhost:5173** — open that in your browser.

## 3. Assess and clean the SQL Server data

From the project root, run the Pandas cleaning script with the same local
SQL Server connection used by the API:

```
.\.venv\Scripts\python.exe .\cleaning_data.py --as-of 2026-09-26
```

The `--as-of` date can be changed to the date used for the analysis. By default,
the script assesses all eight application tables, exports full CSV and Pickle
backups under a unique folder in `analysis_outputs/cleaning_data/backups`, then
updates the existing `dbo` tables in one transaction. It normalizes observed
case/whitespace variants, maps the literal coverage value `NULL` to the existing
`Unknown` category (the SQL column is non-nullable), and flags future patient
registration dates before replacing them with the selected date sentinel.
Missing patient gender/city values are labeled `Unknown`; missing appointment
status, diagnosis severity, billing status/method, and lab result status are labeled
`Not Specified`. These labels identify missing categorical information without
guessing its real value. To satisfy the selected all-fields-filled policy,
missing or invalid dates use `2025-01-01`, missing appointment times use
`00:00:00`, missing billing amounts use `0`, and missing contact/free-text
values use `Not Specified`. Patients without a recorded insurer are linked to
one explicit `Unknown / Not Specified` insurance-provider row, preserving the
foreign key. These are placeholders, not verified facts: exclude or specially
handle them in date, time, financial, and demographic analysis to avoid
misleading results. The provider placeholder adds one row to that table.

The script does not delete existing rows or remove outliers and possible
duplicate business events. The transaction verifies row counts, foreign keys,
and re-read values before commit; errors roll the entire update transaction
back. A full source backup is exported before any database write.

Use `--assessment-only` to create the cleaned Pandas/CSV outputs and reports
without changing SQL Server. Use `--database-dry-run` to exercise the SQL
updates and verification inside a transaction, then roll it back. In Python,
call `run_cleaning()` to receive the cleaned Pandas DataFrames as a
table-name-to-DataFrame dictionary.

## API endpoints (for reference)

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/dashboard/summary` | KPIs + chart data |
| GET/POST | `/api/departments` | |
| GET/POST | `/api/doctors` | supports `?search=&specialty=&department_id=` |
| GET/POST | `/api/patients` | supports `?search=&city=` |
| GET/POST | `/api/diagnoses` | supports `?search=&severity=&department_id=` |
| GET/POST | `/api/billing` | supports `?status=&method=` |
| GET/POST | `/api/lab_tests` | supports `?test_type=&result_status=` |
| GET | `/api/insurance_providers` | for dropdowns |
| GET | `/api/options` | Current appointment, billing, and lab values for filters/forms |

All GET list endpoints support `?page=&per_page=` pagination.

## Notes

- The frontend and backend were both tested end-to-end (including the "Add"
  forms actually writing to the database and the UI refreshing) before this
  was handed over.
- The API uses the existing SQL Server tables and does not create or migrate
  tables automatically.
