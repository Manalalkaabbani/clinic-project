-- ============================================================
-- LOAD CSV DATA INTO SQL SERVER (v2 schema)
-- Run schema_sqlserver.sql FIRST, then this script.
-- Update the file paths below to match where you copied the /data folder.
-- Order matters: departments/insurance_providers first (no dependencies),
-- then doctors, then patients, then diagnoses, then billing/lab_tests.
-- ============================================================

USE ClinicDB;
GO

SET IDENTITY_INSERT departments ON;
BULK INSERT departments FROM 'C:\ClinicData\departments.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT departments OFF;

SET IDENTITY_INSERT insurance_providers ON;
BULK INSERT insurance_providers FROM 'C:\ClinicData\insurance_providers.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT insurance_providers OFF;

SET IDENTITY_INSERT doctors ON;
BULK INSERT doctors FROM 'C:\ClinicData\doctors.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT doctors OFF;

SET IDENTITY_INSERT patients ON;
BULK INSERT patients FROM 'C:\ClinicData\patients.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT patients OFF;

SET IDENTITY_INSERT diagnoses ON;
BULK INSERT diagnoses FROM 'C:\ClinicData\diagnoses.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT diagnoses OFF;

SET IDENTITY_INSERT billing ON;
BULK INSERT billing FROM 'C:\ClinicData\billing.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT billing OFF;

SET IDENTITY_INSERT lab_tests ON;
BULK INSERT lab_tests FROM 'C:\ClinicData\lab_tests.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT lab_tests OFF;

-- Sanity check
SELECT 'departments' AS tbl, COUNT(*) AS rows_loaded FROM departments
UNION ALL SELECT 'insurance_providers', COUNT(*) FROM insurance_providers
UNION ALL SELECT 'doctors', COUNT(*) FROM doctors
UNION ALL SELECT 'patients', COUNT(*) FROM patients
UNION ALL SELECT 'diagnoses', COUNT(*) FROM diagnoses
UNION ALL SELECT 'billing', COUNT(*) FROM billing
UNION ALL SELECT 'lab_tests', COUNT(*) FROM lab_tests;
GO
