    CREATE DATABASE ClinicDB;

USE ClinicDB;

-- ---------- Reference / lookup tables ----------

CREATE TABLE departments (
    department_id   INT IDENTITY(1,1) PRIMARY KEY,
    name            NVARCHAR(100) NOT NULL,
    location        NVARCHAR(150) NOT NULL
);

CREATE TABLE insurance_providers (
    insurance_id    INT IDENTITY(1,1) PRIMARY KEY,
    provider_name   NVARCHAR(100) NOT NULL,
    coverage_type   NVARCHAR(50) NOT NULL,      -- Basic, Premium, Full
    contact_phone   NVARCHAR(30) NULL
);

CREATE TABLE medications (
    medication_id   INT IDENTITY(1,1) PRIMARY KEY,
    name            NVARCHAR(100) NOT NULL,
    category        NVARCHAR(100) NOT NULL,
    unit_price      DECIMAL(10,2) NOT NULL
);

-- ---------- Staff & facilities ----------

CREATE TABLE doctors (
    doctor_id           INT IDENTITY(1,1) PRIMARY KEY,
    first_name          NVARCHAR(50) NOT NULL,
    last_name           NVARCHAR(50) NOT NULL,
    specialty           NVARCHAR(100) NOT NULL,
    department_id       INT NOT NULL,
    years_experience    INT NOT NULL,
    CONSTRAINT FK_doctors_department FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
);

CREATE TABLE nurses (
    nurse_id        INT IDENTITY(1,1) PRIMARY KEY,
    first_name      NVARCHAR(50) NOT NULL,
    last_name       NVARCHAR(50) NOT NULL,
    department_id   INT NOT NULL,
    shift           NVARCHAR(20) NOT NULL,      -- Morning / Evening / Night
    CONSTRAINT FK_nurses_department FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
);

CREATE TABLE rooms (
    room_id         INT IDENTITY(1,1) PRIMARY KEY,
    room_number     NVARCHAR(20) NOT NULL,
    department_id   INT NOT NULL,
    room_type       NVARCHAR(30) NOT NULL,      -- Consultation / Procedure / Lab
    CONSTRAINT FK_rooms_department FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
);

-- ---------- Patients ----------

CREATE TABLE patients (
    patient_id          INT IDENTITY(1,1) PRIMARY KEY,
    first_name          NVARCHAR(50) NOT NULL,
    last_name           NVARCHAR(50) NOT NULL,
    dob                 DATE NOT NULL,
    gender              NVARCHAR(10) NOT NULL,
    city                NVARCHAR(50) NOT NULL,
    insurance_id        INT NULL,
    registration_date   DATE NOT NULL,
    CONSTRAINT FK_patients_insurance FOREIGN KEY (insurance_id)
        REFERENCES insurance_providers(insurance_id)
);

-- ---------- Encounters ----------

CREATE TABLE appointments (
    appointment_id      INT IDENTITY(1,1) PRIMARY KEY,
    patient_id          INT NOT NULL,
    doctor_id           INT NOT NULL,
    nurse_id            INT NULL,
    room_id             INT NULL,
    appointment_date    DATE NOT NULL,
    status              NVARCHAR(20) NOT NULL,   -- Attended / No-show / Cancelled
    CONSTRAINT FK_appt_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    CONSTRAINT FK_appt_doctor  FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id),
    CONSTRAINT FK_appt_nurse   FOREIGN KEY (nurse_id)   REFERENCES nurses(nurse_id),
    CONSTRAINT FK_appt_room    FOREIGN KEY (room_id)    REFERENCES rooms(room_id)
);

CREATE TABLE diagnoses (
    diagnosis_id     INT IDENTITY(1,1) PRIMARY KEY,
    appointment_id   INT NOT NULL,
    diagnosis_code   NVARCHAR(20) NOT NULL,
    description      NVARCHAR(200) NOT NULL,
    severity         NVARCHAR(20) NOT NULL,     -- Mild / Moderate / Severe
    CONSTRAINT FK_diag_appt FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);

CREATE TABLE treatments (
    treatment_id      INT IDENTITY(1,1) PRIMARY KEY,
    appointment_id    INT NOT NULL,
    procedure_type    NVARCHAR(100) NOT NULL,
    cost              DECIMAL(10,2) NOT NULL,
    duration_minutes  INT NOT NULL,
    CONSTRAINT FK_treat_appt FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);

CREATE TABLE lab_tests (
    lab_test_id      INT IDENTITY(1,1) PRIMARY KEY,
    appointment_id   INT NOT NULL,
    test_type        NVARCHAR(100) NOT NULL,
    result_status    NVARCHAR(20) NOT NULL,     -- Normal / Abnormal / Pending
    test_date        DATE NOT NULL,
    CONSTRAINT FK_lab_appt FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);

CREATE TABLE prescriptions (
    prescription_id   INT IDENTITY(1,1) PRIMARY KEY,
    diagnosis_id      INT NOT NULL,
    medication_id     INT NOT NULL,
    dosage            NVARCHAR(50) NOT NULL,
    duration_days     INT NOT NULL,
    CONSTRAINT FK_presc_diag FOREIGN KEY (diagnosis_id) REFERENCES diagnoses(diagnosis_id),
    CONSTRAINT FK_presc_med  FOREIGN KEY (medication_id) REFERENCES medications(medication_id)
);

CREATE TABLE billing (
    billing_id       INT IDENTITY(1,1) PRIMARY KEY,
    appointment_id   INT NOT NULL UNIQUE,
    amount           DECIMAL(10,2) NOT NULL,
    payment_status   NVARCHAR(20) NOT NULL,     -- Paid / Pending / Overdue
    payment_method   NVARCHAR(20) NOT NULL,     -- Insurance / Cash / Card
    billing_date     DATE NOT NULL,
    CONSTRAINT FK_billing_appt FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id)
);
