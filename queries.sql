-- ============================================================
-- CLINIC DATABASE (v2) — BUSINESS QUESTION QUERIES
-- ============================================================

-- 1. Total revenue collected, by payment status
SELECT payment_status, SUM(amount) AS total_amount, COUNT(*) AS num_bills
FROM billing
GROUP BY payment_status
ORDER BY total_amount DESC;

-- 2. Revenue by department (via doctor -> department)
SELECT d.name AS department, ROUND(SUM(b.amount), 2) AS revenue
FROM billing b
JOIN diagnoses dg ON b.diagnosis_id = dg.diagnosis_id
JOIN doctors doc ON dg.doctor_id = doc.doctor_id
JOIN departments d ON doc.department_id = d.department_id
GROUP BY d.name
ORDER BY revenue DESC;

-- 3. Doctor workload — number of diagnoses per doctor (top 10)
SELECT doc.first_name || ' ' || doc.last_name AS doctor_name, d.name AS department,
       COUNT(*) AS num_diagnoses
FROM diagnoses dg
JOIN doctors doc ON dg.doctor_id = doc.doctor_id
JOIN departments d ON doc.department_id = d.department_id
GROUP BY doc.doctor_id
ORDER BY num_diagnoses DESC
LIMIT 10;

-- 4. Top 10 most common diagnoses
SELECT description, COUNT(*) AS occurrences
FROM diagnoses
GROUP BY description
ORDER BY occurrences DESC
LIMIT 10;

-- 5. Diagnosis severity breakdown
SELECT severity, COUNT(*) AS num_cases,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM diagnoses), 1) AS pct_of_total
FROM diagnoses
GROUP BY severity
ORDER BY num_cases DESC;

-- 6. Patient segmentation by age group
SELECT
  CASE
    WHEN (julianday('now') - julianday(dob)) / 365.25 < 18 THEN 'Under 18'
    WHEN (julianday('now') - julianday(dob)) / 365.25 < 40 THEN '18-39'
    WHEN (julianday('now') - julianday(dob)) / 365.25 < 60 THEN '40-59'
    ELSE '60+'
  END AS age_group,
  COUNT(*) AS num_patients
FROM patients
GROUP BY age_group
ORDER BY num_patients DESC;

-- 7. Monthly diagnosis volume trend (last 24 months)
SELECT strftime('%Y-%m', diagnosis_date) AS month, COUNT(*) AS num_diagnoses
FROM diagnoses
GROUP BY month
ORDER BY month;

-- 8. Insurance coverage breakdown of billed amounts
SELECT ip.provider_name, ROUND(SUM(b.amount), 2) AS total_billed, COUNT(*) AS num_visits
FROM billing b
JOIN diagnoses dg ON b.diagnosis_id = dg.diagnosis_id
JOIN patients p ON dg.patient_id = p.patient_id
JOIN insurance_providers ip ON p.insurance_id = ip.insurance_id
GROUP BY ip.provider_name
ORDER BY total_billed DESC;

-- 9. Requested lab tests — abnormal result rate by test type
SELECT test_type,
       ROUND(100.0 * SUM(CASE WHEN result_status = 'Abnormal' THEN 1 ELSE 0 END) / COUNT(*), 1) AS abnormal_rate_pct,
       COUNT(*) AS total_tests
FROM lab_tests
GROUP BY test_type
ORDER BY abnormal_rate_pct DESC;

-- 10. Patients with the highest total spend (top 10)
SELECT p.first_name || ' ' || p.last_name AS patient_name,
       ROUND(SUM(b.amount), 2) AS total_spent,
       COUNT(*) AS num_diagnoses
FROM billing b
JOIN diagnoses dg ON b.diagnosis_id = dg.diagnosis_id
JOIN patients p ON dg.patient_id = p.patient_id
GROUP BY p.patient_id
ORDER BY total_spent DESC
LIMIT 10;

-- 11. Overdue payments — list for follow-up
SELECT p.first_name || ' ' || p.last_name AS patient_name, b.amount, b.billing_date
FROM billing b
JOIN diagnoses dg ON b.diagnosis_id = dg.diagnosis_id
JOIN patients p ON dg.patient_id = p.patient_id
WHERE b.payment_status = 'Overdue'
ORDER BY b.billing_date ASC;

-- 12. Diagnoses that had no lab tests requested (potential follow-up gap)
SELECT COUNT(*) AS diagnoses_without_lab_tests
FROM diagnoses dg
WHERE NOT EXISTS (SELECT 1 FROM lab_tests lt WHERE lt.diagnosis_id = dg.diagnosis_id);

-- 13. Average bill amount by diagnosis severity
SELECT dg.severity, ROUND(AVG(b.amount), 2) AS avg_bill_amount, COUNT(*) AS num_bills
FROM billing b
JOIN diagnoses dg ON b.diagnosis_id = dg.diagnosis_id
GROUP BY dg.severity
ORDER BY avg_bill_amount DESC;
