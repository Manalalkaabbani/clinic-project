import sqlite3
import random
from datetime import date, timedelta
from faker import Faker
import pandas as pd
import os

random.seed(42)
fake = Faker()
Faker.seed(42)

# All paths are relative to this script's own folder, so it works
# no matter where the clinic_project folder lives on your machine.
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
N_APPOINTMENTS = 20000

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

MED_CATEGORIES = {
    "Amoxicillin": "Antibiotic", "Azithromycin": "Antibiotic",
    "Ibuprofen": "Painkiller", "Paracetamol": "Painkiller",
    "Metformin": "Chronic - Diabetes", "Atorvastatin": "Chronic - Cholesterol",
    "Amlodipine": "Chronic - Hypertension", "Cetirizine": "Antihistamine",
    "Omeprazole": "Gastro", "Salbutamol": "Respiratory",
}

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

TREATMENT_POOL = [
    ("Consultation", 150, 20), ("Follow-up visit", 80, 15),
    ("Physiotherapy session", 200, 45), ("Minor procedure", 500, 40),
    ("Vaccination", 100, 10), ("Dental cleaning", 250, 30),
    ("X-Ray", 300, 15), ("Blood test panel", 180, 10),
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

# ---------------- Medications ----------------
for med, cat in MED_CATEGORIES.items():
    cur.execute("INSERT INTO medications (name, category, unit_price) VALUES (?,?,?)",
                (med, cat, round(random.uniform(15, 300), 2)))
conn.commit()
medication_ids = [row[0] for row in cur.execute("SELECT medication_id FROM medications")]

# ---------------- Doctors ----------------
N_DOCTORS = 80
for _ in range(N_DOCTORS):
    dept_name = random.choice(list(dept_ids.keys()))
    cur.execute("""INSERT INTO doctors (first_name, last_name, specialty, department_id, years_experience)
                   VALUES (?,?,?,?,?)""",
                (fake.first_name(), fake.last_name(), SPECIALTIES[dept_name],
                 dept_ids[dept_name], random.randint(1, 30)))
conn.commit()
doctor_rows = list(cur.execute("SELECT doctor_id, department_id FROM doctors"))

# ---------------- Nurses ----------------
N_NURSES = 50
for _ in range(N_NURSES):
    dept_name = random.choice(list(dept_ids.keys()))
    cur.execute("""INSERT INTO nurses (first_name, last_name, department_id, shift)
                   VALUES (?,?,?,?)""",
                (fake.first_name(), fake.last_name(), dept_ids[dept_name],
                 random.choice(["Morning", "Evening", "Night"])))
conn.commit()
nurse_ids_by_dept = {}
for nid, did in cur.execute("SELECT nurse_id, department_id FROM nurses"):
    nurse_ids_by_dept.setdefault(did, []).append(nid)

# ---------------- Rooms ----------------
for name, did in dept_ids.items():
    for i in range(1, 5):
        cur.execute("""INSERT INTO rooms (room_number, department_id, room_type) VALUES (?,?,?)""",
                    (f"{name[:3].upper()}-{i}", did, random.choice(["Consultation", "Procedure", "Lab"])))
conn.commit()
room_ids_by_dept = {}
for rid, did in cur.execute("SELECT room_id, department_id FROM rooms"):
    room_ids_by_dept.setdefault(did, []).append(rid)

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

# ---------------- Appointments (+ diagnoses, treatments, lab tests, billing, prescriptions) ----------------
status_weights = [("Attended", 0.75), ("No-show", 0.15), ("Cancelled", 0.10)]

for _ in range(N_APPOINTMENTS):
    doctor_id, dept_id = random.choice(doctor_rows)
    patient_id = random.choice(patient_ids)
    nurse_id = random.choice(nurse_ids_by_dept.get(dept_id, [None]))
    room_id = random.choice(room_ids_by_dept.get(dept_id, [None]))
    appt_date = fake.date_between(start_date="-2y", end_date="today")
    status = random.choices([s[0] for s in status_weights], weights=[s[1] for s in status_weights])[0]

    cur.execute("""INSERT INTO appointments
        (patient_id, doctor_id, nurse_id, room_id, appointment_date, status)
        VALUES (?,?,?,?,?,?)""",
        (patient_id, doctor_id, nurse_id, room_id, appt_date.isoformat(), status))
    appointment_id = cur.lastrowid

    if status == "Attended":
        # 1-2 diagnoses
        for _ in range(random.randint(1, 2)):
            code, desc, sev = random.choice(DIAGNOSIS_POOL)
            cur.execute("""INSERT INTO diagnoses (appointment_id, diagnosis_code, description, severity)
                           VALUES (?,?,?,?)""", (appointment_id, code, desc, sev))
            diagnosis_id = cur.lastrowid

            # prescriptions ~70% chance per diagnosis
            if random.random() < 0.7:
                med_id = random.choice(medication_ids)
                cur.execute("""INSERT INTO prescriptions (diagnosis_id, medication_id, dosage, duration_days)
                               VALUES (?,?,?,?)""",
                            (diagnosis_id, med_id, random.choice(["1 tablet/day", "2 tablets/day", "1 tablet twice/day"]),
                             random.choice([5, 7, 10, 14, 30])))

        # 1 treatment
        proc, base_cost, dur = random.choice(TREATMENT_POOL)
        cost = round(base_cost * random.uniform(0.85, 1.25), 2)
        cur.execute("""INSERT INTO treatments (appointment_id, procedure_type, cost, duration_minutes)
                       VALUES (?,?,?,?)""", (appointment_id, proc, cost, dur))

        # lab test ~40% chance
        if random.random() < 0.4:
            test_type = random.choice(["Blood Panel", "X-Ray", "MRI", "Urine Test", "ECG"])
            result = random.choices(["Normal", "Abnormal", "Pending"], weights=[0.7, 0.25, 0.05])[0]
            cur.execute("""INSERT INTO lab_tests (appointment_id, test_type, result_status, test_date)
                           VALUES (?,?,?,?)""", (appointment_id, test_type, result, appt_date.isoformat()))

        # billing
        amount = round(cost + random.uniform(-20, 80), 2)
        pay_status = random.choices(["Paid", "Pending", "Overdue"], weights=[0.75, 0.15, 0.10])[0]
        pay_method = random.choice(["Insurance", "Cash", "Card"])
        cur.execute("""INSERT INTO billing (appointment_id, amount, payment_status, payment_method, billing_date)
                       VALUES (?,?,?,?,?)""",
                    (appointment_id, amount, pay_status, pay_method, appt_date.isoformat()))

conn.commit()

# ---------------- Export all tables to CSV ----------------
tables = ["departments", "insurance_providers", "medications", "doctors", "nurses",
          "rooms", "patients", "appointments", "diagnoses", "treatments",
          "lab_tests", "prescriptions", "billing"]

for t in tables:
    df = pd.read_sql_query(f"SELECT * FROM {t}", conn)
    df.to_csv(f"{OUT_DIR}/{t}.csv", index=False)
    print(f"{t}: {len(df)} rows")

conn.close()
print("\nDatabase built at:", DB_PATH)
