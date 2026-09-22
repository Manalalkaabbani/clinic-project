-- ============================================================
-- CLINIC MANAGEMENT DATABASE SCHEMA
-- 13 tables covering operations, clinical, and billing data
-- ============================================================

PRAGMA foreign_keys = ON;

-- ---------- Reference / lookup tables ----------

CREATE TABLE departments (
    department_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    location        TEXT NOT NULL
);

CREATE TABLE insurance_providers (
    insurance_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name   TEXT NOT NULL,
    coverage_type   TEXT NOT NULL,      -- e.g. Basic, Premium, Full
    contact_phone   TEXT
);

CREATE TABLE medications (
    medication_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    category        TEXT NOT NULL,      -- e.g. Antibiotic, Painkiller
    unit_price      DECIMAL(10,2) NOT NULL
);

-- ---------- Staff & facilities ----------

CREATE TABLE doctors (
    doctor_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name          TEXT NOT NULL,
    last_name           TEXT NOT NULL,
    specialty           TEXT NOT NULL,
    department_id       INTEGER NOT NULL,
    years_experience    INTEGER NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE nurses (
    nurse_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    department_id   INTEGER NOT NULL,
    shift           TEXT NOT NULL,      -- Morning / Evening / Night
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE rooms (
    room_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    room_number     TEXT NOT NULL,
    department_id   INTEGER NOT NULL,
    room_type       TEXT NOT NULL,      -- Consultation / Procedure / Lab
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- ---------- Patients ----------

CREATE TABLE patients (
    patient_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name          TEXT NOT NULL,
    last_name            TEXT NOT NULL,
    dob                 DATE NOT NULL,
    gender              TEXT NOT NULL,
    city                TEXT NOT NULL,
    insurance_id        INTEGER,
    registration_date   DATE NOT NULL,
    FOREIGN KEY (insurance_id) REFERENCES insurance_providers(insurance_id)
);

-- ---------- Encounters ----------

CREATE TABLE appointments (
    appointment_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id          INTEGER NOT NULL,
    doctor_id           INTEGER NOT NULL,
    nurse_id            INTEGER,
    room_id             INTEGER,
    appointment_date    DATE NOT NULL,
    status              TEXT NOT NULL,   -- Attended / No-show / Cancelled
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
    FOREIGN KEY (nurse_id) REFERENCES nurses(nurse_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
);

CREATE TABLE diagnoses (
    diagnosis_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id   INTEGER NOT NULL,
    diagnosis_code   TEXT NOT NULL,
    description      TEXT NOT NULL,
    severity         TEXT NOT NULL,     -- Mild / Moderate / Severe
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);

CREATE TABLE treatments (
    treatment_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id    INTEGER NOT NULL,
    procedure_type    TEXT NOT NULL,
    cost              DECIMAL(10,2) NOT NULL,
    duration_minutes  INTEGER NOT NULL,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);

CREATE TABLE lab_tests (
    lab_test_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id   INTEGER NOT NULL,
    test_type        TEXT NOT NULL,
    result_status    TEXT NOT NULL,     -- Normal / Abnormal / Pending
    test_date        DATE NOT NULL,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);

CREATE TABLE prescriptions (
    prescription_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    diagnosis_id      INTEGER NOT NULL,
    medication_id     INTEGER NOT NULL,
    dosage            TEXT NOT NULL,
    duration_days     INTEGER NOT NULL,
    FOREIGN KEY (diagnosis_id) REFERENCES diagnoses(diagnosis_id),
    FOREIGN KEY (medication_id) REFERENCES medications(medication_id)
);

CREATE TABLE billing (
    billing_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id   INTEGER NOT NULL UNIQUE,
    amount           DECIMAL(10,2) NOT NULL,
    payment_status   TEXT NOT NULL,     -- Paid / Pending / Overdue
    payment_method   TEXT NOT NULL,     -- Insurance / Cash / Card
    billing_date     DATE NOT NULL,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);
