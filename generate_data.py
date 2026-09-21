"""
generate_data.py (v2 — simplified schema)
Chain: Departments -> Doctors -> Patients (via Insurance) ->
       Diagnoses -> Billing -> Lab Tests (requested services)
"""

import sqlite3
import random
from faker import Faker
import pandas as pd
import os

random.seed(42)
fake = Faker()
Faker.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(OUT_DIR, exist_ok=True)

DB_PATH = os.path.join(BASE_DIR, "clinic.db")
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
with open(os.path.join(BASE_DIR, "schema.sql"), "r") as f:
    cur.executescript(f.read())
conn.commit()

# ---------------- Config ----------------
N_PATIENTS = 5000
N_DOCTORS = 80

DEPARTMENTS = [
    ("Cardiology", "Building A - Floor 1"),
    ("Dermatology", "Building A - Floor 2"),
    ("Orthopedics", "Building B - Floor 1"),
    ("Pediatrics", "Building B - Floor 2"),
    ("General Medicine", "Building A - Floor 1"),
    ("Physiotherapy", "Building C - Floor 1"),
    ("ENT", "Building C - Floor 2"),
    ("Dentistry", "Building D - Floor 1"),
]

SPECIALTIES = {
    "Cardiology": "Cardiologist", "Dermatology": "Dermatologist",
    "Orthopedics": "Orthopedic Surgeon", "Pediatrics": "Pediatrician",
    "General Medicine": "General Practitioner", "Physiotherapy": "Physiotherapist",
    "ENT": "ENT Specialist", "Dentistry": "Dentist",
}

INSURANCE_PROVIDERS = [
    ("Misr Health Insurance", "Full"), ("Allianz Egypt", "Premium"),
    ("AXA Egypt", "Premium"), ("Bupa Global", "Full"),
    ("National Social Insurance", "Basic"),
]

DIAGNOSIS_POOL = [
    ("J06.9", "Upper respiratory infection", "Mild"),
    ("I10", "Hypertension", "Moderate"),
    ("E11.9", "Type 2 Diabetes", "Moderate"),
    ("M54.5", "Lower back pain", "Mild"),
    ("L20.9", "Atopic dermatitis", "Mild"),
    ("J45.9", "Asthma", "Moderate"),
    ("K21.0", "GERD", "Mild"),
    ("S93.4", "Ankle sprain", "Moderate"),
    ("R51", "Headache", "Mild"),
    ("I25.1", "Coronary artery disease", "Severe"),
    ("N39.0", "Urinary tract infection", "Mild"),
    ("J03.9", "Tonsillitis", "Mild"),
]

CITIES = ["Cairo", "Giza", "Alexandria", "Mansoura", "Tanta", "Aswan", "Luxor", "Ismailia"]

# ---------------- Departments ----------------
for name, loc in DEPARTMENTS:
    cur.execute("INSERT INTO departments (name, location) VALUES (?,?)", (name, loc))
conn.commit()
dept_ids = {row[1]: row[0] for row in cur.execute("SELECT department_id, name FROM departments")}

# ---------------- Insurance providers ----------------
for name, cov in INSURANCE_PROVIDERS:
    cur.execute("INSERT INTO insurance_providers (provider_name, coverage_type, contact_phone) VALUES (?,?,?)",
                (name, cov, fake.phone_number()))
conn.commit()
insurance_ids = [row[0] for row in cur.execute("SELECT insurance_id FROM insurance_providers")]

# ---------------- Doctors ----------------
for _ in range(N_DOCTORS):
    dept_name = random.choice(list(dept_ids.keys()))
    cur.execute("""INSERT INTO doctors (first_name, last_name, specialty, department_id, years_experience)
                   VALUES (?,?,?,?,?)""",
                (fake.first_name(), fake.last_name(), SPECIALTIES[dept_name],
                 dept_ids[dept_name], random.randint(1, 30)))
conn.commit()
doctor_ids = [row[0] for row in cur.execute("SELECT doctor_id FROM doctors")]

# ---------------- Patients ----------------
for _ in range(N_PATIENTS):
    dob = fake.date_of_birth(minimum_age=1, maximum_age=90)
    reg_date = fake.date_between(start_date="-3y", end_date="today")
    has_insurance = random.random() < 0.7
    cur.execute("""INSERT INTO patients
        (first_name, last_name, dob, gender, city, insurance_id, registration_date)
        VALUES (?,?,?,?,?,?,?)""",
        (fake.first_name(), fake.last_name(), dob.isoformat(),
         random.choice(["Male", "Female"]), random.choice(CITIES),
         random.choice(insurance_ids) if has_insurance else None,
         reg_date.isoformat()))
conn.commit()
patient_ids = [row[0] for row in cur.execute("SELECT patient_id FROM patients")]

# ---------------- Diagnoses (+ billing + lab tests) ----------------
N_DIAGNOSES = 20000

for _ in range(N_DIAGNOSES):
    patient_id = random.choice(patient_ids)
    doctor_id = random.choice(doctor_ids)
    code, desc, sev = random.choice(DIAGNOSIS_POOL)
    diag_date = fake.date_between(start_date="-2y", end_date="today")

    cur.execute("""INSERT INTO diagnoses (patient_id, doctor_id, diagnosis_code, description, severity, diagnosis_date)
                   VALUES (?,?,?,?,?,?)""",
                (patient_id, doctor_id, code, desc, sev, diag_date.isoformat()))
    diagnosis_id = cur.lastrowid

    # Billing — generated for ~90% of diagnoses (some still awaiting billing)
    if random.random() < 0.9:
        amount = round(random.uniform(80, 900), 2)
        pay_status = random.choices(["Paid", "Pending", "Overdue"], weights=[0.75, 0.15, 0.10])[0]
        pay_method = random.choice(["Insurance", "Cash", "Card"])
        cur.execute("""INSERT INTO billing (diagnosis_id, amount, payment_status, payment_method, billing_date)
                       VALUES (?,?,?,?,?)""",
                    (diagnosis_id, amount, pay_status, pay_method, diag_date.isoformat()))

    # Lab tests requested — ~40% chance, 1-2 tests
    if random.random() < 0.4:
        for _ in range(random.randint(1, 2)):
            test_type = random.choice(["Blood Panel", "X-Ray", "MRI", "Urine Test", "ECG"])
            result = random.choices(["Normal", "Abnormal", "Pending"], weights=[0.7, 0.25, 0.05])[0]
            cur.execute("""INSERT INTO lab_tests (diagnosis_id, test_type, result_status, test_date)
                           VALUES (?,?,?,?)""", (diagnosis_id, test_type, result, diag_date.isoformat()))

conn.commit()

# ---------------- Export all tables to CSV ----------------
tables = ["departments", "insurance_providers", "doctors", "patients",
          "diagnoses", "billing", "lab_tests"]

for t in tables:
    df = pd.read_sql_query(f"SELECT * FROM {t}", conn)
    df.to_csv(f"{OUT_DIR}/{t}.csv", index=False)
    print(f"{t}: {len(df)} rows")

conn.close()
print("\nDatabase built at:", DB_PATH)
