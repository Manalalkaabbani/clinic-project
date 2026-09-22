-- 1. Total revenue collected, by payment status
SELECT payment_status, SUM(amount) AS total_amount, COUNT(*) AS num_bills
FROM billing
GROUP BY payment_status
ORDER BY total_amount DESC;

-- 2. Revenue by department (via doctor -> department)
SELECT d.name AS department, ROUND(SUM(b.amount), 2) AS revenue
FROM billing b
JOIN appointments a ON b.appointment_id = a.appointment_id
JOIN doctors doc ON a.doctor_id = doc.doctor_id
JOIN departments d ON doc.department_id = d.department_id
GROUP BY d.name
ORDER BY revenue DESC;

-- 3. No-show rate by department
SELECT d.name AS department,
       ROUND(100.0 * SUM(CASE WHEN a.status = 'No-show' THEN 1 ELSE 0 END) / COUNT(*), 1) AS no_show_rate_pct,
       COUNT(*) AS total_appointments
FROM appointments a
JOIN doctors doc ON a.doctor_id = doc.doctor_id
JOIN departments d ON doc.department_id = d.department_id
GROUP BY d.name
ORDER BY no_show_rate_pct DESC;

-- 4. Top 10 most common diagnoses
SELECT description, COUNT(*) AS occurrences
FROM diagnoses
GROUP BY description
ORDER BY occurrences DESC
LIMIT 10;

-- 5. Average treatment cost by procedure type
SELECT procedure_type, ROUND(AVG(cost), 2) AS avg_cost, COUNT(*) AS num_procedures
FROM treatments
GROUP BY procedure_type
ORDER BY avg_cost DESC;

-- 6. Doctor workload — number of attended appointments per doctor (top 10)
SELECT doc.first_name || ' ' || doc.last_name AS doctor_name, d.name AS department,
       COUNT(*) AS appointments_attended
FROM appointments a
JOIN doctors doc ON a.doctor_id = doc.doctor_id
JOIN departments d ON doc.department_id = d.department_id
WHERE a.status = 'Attended'
GROUP BY doc.doctor_id
ORDER BY appointments_attended DESC
LIMIT 10;

-- 7. Patient segmentation by age group
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

-- 8. Monthly appointment volume trend (last 24 months)
SELECT strftime('%Y-%m', appointment_date) AS month, COUNT(*) AS num_appointments
FROM appointments
GROUP BY month
ORDER BY month;

-- 9. Insurance coverage breakdown of billed amounts
SELECT ip.provider_name, ROUND(SUM(b.amount), 2) AS total_billed, COUNT(*) AS num_visits
FROM billing b
JOIN appointments a ON b.appointment_id = a.appointment_id
JOIN patients p ON a.patient_id = p.patient_id
JOIN insurance_providers ip ON p.insurance_id = ip.insurance_id
GROUP BY ip.provider_name
ORDER BY total_billed DESC;

-- 10. Most prescribed medications
SELECT m.name AS medication, m.category, COUNT(*) AS times_prescribed
FROM prescriptions pr
JOIN medications m ON pr.medication_id = m.medication_id
GROUP BY m.name
ORDER BY times_prescribed DESC
LIMIT 10;

-- 11. Abnormal lab result rate by test type
SELECT test_type,
       ROUND(100.0 * SUM(CASE WHEN result_status = 'Abnormal' THEN 1 ELSE 0 END) / COUNT(*), 1) AS abnormal_rate_pct,
       COUNT(*) AS total_tests
FROM lab_tests
GROUP BY test_type
ORDER BY abnormal_rate_pct DESC;

-- 12. Patients with the highest total spend (top 10)
SELECT p.first_name || ' ' || p.last_name AS patient_name,
       ROUND(SUM(b.amount), 2) AS total_spent,
       COUNT(*) AS num_visits
FROM billing b
JOIN appointments a ON b.appointment_id = a.appointment_id
JOIN patients p ON a.patient_id = p.patient_id
GROUP BY p.patient_id
ORDER BY total_spent DESC
LIMIT 10;

-- 13. Overdue payments — list for follow-up
SELECT p.first_name || ' ' || p.last_name AS patient_name, b.amount, b.billing_date
FROM billing b
JOIN appointments a ON b.appointment_id = a.appointment_id
JOIN patients p ON a.patient_id = p.patient_id
WHERE b.payment_status = 'Overdue'
ORDER BY b.billing_date ASC;
