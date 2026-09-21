-- ============================================================
-- CLINIC DATABASE SCHEMA (v2 — simplified linear design)
-- Chain: Departments -> Doctors -> Patients (via Insurance) ->
--        Diagnoses -> Billing -> Lab Tests (requested services)
-- ============================================================

PRAGMA foreign_keys = ON;

CREATE TABLE departments (
    department_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    location        TEXT NOT NULL
);

CREATE TABLE doctors (
    doctor_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name          TEXT NOT NULL,
    last_name           TEXT NOT NULL,
    specialty           TEXT NOT NULL,
    department_id       INTEGER NOT NULL,
    years_experience    INTEGER NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE insurance_providers (
    insurance_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_name   TEXT NOT NULL,
    coverage_type   TEXT NOT NULL,      -- Basic, Premium, Full
    contact_phone   TEXT
);

CREATE TABLE patients (
    patient_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name          TEXT NOT NULL,
    last_name           TEXT NOT NULL,
    dob                 DATE NOT NULL,
    gender              TEXT NOT NULL,
    city                TEXT NOT NULL,
    insurance_id        INTEGER,
    registration_date   DATE NOT NULL,
    FOREIGN KEY (insurance_id) REFERENCES insurance_providers(insurance_id)
);

CREATE TABLE diagnoses (
    diagnosis_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id       INTEGER NOT NULL,
    doctor_id        INTEGER NOT NULL,
    diagnosis_code   TEXT NOT NULL,
    description      TEXT NOT NULL,
    severity         TEXT NOT NULL,      -- Mild / Moderate / Severe
    diagnosis_date   DATE NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

CREATE TABLE billing (
    billing_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    diagnosis_id     INTEGER NOT NULL UNIQUE,
    amount           DECIMAL(10,2) NOT NULL,
    payment_status   TEXT NOT NULL,     -- Paid / Pending / Overdue
    payment_method   TEXT NOT NULL,     -- Insurance / Cash / Card
    billing_date     DATE NOT NULL,
    FOREIGN KEY (diagnosis_id) REFERENCES diagnoses(diagnosis_id)
);

CREATE TABLE lab_tests (
    lab_test_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    diagnosis_id     INTEGER NOT NULL,
    test_type        TEXT NOT NULL,
    result_status    TEXT NOT NULL,     -- Normal / Abnormal / Pending
    test_date        DATE NOT NULL,
    FOREIGN KEY (diagnosis_id) REFERENCES diagnoses(diagnosis_id)
);
