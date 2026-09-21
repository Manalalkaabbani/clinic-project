"""
analysis.py (v2 — simplified schema)
Loads data from the clinic SQLite database, cleans it, and runs:
  - Trend analysis (monthly diagnosis volume, revenue)
  - Segmentation (patients by age group / city, revenue by department)
  - A simple payment-risk prediction model (logistic regression)
"""

import sqlite3
import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "analysis_outputs")
os.makedirs(OUT_DIR, exist_ok=True)

conn = sqlite3.connect(os.path.join(BASE_DIR, "clinic.db"))

# ---------------- Load ----------------
patients = pd.read_sql_query("SELECT * FROM patients", conn, parse_dates=["dob", "registration_date"])
doctors = pd.read_sql_query("SELECT * FROM doctors", conn)
departments = pd.read_sql_query("SELECT * FROM departments", conn)
diagnoses = pd.read_sql_query("SELECT * FROM diagnoses", conn, parse_dates=["diagnosis_date"])
billing = pd.read_sql_query("SELECT * FROM billing", conn, parse_dates=["billing_date"])
lab_tests = pd.read_sql_query("SELECT * FROM lab_tests", conn)

# ---------------- Clean ----------------
for df in [patients, diagnoses, billing]:
    df.drop_duplicates(inplace=True)

patients["city"] = patients["city"].str.strip().str.title()
patients["has_insurance"] = patients["insurance_id"].notna()
patients["age"] = ((pd.Timestamp.today() - patients["dob"]).dt.days / 365.25).astype(int)

print("=" * 60)
print("DATA OVERVIEW")
print("=" * 60)
print(f"Patients: {len(patients)} | Diagnoses: {len(diagnoses)} | Billing records: {len(billing)}")
print(f"Insured: {patients['has_insurance'].mean()*100:.1f}%")

# ---------------- Trend: monthly diagnosis volume ----------------
diagnoses["month"] = diagnoses["diagnosis_date"].dt.to_period("M").astype(str)
monthly_volume = diagnoses.groupby("month").size().reset_index(name="num_diagnoses")
monthly_volume.to_csv(f"{OUT_DIR}/monthly_diagnosis_volume.csv", index=False)

# ---------------- Trend: monthly revenue ----------------
billing["month"] = billing["billing_date"].dt.to_period("M").astype(str)
monthly_revenue = billing.groupby("month")["amount"].sum().reset_index()
monthly_revenue.to_csv(f"{OUT_DIR}/monthly_revenue.csv", index=False)

print("\n" + "=" * 60)
print("TRENDS")
print("=" * 60)
print(f"Peak diagnosis month: {monthly_volume.loc[monthly_volume['num_diagnoses'].idxmax(), 'month']}")
print(f"Peak revenue month: {monthly_revenue.loc[monthly_revenue['amount'].idxmax(), 'month']} "
      f"(EGP {monthly_revenue['amount'].max():,.2f})")

# ---------------- Segmentation ----------------
bins = [0, 18, 40, 60, 120]
labels = ["Under 18", "18-39", "40-59", "60+"]
patients["age_group"] = pd.cut(patients["age"], bins=bins, labels=labels, right=False)
age_segmentation = patients["age_group"].value_counts().reset_index()
age_segmentation.columns = ["age_group", "num_patients"]
age_segmentation.to_csv(f"{OUT_DIR}/age_segmentation.csv", index=False)

city_segmentation = patients["city"].value_counts().reset_index()
city_segmentation.columns = ["city", "num_patients"]
city_segmentation.to_csv(f"{OUT_DIR}/city_segmentation.csv", index=False)

diag_doc = diagnoses.merge(doctors, on="doctor_id").merge(departments, on="department_id")
diag_billing = diag_doc.merge(billing, on="diagnosis_id", how="inner")
dept_revenue = diag_billing.groupby("name")["amount"].sum().sort_values(ascending=False).reset_index()
dept_revenue.columns = ["department", "revenue"]
dept_revenue.to_csv(f"{OUT_DIR}/department_revenue.csv", index=False)

print("\n" + "=" * 60)
print("SEGMENTATION")
print("=" * 60)
print("Patients by age group:\n", age_segmentation.to_string(index=False))
print("\nTop department by revenue:", dept_revenue.iloc[0]["department"],
      f"(EGP {dept_revenue.iloc[0]['revenue']:,.2f})")

# ---------------- Prediction: overdue-payment risk ----------------
model_df = billing.merge(diagnoses[["diagnosis_id", "patient_id", "severity"]], on="diagnosis_id")
model_df = model_df.merge(patients[["patient_id", "age", "gender", "has_insurance"]], on="patient_id")
model_df["is_overdue"] = (model_df["payment_status"] == "Overdue").astype(int)
model_df["weekday"] = model_df["billing_date"].dt.dayofweek

le_gender = LabelEncoder()
model_df["gender_enc"] = le_gender.fit_transform(model_df["gender"])
le_sev = LabelEncoder()
model_df["severity_enc"] = le_sev.fit_transform(model_df["severity"])

features = ["age", "gender_enc", "has_insurance", "weekday", "severity_enc", "amount"]
X = model_df[features]
y = model_df["is_overdue"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
clf = LogisticRegression(max_iter=1000, class_weight="balanced")
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

print("\n" + "=" * 60)
print("PREDICTION: OVERDUE PAYMENT RISK MODEL (Logistic Regression)")
print("=" * 60)
print(f"Baseline overdue rate: {y.mean()*100:.1f}%")
print(f"Model accuracy: {accuracy_score(y_test, y_pred)*100:.1f}%")
print(classification_report(y_test, y_pred, target_names=["Not overdue", "Overdue"]))

coef_summary = pd.DataFrame({"feature": features, "coefficient": clf.coef_[0]}).sort_values("coefficient", ascending=False)
coef_summary.to_csv(f"{OUT_DIR}/overdue_model_coefficients.csv", index=False)
print("\nFeature influence on overdue risk (positive = increases risk):")
print(coef_summary.to_string(index=False))

print("\nAll summary CSVs saved to:", OUT_DIR)
conn.close()
