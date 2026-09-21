# ClinicRCM — Full-Stack Web Interface

A real client-server web application for the clinic project: a Flask REST API
backend and a React (Vite + Tailwind) frontend, styled after the Medcare
dashboard reference. This replaces/complements the Streamlit interface with
a proper multi-tier architecture (Backend + Frontend), matching the same
`clinic.db` database used throughout the project.

Chain: **Departments → Doctors → Patients (via Insurance) → Diagnoses → Billing → Lab Tests**

## Folder structure

```
rcm/
  backend/
    app.py           # Flask REST API
    clinic.db         # SQLite database (same schema as the rest of the project)
  frontend/
    src/
      api.js
      App.jsx
      components/     # Sidebar, KpiCard, Badge, DataTable, Modal
      pages/           # Dashboard, Departments, Doctors, Patients, Diagnoses, Payments, LabTests
    package.json
```

## 1. Run the backend

```
cd rcm/backend
pip install flask flask-sqlalchemy flask-cors
python app.py
```

This starts the API at **http://localhost:5000**. Leave this terminal running.

## 2. Run the frontend

Open a **second** terminal:

```
cd rcm/frontend
npm install
npm run dev
```

This starts the app at **http://localhost:5173** — open that in your browser.

## API endpoints (for reference)

| Method | Endpoint | Notes |
|---|---|---|
| GET | `/api/dashboard/summary` | KPIs + chart data |
| GET/POST | `/api/departments` | |
| GET/POST | `/api/doctors` | supports `?search=&specialty=&department_id=` |
| GET/POST | `/api/patients` | supports `?search=&city=` |
| GET/POST | `/api/diagnoses` | supports `?search=&severity=&department_id=` |
| GET/POST | `/api/billing` | supports `?status=&method=` |
| GET/POST | `/api/lab_tests` | supports `?test_type=&result_status=` |
| GET | `/api/insurance_providers` | for dropdowns |

All GET list endpoints support `?page=&per_page=` pagination.

## Notes

- The frontend and backend were both tested end-to-end (including the "Add"
  forms actually writing to the database and the UI refreshing) before this
  was handed over.
- The database is the same `clinic.db` used by the SQL/Python/Excel/Streamlit
  parts of the project — no duplicate data.
- To reset the data, re-run `generate_data.py` from the main project folder
  and copy the resulting `clinic.db` into `rcm/backend/`.
