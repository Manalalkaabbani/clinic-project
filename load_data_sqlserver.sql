USE ClinicDB;

DECLARE @path NVARCHAR(500) = 'D:\clinic_project\data';

-- ---------- 1. Lookup tables (no dependencies) ----------
SET IDENTITY_INSERT departments ON;
BULK INSERT departments FROM 'D:\clinic_project\data\departments.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT departments OFF;

SET IDENTITY_INSERT insurance_providers ON;
BULK INSERT insurance_providers FROM 'D:\clinic_project\data\insurance_providers.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT insurance_providers OFF;

SET IDENTITY_INSERT medications ON;
BULK INSERT medications FROM 'C:\ClinicData\medications.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT medications OFF;

-- ---------- 2. Staff & facilities (depend on departments) ----------
SET IDENTITY_INSERT doctors ON;
BULK INSERT doctors FROM 'C:\ClinicData\doctors.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT doctors OFF;

SET IDENTITY_INSERT nurses ON;
BULK INSERT nurses FROM 'C:\ClinicData\nurses.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT nurses OFF;

SET IDENTITY_INSERT rooms ON;
BULK INSERT rooms FROM 'C:\ClinicData\rooms.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT rooms OFF;

-- ---------- 3. Patients (depend on insurance_providers) ----------
SET IDENTITY_INSERT patients ON;
BULK INSERT patients FROM 'C:\ClinicData\patients.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT patients OFF;

-- ---------- 4. Appointments (depend on patients, doctors, nurses, rooms) ----------
SET IDENTITY_INSERT appointments ON;
BULK INSERT appointments FROM 'C:\ClinicData\appointments.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT appointments OFF;

-- ---------- 5. Everything that depends on appointments ----------
SET IDENTITY_INSERT diagnoses ON;
BULK INSERT diagnoses FROM 'C:\ClinicData\diagnoses.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT diagnoses OFF;

SET IDENTITY_INSERT treatments ON;
BULK INSERT treatments FROM 'C:\ClinicData\treatments.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT treatments OFF;

SET IDENTITY_INSERT lab_tests ON;
BULK INSERT lab_tests FROM 'C:\ClinicData\lab_tests.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT lab_tests OFF;

SET IDENTITY_INSERT billing ON;
BULK INSERT billing FROM 'C:\ClinicData\billing.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT billing OFF;

-- ---------- 6. Prescriptions (depend on diagnoses, medications) ----------
SET IDENTITY_INSERT prescriptions ON;
BULK INSERT prescriptions FROM 'C:\ClinicData\prescriptions.csv'
WITH (FORMAT='CSV', FIRSTROW=2, CODEPAGE='65001', TABLOCK);
SET IDENTITY_INSERT prescriptions OFF;

-- ---------- Sanity check ----------
SELECT 'departments' AS tbl, COUNT(*) AS rows_loaded FROM departments
UNION ALL SELECT 'insurance_providers', COUNT(*) FROM insurance_providers
UNION ALL SELECT 'medications', COUNT(*) FROM medications
UNION ALL SELECT 'doctors', COUNT(*) FROM doctors
UNION ALL SELECT 'nurses', COUNT(*) FROM nurses
UNION ALL SELECT 'rooms', COUNT(*) FROM rooms
UNION ALL SELECT 'patients', COUNT(*) FROM patients
UNION ALL SELECT 'appointments', COUNT(*) FROM appointments
UNION ALL SELECT 'diagnoses', COUNT(*) FROM diagnoses
UNION ALL SELECT 'treatments', COUNT(*) FROM treatments
UNION ALL SELECT 'lab_tests', COUNT(*) FROM lab_tests
UNION ALL SELECT 'billing', COUNT(*) FROM billing
UNION ALL SELECT 'prescriptions', COUNT(*) FROM prescriptions;