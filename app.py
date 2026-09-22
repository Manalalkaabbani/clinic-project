import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "clinic.db")

st.set_page_config(page_title="Clinic Management System", layout="wide", page_icon="🏥")

TABLES = ["patients", "doctors", "nurses", "departments", "rooms", "insurance_providers",
          "medications", "appointments", "diagnoses", "treatments", "lab_tests",
          "prescriptions", "billing"]


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


@st.cache_data(ttl=5)
def load_table(table_name):
    conn = get_conn()
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df


@st.cache_data(ttl=5)
def run_query(sql):
    conn = get_conn()
    df = pd.read_sql_query(sql, conn)
    conn.close()
    return df


if not os.path.exists(DB_PATH):
    st.error(
        "clinic.db not found next to app.py. Run `python generate_data.py` first "
        "to build the database, then reload this page."
    )
    st.stop()

st.sidebar.title("🏥 Clinic Management System")
page = st.sidebar.radio("Navigate", ["📊 Dashboard", "🔍 Explore Data", "➕ Add Data", "🧮 Run SQL Query"])

# ============================================================
# DASHBOARD
# ============================================================
if page == "📊 Dashboard":
    st.title("📊 Clinic Operations Dashboard")

    patients = load_table("patients")
    appointments = load_table("appointments")
    billing = load_table("billing")
    doctors = load_table("doctors")
    departments = load_table("departments")

    # ---- Department filter ----
    dept_options = ["All departments"] + sorted(departments["name"].tolist())
    selected_dept = st.selectbox("Filter by department", dept_options)

    appt_doc = appointments.merge(doctors, on="doctor_id").merge(departments, on="department_id")
    if selected_dept != "All departments":
        appt_doc = appt_doc[appt_doc["name"] == selected_dept]

    filtered_appt_ids = set(appt_doc["appointment_id"])
    filtered_billing = billing[billing["appointment_id"].isin(filtered_appt_ids)]

    # ---- KPI row ----
    total_revenue = filtered_billing["amount"].sum()
    total_appointments = len(appt_doc)
    no_show_rate = (appt_doc["status"] == "No-show").mean() * 100 if len(appt_doc) else 0
    total_patients = patients["patient_id"].nunique() if selected_dept == "All departments" else appt_doc["patient_id"].nunique()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"EGP {total_revenue:,.0f}")
    c2.metric("Appointments", f"{total_appointments:,}")
    c3.metric("No-show Rate", f"{no_show_rate:.1f}%")
    c4.metric("Patients Involved", f"{total_patients:,}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly Revenue Trend")
        billing_m = filtered_billing.copy()
        billing_m["month"] = pd.to_datetime(billing_m["billing_date"]).dt.to_period("M").astype(str)
        monthly_rev = billing_m.groupby("month")["amount"].sum().reset_index()
        st.line_chart(monthly_rev, x="month", y="amount")

    with col2:
        st.subheader("Appointment Status Breakdown")
        status_counts = appt_doc["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        import plotly.express as px
        fig = px.pie(status_counts, names="status", values="count", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Revenue by Department")
        dept_rev = appointments.merge(doctors, on="doctor_id").merge(departments, on="department_id") \
            .merge(billing, on="appointment_id")
        dept_rev = dept_rev.groupby("name")["amount"].sum().sort_values(ascending=False).reset_index()
        st.bar_chart(dept_rev, x="name", y="amount")

    with col4:
        st.subheader("Patients by Age Group")
        p = patients.copy()
        p["dob"] = pd.to_datetime(p["dob"])
        p["age"] = ((pd.Timestamp.today() - p["dob"]).dt.days / 365.25).astype(int)
        bins = [0, 18, 40, 60, 120]
        labels = ["Under 18", "18-39", "40-59", "60+"]
        p["age_group"] = pd.cut(p["age"], bins=bins, labels=labels, right=False)
        age_counts = p["age_group"].value_counts().reindex(labels).reset_index()
        age_counts.columns = ["age_group", "count"]
        st.bar_chart(age_counts, x="age_group", y="count")

# ============================================================
# EXPLORE DATA
# ============================================================
elif page == "🔍 Explore Data":
    st.title("🔍 Explore Data")

    table = st.selectbox("Choose a table", TABLES)
    df = load_table(table)

    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("Search (matches any column)")
    with col2:
        st.write("")
        st.write(f"**{len(df):,} total rows**")

    if search:
        mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False, na=False).any(), axis=1)
        df_display = df[mask]
    else:
        df_display = df

    # Optional column filter
    with st.expander("Advanced filter"):
        col = st.selectbox("Column", ["(none)"] + list(df.columns))
        if col != "(none)":
            unique_vals = df[col].dropna().unique().tolist()
            if len(unique_vals) <= 50:
                chosen = st.multiselect(f"Filter {col}", sorted(unique_vals, key=str))
                if chosen:
                    df_display = df_display[df_display[col].isin(chosen)]
            else:
                st.caption("Too many unique values to filter as a list — use the search box instead.")

    st.dataframe(df_display, use_container_width=True, height=500)
    st.caption(f"Showing {len(df_display):,} of {len(df):,} rows")

    csv = df_display.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered data as CSV", csv, f"{table}_filtered.csv", "text/csv")

# ============================================================
# ADD DATA
# ============================================================
elif page == "➕ Add Data":
    st.title("➕ Add Data")

    entity = st.selectbox("What do you want to add?", ["Patient", "Appointment", "Doctor", "Diagnosis", "Billing entry"])

    if entity == "Patient":
        insurance_df = load_table("insurance_providers")
        with st.form("add_patient"):
            c1, c2 = st.columns(2)
            first = c1.text_input("First name")
            last = c2.text_input("Last name")
            dob = c1.date_input("Date of birth", min_value=date(1920, 1, 1), max_value=date.today())
            gender = c2.selectbox("Gender", ["Male", "Female"])
            city = c1.text_input("City")
            insurance_choice = c2.selectbox("Insurance provider", ["None"] + insurance_df["provider_name"].tolist())
            submitted = st.form_submit_button("Add patient")
            if submitted:
                if not first or not last:
                    st.warning("First and last name are required.")
                else:
                    insurance_id = None
                    if insurance_choice != "None":
                        insurance_id = int(insurance_df.loc[insurance_df.provider_name == insurance_choice, "insurance_id"].iloc[0])
                    conn = get_conn()
                    conn.execute(
                        "INSERT INTO patients (first_name,last_name,dob,gender,city,insurance_id,registration_date) VALUES (?,?,?,?,?,?,?)",
                        (first, last, dob.isoformat(), gender, city, insurance_id, date.today().isoformat()),
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"Added patient {first} {last}.")
                    st.cache_data.clear()

    elif entity == "Appointment":
        patients_df = load_table("patients")
        doctors_df = load_table("doctors")
        nurses_df = load_table("nurses")
        rooms_df = load_table("rooms")
        with st.form("add_appointment"):
            patient_choice = st.selectbox(
                "Patient", patients_df.apply(lambda r: f"{r.patient_id} - {r.first_name} {r.last_name}", axis=1)
            )
            doctor_choice = st.selectbox(
                "Doctor", doctors_df.apply(lambda r: f"{r.doctor_id} - Dr. {r.first_name} {r.last_name} ({r.specialty})", axis=1)
            )
            nurse_choice = st.selectbox(
                "Nurse (optional)", ["None"] + nurses_df.apply(lambda r: f"{r.nurse_id} - {r.first_name} {r.last_name}", axis=1).tolist()
            )
            room_choice = st.selectbox("Room (optional)", ["None"] + rooms_df.apply(lambda r: f"{r.room_id} - {r.room_number}", axis=1).tolist())
            appt_date = st.date_input("Appointment date", value=date.today())
            status = st.selectbox("Status", ["Attended", "No-show", "Cancelled"])
            submitted = st.form_submit_button("Add appointment")
            if submitted:
                patient_id = int(patient_choice.split(" - ")[0])
                doctor_id = int(doctor_choice.split(" - ")[0])
                nurse_id = int(nurse_choice.split(" - ")[0]) if nurse_choice != "None" else None
                room_id = int(room_choice.split(" - ")[0]) if room_choice != "None" else None
                conn = get_conn()
                conn.execute(
                    "INSERT INTO appointments (patient_id,doctor_id,nurse_id,room_id,appointment_date,status) VALUES (?,?,?,?,?,?)",
                    (patient_id, doctor_id, nurse_id, room_id, appt_date.isoformat(), status),
                )
                conn.commit()
                conn.close()
                st.success("Appointment added.")
                st.cache_data.clear()

    elif entity == "Doctor":
        departments_df = load_table("departments")
        with st.form("add_doctor"):
            c1, c2 = st.columns(2)
            first = c1.text_input("First name")
            last = c2.text_input("Last name")
            specialty = c1.text_input("Specialty")
            dept_choice = c2.selectbox("Department", departments_df["name"].tolist())
            years = st.number_input("Years of experience", min_value=0, max_value=60, value=5)
            submitted = st.form_submit_button("Add doctor")
            if submitted:
                dept_id = int(departments_df.loc[departments_df.name == dept_choice, "department_id"].iloc[0])
                conn = get_conn()
                conn.execute(
                    "INSERT INTO doctors (first_name,last_name,specialty,department_id,years_experience) VALUES (?,?,?,?,?)",
                    (first, last, specialty, dept_id, years),
                )
                conn.commit()
                conn.close()
                st.success(f"Added Dr. {first} {last}.")
                st.cache_data.clear()

    elif entity == "Diagnosis":
        appointments_df = load_table("appointments")
        with st.form("add_diagnosis"):
            appt_choice = st.selectbox(
                "Appointment", appointments_df.apply(lambda r: f"{r.appointment_id} - Patient {r.patient_id} on {r.appointment_date}", axis=1)
            )
            code = st.text_input("Diagnosis code (e.g. J06.9)")
            description = st.text_input("Description")
            severity = st.selectbox("Severity", ["Mild", "Moderate", "Severe"])
            submitted = st.form_submit_button("Add diagnosis")
            if submitted:
                appt_id = int(appt_choice.split(" - ")[0])
                conn = get_conn()
                conn.execute(
                    "INSERT INTO diagnoses (appointment_id,diagnosis_code,description,severity) VALUES (?,?,?,?)",
                    (appt_id, code, description, severity),
                )
                conn.commit()
                conn.close()
                st.success("Diagnosis added.")
                st.cache_data.clear()

    elif entity == "Billing entry":
        appointments_df = load_table("appointments")
        with st.form("add_billing"):
            appt_choice = st.selectbox(
                "Appointment", appointments_df.apply(lambda r: f"{r.appointment_id} - Patient {r.patient_id} on {r.appointment_date}", axis=1)
            )
            amount = st.number_input("Amount (EGP)", min_value=0.0, value=100.0, step=10.0)
            payment_status = st.selectbox("Payment status", ["Paid", "Pending", "Overdue"])
            payment_method = st.selectbox("Payment method", ["Insurance", "Cash", "Card"])
            billing_date = st.date_input("Billing date", value=date.today())
            submitted = st.form_submit_button("Add billing entry")
            if submitted:
                appt_id = int(appt_choice.split(" - ")[0])
                conn = get_conn()
                conn.execute(
                    "INSERT INTO billing (appointment_id,amount,payment_status,payment_method,billing_date) VALUES (?,?,?,?,?)",
                    (appt_id, amount, payment_status, payment_method, billing_date.isoformat()),
                )
                conn.commit()
                conn.close()
                st.success("Billing entry added.")
                st.cache_data.clear()

# ============================================================
# RUN SQL QUERY
# ============================================================
elif page == "🧮 Run SQL Query":
    st.title("🧮 Run a SQL Query")
    st.caption("Write any SELECT query against the database. Table names: " + ", ".join(TABLES))

    default_query = "SELECT * FROM patients LIMIT 10;"
    query = st.text_area("SQL query", value=default_query, height=150)

    if st.button("Run query", type="primary"):
        cleaned = query.strip().lower()
        if not cleaned.startswith("select"):
            st.error("Only SELECT queries are allowed here.")
        else:
            try:
                df = run_query(query)
                st.dataframe(df, use_container_width=True, height=450)
                st.caption(f"{len(df):,} rows returned")
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download results as CSV", csv, "query_results.csv", "text/csv")
            except Exception as e:
                st.error(f"Query error: {e}")