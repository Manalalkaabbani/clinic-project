-- ============================================================
-- CLINIC DATABASE SCHEMA (v2 — simplified linear design) — SQL Server
-- Chain: Departments -> Doctors -> Patients (via Insurance) ->
--        Diagnoses -> Billing -> Lab Tests (requested services)
-- Run this whole script in SSMS (F5)
-- ============================================================

IF DB_ID('ClinicDB') IS NULL
    CREATE DATABASE ClinicDB;
GO

USE ClinicDB;
GO

CREATE TABLE departments (
    department_id   INT IDENTITY(1,1) PRIMARY KEY,
    name            NVARCHAR(100) NOT NULL,
    location        NVARCHAR(150) NOT NULL
);
GO

CREATE TABLE doctors (
    doctor_id           INT IDENTITY(1,1) PRIMARY KEY,
    first_name          NVARCHAR(50) NOT NULL,
    last_name           NVARCHAR(50) NOT NULL,
    specialty           NVARCHAR(100) NOT NULL,
    department_id       INT NOT NULL,
    years_experience    INT NOT NULL,
    CONSTRAINT FK_doctors_department FOREIGN KEY (department_id) REFERENCES departments(department_id)
);
GO

CREATE TABLE insurance_providers (
    insurance_id    INT IDENTITY(1,1) PRIMARY KEY,
    provider_name   NVARCHAR(100) NOT NULL,
    coverage_type   NVARCHAR(50) NOT NULL,
    contact_phone   NVARCHAR(30) NULL
);
GO

CREATE TABLE patients (
    patient_id          INT IDENTITY(1,1) PRIMARY KEY,
    first_name          NVARCHAR(50) NOT NULL,
    last_name           NVARCHAR(50) NOT NULL,
    dob                 DATE NOT NULL,
    gender              NVARCHAR(10) NOT NULL,
    city                NVARCHAR(50) NOT NULL,
    insurance_id        INT NULL,
    registration_date   DATE NOT NULL,
    CONSTRAINT FK_patients_insurance FOREIGN KEY (insurance_id) REFERENCES insurance_providers(insurance_id)
);
GO

CREATE TABLE diagnoses (
    diagnosis_id     INT IDENTITY(1,1) PRIMARY KEY,
    patient_id       INT NOT NULL,
    doctor_id        INT NOT NULL,
    diagnosis_code   NVARCHAR(20) NOT NULL,
    description      NVARCHAR(200) NOT NULL,
    severity         NVARCHAR(20) NOT NULL,
    diagnosis_date   DATE NOT NULL,
    CONSTRAINT FK_diag_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    CONSTRAINT FK_diag_doctor  FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)
);
GO

CREATE TABLE billing (
    billing_id       INT IDENTITY(1,1) PRIMARY KEY,
    diagnosis_id     INT NOT NULL UNIQUE,
    amount           DECIMAL(10,2) NOT NULL,
    payment_status   NVARCHAR(20) NOT NULL,
    payment_method   NVARCHAR(20) NOT NULL,
    billing_date     DATE NOT NULL,
    CONSTRAINT FK_billing_diag FOREIGN KEY (diagnosis_id) REFERENCES diagnoses(diagnosis_id)
);
GO

CREATE TABLE lab_tests (
    lab_test_id      INT IDENTITY(1,1) PRIMARY KEY,
    diagnosis_id     INT NOT NULL,
    test_type        NVARCHAR(100) NOT NULL,
    result_status    NVARCHAR(20) NOT NULL,
    test_date        DATE NOT NULL,
    CONSTRAINT FK_lab_diag FOREIGN KEY (diagnosis_id) REFERENCES diagnoses(diagnosis_id)
);
GO
