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
appointments = pd.read_sql_query("SELECT * FROM appointments", conn, parse_dates=["appointment_date"])
doctors = pd.read_sql_query("SELECT * FROM doctors", conn)
departments = pd.read_sql_query("SELECT * FROM departments", conn)
billing = pd.read_sql_query("SELECT * FROM billing", conn, parse_dates=["billing_date"])
diagnoses = pd.read_sql_query("SELECT * FROM diagnoses", conn)
treatments = pd.read_sql_query("SELECT * FROM treatments", conn)

# ---------------- Clean ----------------
# Drop exact duplicate rows, standardize text case, handle missing insurance
for df in [patients, appointments, billing]:
    df.drop_duplicates(inplace=True)

patients["city"] = patients["city"].str.strip().str.title()
patients["has_insurance"] = patients["insurance_id"].notna()
patients["age"] = ((pd.Timestamp.today() - patients["dob"]).dt.days / 365.25).astype(int)

print("=" * 60)
print("DATA OVERVIEW")
print("=" * 60)
print(f"Patients: {len(patients)} | Appointments: {len(appointments)} | Billing records: {len(billing)}")
print(f"Missing insurance: {patients['insurance_id'].isna().sum()} patients ({patients['has_insurance'].mean()*100:.1f}% insured)")

# ---------------- Trend: monthly appointment volume ----------------
appointments["month"] = appointments["appointment_date"].dt.to_period("M").astype(str)
monthly_volume = appointments.groupby("month").size().reset_index(name="num_appointments")
monthly_volume.to_csv(f"{OUT_DIR}/monthly_appointment_volume.csv", index=False)

# ---------------- Trend: monthly revenue ----------------
billing["month"] = billing["billing_date"].dt.to_period("M").astype(str)
monthly_revenue = billing.groupby("month")["amount"].sum().reset_index()
monthly_revenue.to_csv(f"{OUT_DIR}/monthly_revenue.csv", index=False)

print("\n" + "=" * 60)
print("TRENDS")
print("=" * 60)
print(f"Peak appointment month: {monthly_volume.loc[monthly_volume['num_appointments'].idxmax(), 'month']}")
print(f"Peak revenue month: {monthly_revenue.loc[monthly_revenue['amount'].idxmax(), 'month']} "
      f"(EGP {monthly_revenue['amount'].max():,.2f})")

# ---------------- Segmentation: patients by age group & city ----------------
bins = [0, 18, 40, 60, 120]
labels = ["Under 18", "18-39", "40-59", "60+"]
patients["age_group"] = pd.cut(patients["age"], bins=bins, labels=labels, right=False)

age_segmentation = patients["age_group"].value_counts().reset_index()
age_segmentation.columns = ["age_group", "num_patients"]
age_segmentation.to_csv(f"{OUT_DIR}/age_segmentation.csv", index=False)

city_segmentation = patients["city"].value_counts().reset_index()
city_segmentation.columns = ["city", "num_patients"]
city_segmentation.to_csv(f"{OUT_DIR}/city_segmentation.csv", index=False)

# ---------------- Segmentation: revenue by department ----------------
appt_doc = appointments.merge(doctors, on="doctor_id").merge(departments, on="department_id")
appt_billing = appt_doc.merge(billing, on="appointment_id", how="inner")
dept_revenue = appt_billing.groupby("name")["amount"].sum().sort_values(ascending=False).reset_index()
dept_revenue.columns = ["department", "revenue"]
dept_revenue.to_csv(f"{OUT_DIR}/department_revenue.csv", index=False)

print("\n" + "=" * 60)
print("SEGMENTATION")
print("=" * 60)
print("Patients by age group:\n", age_segmentation.to_string(index=False))
print("\nTop department by revenue:", dept_revenue.iloc[0]["department"],
      f"(EGP {dept_revenue.iloc[0]['revenue']:,.2f})")

# ---------------- Prediction: no-show risk ----------------
model_df = appointments.merge(patients[["patient_id", "age", "gender", "has_insurance"]], on="patient_id")
model_df["is_no_show"] = (model_df["status"] == "No-show").astype(int)
model_df["weekday"] = model_df["appointment_date"].dt.dayofweek
model_df["month_num"] = model_df["appointment_date"].dt.month

le_gender = LabelEncoder()
model_df["gender_enc"] = le_gender.fit_transform(model_df["gender"])

features = ["age", "gender_enc", "has_insurance", "weekday", "month_num"]
X = model_df[features]
y = model_df["is_no_show"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
clf = LogisticRegression(max_iter=1000, class_weight="balanced")
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

print("\n" + "=" * 60)
print("PREDICTION: NO-SHOW RISK MODEL (Logistic Regression)")
print("=" * 60)
print(f"Baseline no-show rate: {y.mean()*100:.1f}%")
print(f"Model accuracy: {accuracy_score(y_test, y_pred)*100:.1f}%")
print(classification_report(y_test, y_pred, target_names=["Showed up", "No-show"]))

coef_summary = pd.DataFrame({"feature": features, "coefficient": clf.coef_[0]})
coef_summary = coef_summary.sort_values("coefficient", ascending=False)
coef_summary.to_csv(f"{OUT_DIR}/no_show_model_coefficients.csv", index=False)
print("\nFeature influence on no-show risk (positive = increases risk):")
print(coef_summary.to_string(index=False))

print("\nAll summary CSVs saved to:", OUT_DIR)
conn.close()
