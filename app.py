"""
app.py — Clinic Management System (v2 schema).
Run with:  streamlit run app.py

Chain: Departments -> Doctors -> Patients (via Insurance) ->
       Diagnoses -> Billing -> Lab Tests (requested services)

Pages:
  Dashboard    - KPI cards, revenue trend, department/diagnosis breakdown
  Diagnoses    - searchable/filterable diagnosis list (the patient journey record)
  Patients     - patient directory, add new patient
  Doctors      - doctor directory, add new doctor
  Payments     - billing list with status badges, filters, export
  Lab Tests    - requested services list with result status
  Explore Data - raw browser for any of the 7 tables
  Add Data     - forms to insert new records
  SQL Playground - free-form SELECT queries
"""

import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import date
import plotly.express as px
from streamlit_option_menu import option_menu

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "clinic.db")

st.set_page_config(page_title="Clinic Management System", layout="wide", page_icon="🏥", initial_sidebar_state="expanded")

TABLES = ["departments", "doctors", "insurance_providers", "patients", "diagnoses", "billing", "lab_tests"]

ACCENT = "#4F46E5"
PLOTLY_COLORWAY = ["#4F46E5", "#22C55E", "#F59E0B", "#EF4444", "#06B6D4", "#A855F7", "#EC4899"]

# ============================================================
# GLOBAL STYLE
# ============================================================
st.markdown(f"""
<style>
    .block-container {{ padding-top: 1.5rem; max-width: 1300px; }}
    [data-testid="stSidebar"] {{ background: #12141F; }}
    [data-testid="stSidebar"] * {{ color: #E5E7EB !important; }}
    .kpi-card {{
        border-radius: 18px; padding: 22px 24px; color: white;
        background: linear-gradient(135deg, {ACCENT}, #7C3AED);
        box-shadow: 0 8px 20px rgba(79,70,229,0.25);
        height: 118px; display:flex; flex-direction:column; justify-content:center;
    }}
    .kpi-card.light {{
        background: #FFFFFF; color:#111827; border:1px solid #EEF0F4;
        box-shadow: 0 2px 10px rgba(17,24,39,0.05);
    }}
    .kpi-label {{ font-size:13px; opacity:0.85; margin-bottom:8px; font-weight:500; }}
    .kpi-card.light .kpi-label {{ color:#6B7280; opacity:1; }}
    .kpi-value {{ font-size:30px; font-weight:800; line-height:1; }}
    .badge {{ padding:4px 12px; border-radius:999px; font-size:12px; font-weight:700; display:inline-block; }}
    .badge-green {{ background:#DCFCE7; color:#16A34A; }}
    .badge-red {{ background:#FEE2E2; color:#DC2626; }}
    .badge-yellow {{ background:#FEF9C3; color:#CA8A04; }}
    .section-card {{
        background:white; border-radius:18px; padding:22px;
        border:1px solid #EEF0F4; box-shadow: 0 2px 10px rgba(17,24,39,0.05);
        margin-bottom: 18px;
    }}
    table {{ width:100%; border-collapse:collapse; }}
    th {{ text-align:left; padding:10px 12px; font-size:11px; text-transform:uppercase;
          letter-spacing:0.04em; color:#6B7280; border-bottom:2px solid #EEF0F4; }}
    td {{ padding:11px 12px; font-size:14px; color:#111827; border-bottom:1px solid #F3F4F6; }}
    tr:hover td {{ background:#FAFAFA; }}
    h1, h2, h3 {{ font-family: 'Segoe UI', sans-serif; }}
    .page-title {{ font-size:26px; font-weight:800; margin-bottom:2px; }}
    .page-subtitle {{ color:#6B7280; margin-bottom:20px; }}
</style>
""", unsafe_allow_html=True)


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
    st.error("clinic.db not found next to app.py. Run `python generate_data.py` first, then reload this page.")
    st.stop()


def kpi_card(label, value, light=False):
    cls = "kpi-card light" if light else "kpi-card"
    st.markdown(f"""<div class="{cls}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>""", unsafe_allow_html=True)


def badge(text):
    colors = {
        "Paid": "badge-green", "Normal": "badge-green",
        "Overdue": "badge-red", "Abnormal": "badge-red", "Severe": "badge-red",
        "Pending": "badge-yellow", "Mild": "badge-green", "Moderate": "badge-yellow",
    }
    cls = colors.get(str(text), "badge-yellow")
    return f'<span class="badge {cls}">{text}</span>'


def html_table(df, badge_cols=None, max_rows=100):
    badge_cols = badge_cols or []
    if df.empty:
        st.info("No rows match the current filters.")
        return
    rows_html = ""
    for _, row in df.head(max_rows).iterrows():
        cells = "".join(
            f"<td>{badge(row[c])}</td>" if c in badge_cols else f"<td>{row[c]}</td>"
            for c in df.columns
        )
        rows_html += f"<tr>{cells}</tr>"
    header_html = "".join(f"<th>{c.replace('_', ' ').title()}</th>" for c in df.columns)
    st.markdown(f"""<div class="section-card" style="overflow-x:auto;"><table><thead><tr>{header_html}</tr></thead><tbody>{rows_html}</tbody></table></div>""", unsafe_allow_html=True)
    if len(df) > max_rows:
        st.caption(f"Showing {max_rows:,} of {len(df):,} rows — narrow with filters to see more, or export below.")


def add_age(patients_df):
    p = patients_df.copy()
    p["dob"] = pd.to_datetime(p["dob"])
    p["age"] = ((pd.Timestamp.today() - p["dob"]).dt.days / 365.25).astype(int)
    return p


def px_layout(fig, height=320):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor="white",
                       paper_bgcolor="white", colorway=PLOTLY_COLORWAY, font=dict(family="Segoe UI", size=12))
    return fig


with st.sidebar:
    st.markdown("## 🏥 ClinicOS")
    st.caption("Clinic Management System")
    page = option_menu(
        menu_title=None,
        options=["Dashboard", "Diagnoses", "Patients", "Doctors", "Payments", "Lab Tests",
                 "Explore Data", "Add Data", "SQL Playground"],
        icons=["speedometer2", "clipboard2-pulse", "people", "person-badge", "cash-stack", "flask",
               "search", "plus-circle", "code-slash"],
        default_index=0,
        styles={
            "container": {"background-color": "#12141F"},
            "icon": {"color": "#A5B4FC", "font-size": "16px"},
            "nav-link": {"font-size": "14px", "color": "#E5E7EB", "--hover-color": "#1E2233"},
            "nav-link-selected": {"background-color": ACCENT},
        },
    )

# ============================================================
# DASHBOARD
# ============================================================
if page == "Dashboard":
    st.markdown('<div class="page-title">Hello, Manal 👋</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Here\'s what\'s happening across the clinic.</div>', unsafe_allow_html=True)

    patients = load_table("patients")
    doctors = load_table("doctors")
    departments = load_table("departments")
    diagnoses = load_table("diagnoses")
    billing = load_table("billing")
    lab_tests = load_table("lab_tests")

    total_revenue = billing["amount"].sum()
    total_diagnoses = len(diagnoses)
    total_patients = len(patients)
    overdue_rate = (billing["payment_status"] == "Overdue").mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Total Revenue", f"EGP {total_revenue:,.0f}")
    with c2: kpi_card("Total Diagnoses", f"{total_diagnoses:,}", light=True)
    with c3: kpi_card("Total Patients", f"{total_patients:,}", light=True)
    with c4: kpi_card("Overdue Rate", f"{overdue_rate:.1f}%", light=True)

    st.write("")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Monthly Revenue Trend**")
        b = billing.copy()
        b["month"] = pd.to_datetime(b["billing_date"]).dt.to_period("M").astype(str)
        monthly_rev = b.groupby("month")["amount"].sum().reset_index()
        fig = px.bar(monthly_rev, x="month", y="amount")
        fig.update_traces(marker_color=ACCENT)
        st.plotly_chart(px_layout(fig), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Payment Status**")
        status_counts = billing["payment_status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        fig2 = px.pie(status_counts, names="status", values="count", hole=0.55)
        st.plotly_chart(px_layout(fig2, height=320), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    col3, col4, col5 = st.columns(3)
    with col3:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f"### {(diagnoses['severity']=='Severe').sum():,}")
        st.caption("Severe diagnoses on record")
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f"### {len(lab_tests):,}")
        st.caption("Lab tests requested")
        st.markdown('</div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f"### {len(doctors):,}")
        st.caption("Active doctors")
        st.markdown('</div>', unsafe_allow_html=True)

    col6, col7 = st.columns(2)
    with col6:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Revenue by Department**")
        dept_rev = diagnoses.merge(doctors, on="doctor_id").merge(departments, on="department_id").merge(billing, on="diagnosis_id")
        dept_rev = dept_rev.groupby("name")["amount"].sum().sort_values(ascending=False).reset_index()
        fig3 = px.bar(dept_rev, x="amount", y="name", orientation="h")
        fig3.update_traces(marker_color=ACCENT)
        fig3.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(px_layout(fig3), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with col7:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("**Top Diagnoses**")
        top_diag = diagnoses["description"].value_counts().head(6).reset_index()
        top_diag.columns = ["diagnosis", "count"]
        fig4 = px.pie(top_diag, names="diagnosis", values="count", hole=0.55)
        st.plotly_chart(px_layout(fig4), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# DIAGNOSES
# ============================================================
elif page == "Diagnoses":
    st.markdown('<div class="page-title">Diagnoses</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Every patient visit: who saw whom, and what was found.</div>', unsafe_allow_html=True)

    diagnoses = load_table("diagnoses")
    patients = load_table("patients")
    doctors = load_table("doctors")
    departments = load_table("departments")

    merged = diagnoses.merge(patients[["patient_id", "first_name", "last_name"]], on="patient_id") \
        .merge(doctors[["doctor_id", "first_name", "last_name", "department_id"]], on="doctor_id", suffixes=("_patient", "_doctor")) \
        .merge(departments, on="department_id")
    merged["patient_name"] = merged["first_name_patient"] + " " + merged["last_name_patient"]
    merged["doctor_name"] = "Dr. " + merged["first_name_doctor"] + " " + merged["last_name_doctor"]

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        search = st.text_input("🔍 Search by patient, doctor, or diagnosis")
    with c2:
        dept_filter = st.selectbox("Department", ["All"] + sorted(departments["name"].tolist()))
    with c3:
        sev_filter = st.selectbox("Severity", ["All", "Mild", "Moderate", "Severe"])

    view = merged.copy()
    if search:
        mask = (view["patient_name"].str.contains(search, case=False) | view["doctor_name"].str.contains(search, case=False)
                | view["description"].str.contains(search, case=False))
        view = view[mask]
    if dept_filter != "All":
        view = view[view["name"] == dept_filter]
    if sev_filter != "All":
        view = view[view["severity"] == sev_filter]

    view = view.sort_values("diagnosis_date", ascending=False)
    display_df = view[["patient_name", "doctor_name", "name", "description", "diagnosis_date", "severity"]]
    display_df.columns = ["patient_name", "doctor", "department", "diagnosis", "date", "severity"]

    st.caption(f"{len(view):,} diagnoses match your filters")
    html_table(display_df, badge_cols=["severity"], max_rows=100)

    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export diagnoses as CSV", csv, "diagnoses.csv", "text/csv")

# ============================================================
# PATIENTS
# ============================================================
elif page == "Patients":
    st.markdown('<div class="page-title">Patients</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Patient directory and registration.</div>', unsafe_allow_html=True)

    patients = add_age(load_table("patients"))
    insurance = load_table("insurance_providers")
    patients = patients.merge(insurance[["insurance_id", "provider_name"]], on="insurance_id", how="left")
    patients["provider_name"] = patients["provider_name"].fillna("Self-pay")

    c1, c2 = st.columns([3, 1])
    with c1:
        search = st.text_input("🔍 Search by name or city")
    with c2:
        st.write("")
        show_form = st.button("➕ Add Patient", use_container_width=True)

    if show_form:
        with st.form("quick_add_patient"):
            cc1, cc2 = st.columns(2)
            first = cc1.text_input("First name")
            last = cc2.text_input("Last name")
            dob = cc1.date_input("Date of birth", min_value=date(1920, 1, 1), max_value=date.today())
            gender = cc2.selectbox("Gender", ["Male", "Female"])
            city = cc1.text_input("City")
            ins_choice = cc2.selectbox("Insurance provider", ["None"] + insurance["provider_name"].tolist())
            submitted = st.form_submit_button("Save patient")
            if submitted and first and last:
                ins_id = None
                if ins_choice != "None":
                    ins_id = int(insurance.loc[insurance.provider_name == ins_choice, "insurance_id"].iloc[0])
                conn = get_conn()
                conn.execute(
                    "INSERT INTO patients (first_name,last_name,dob,gender,city,insurance_id,registration_date) VALUES (?,?,?,?,?,?,?)",
                    (first, last, dob.isoformat(), gender, city, ins_id, date.today().isoformat()),
                )
                conn.commit(); conn.close()
                st.success(f"Added {first} {last}.")
                st.cache_data.clear()

    view = patients.copy()
    if search:
        mask = (view["first_name"] + " " + view["last_name"]).str.contains(search, case=False) | view["city"].str.contains(search, case=False)
        view = view[mask]

    view["patient_name"] = view["first_name"] + " " + view["last_name"]
    display_df = view[["patient_name", "age", "gender", "city", "provider_name", "registration_date"]]
    display_df.columns = ["patient_name", "age", "gender", "city", "insurance", "registered"]

    st.caption(f"{len(view):,} patients match your search")
    html_table(display_df, max_rows=100)
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export patients as CSV", csv, "patients.csv", "text/csv")

# ============================================================
# DOCTORS
# ============================================================
elif page == "Doctors":
    st.markdown('<div class="page-title">Doctors</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Staff directory by department and specialty.</div>', unsafe_allow_html=True)

    doctors = load_table("doctors")
    departments = load_table("departments")
    diagnoses = load_table("diagnoses")

    workload = diagnoses.groupby("doctor_id").size().reset_index(name="num_diagnoses")
    doctors = doctors.merge(departments, on="department_id").merge(workload, on="doctor_id", how="left")
    doctors["num_diagnoses"] = doctors["num_diagnoses"].fillna(0).astype(int)

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        search = st.text_input("🔍 Search by name or specialty")
    with c2:
        dept_filter = st.selectbox("Department", ["All"] + sorted(departments["name"].tolist()))
    with c3:
        st.write("")
        show_form = st.button("➕ Add Doctor", use_container_width=True)

    if show_form:
        with st.form("quick_add_doctor"):
            cc1, cc2 = st.columns(2)
            first = cc1.text_input("First name")
            last = cc2.text_input("Last name")
            specialty = cc1.text_input("Specialty")
            dept_choice = cc2.selectbox("Department", departments["name"].tolist())
            years = st.number_input("Years of experience", min_value=0, max_value=60, value=5)
            submitted = st.form_submit_button("Save doctor")
            if submitted and first and last:
                dept_id = int(departments.loc[departments.name == dept_choice, "department_id"].iloc[0])
                conn = get_conn()
                conn.execute(
                    "INSERT INTO doctors (first_name,last_name,specialty,department_id,years_experience) VALUES (?,?,?,?,?)",
                    (first, last, specialty, dept_id, years),
                )
                conn.commit(); conn.close()
                st.success(f"Added Dr. {first} {last}.")
                st.cache_data.clear()

    view = doctors.copy()
    if search:
        mask = (view["first_name"] + " " + view["last_name"]).str.contains(search, case=False) | view["specialty"].str.contains(search, case=False)
        view = view[mask]
    if dept_filter != "All":
        view = view[view["name"] == dept_filter]

    view["doctor_name"] = "Dr. " + view["first_name"] + " " + view["last_name"]
    display_df = view[["doctor_name", "specialty", "name", "years_experience", "num_diagnoses"]]
    display_df.columns = ["doctor", "specialty", "department", "years_experience", "num_diagnoses"]
    display_df = display_df.sort_values("num_diagnoses", ascending=False)

    st.caption(f"{len(view):,} doctors match your search")
    html_table(display_df, max_rows=100)

# ============================================================
# PAYMENTS
# ============================================================
elif page == "Payments":
    st.markdown('<div class="page-title">Payments</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Billing records, payment status, and collections.</div>', unsafe_allow_html=True)

    billing = load_table("billing")
    diagnoses = load_table("diagnoses")
    patients = load_table("patients")

    merged = billing.merge(diagnoses[["diagnosis_id", "patient_id", "description"]], on="diagnosis_id") \
        .merge(patients[["patient_id", "first_name", "last_name"]], on="patient_id")
    merged["patient_name"] = merged["first_name"] + " " + merged["last_name"]

    paid_n = (billing["payment_status"] == "Paid").sum()
    pending_n = (billing["payment_status"] == "Pending").sum()
    overdue_n = (billing["payment_status"] == "Overdue").sum()

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Total Billed", f"EGP {billing['amount'].sum():,.0f}")
    with c2: kpi_card("Paid Bills", f"{paid_n:,}", light=True)
    with c3: kpi_card("Pending Bills", f"{pending_n:,}", light=True)
    with c4: kpi_card("Overdue Bills", f"{overdue_n:,}", light=True)

    st.write("")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        search = st.text_input("🔍 Search by patient name")
    with c2:
        status_filter = st.selectbox("Payment status", ["All", "Paid", "Pending", "Overdue"])
    with c3:
        method_filter = st.selectbox("Payment method", ["All", "Insurance", "Cash", "Card"])

    view = merged.copy()
    if search:
        view = view[view["patient_name"].str.contains(search, case=False)]
    if status_filter != "All":
        view = view[view["payment_status"] == status_filter]
    if method_filter != "All":
        view = view[view["payment_method"] == method_filter]

    view = view.sort_values("billing_date", ascending=False)
    display_df = view[["patient_name", "description", "amount", "billing_date", "payment_method", "payment_status"]]
    display_df.columns = ["patient_name", "diagnosis", "amount_egp", "date", "method", "status"]

    st.caption(f"{len(view):,} bills match your filters")
    html_table(display_df, badge_cols=["status"], max_rows=100)
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export payments as CSV", csv, "payments.csv", "text/csv")

# ============================================================
# LAB TESTS
# ============================================================
elif page == "Lab Tests":
    st.markdown('<div class="page-title">Lab Tests</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Requested services and their results.</div>', unsafe_allow_html=True)

    lab_tests = load_table("lab_tests")
    diagnoses = load_table("diagnoses")
    patients = load_table("patients")

    merged = lab_tests.merge(diagnoses[["diagnosis_id", "patient_id", "description"]], on="diagnosis_id") \
        .merge(patients[["patient_id", "first_name", "last_name"]], on="patient_id")
    merged["patient_name"] = merged["first_name"] + " " + merged["last_name"]

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        search = st.text_input("🔍 Search by patient name")
    with c2:
        type_filter = st.selectbox("Test type", ["All"] + sorted(lab_tests["test_type"].unique().tolist()))
    with c3:
        result_filter = st.selectbox("Result", ["All", "Normal", "Abnormal", "Pending"])

    view = merged.copy()
    if search:
        view = view[view["patient_name"].str.contains(search, case=False)]
    if type_filter != "All":
        view = view[view["test_type"] == type_filter]
    if result_filter != "All":
        view = view[view["result_status"] == result_filter]

    view = view.sort_values("test_date", ascending=False)
    display_df = view[["patient_name", "description", "test_type", "test_date", "result_status"]]
    display_df.columns = ["patient_name", "diagnosis", "test_type", "date", "result"]

    st.caption(f"{len(view):,} lab tests match your filters")
    html_table(display_df, badge_cols=["result"], max_rows=100)
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Export lab tests as CSV", csv, "lab_tests.csv", "text/csv")

# ============================================================
# EXPLORE DATA
# ============================================================
elif page == "Explore Data":
    st.markdown('<div class="page-title">Explore Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Browse any table directly.</div>', unsafe_allow_html=True)

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
elif page == "Add Data":
    st.markdown('<div class="page-title">Add Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Insert diagnoses, billing entries, or lab tests. (Patients and Doctors can also be added from their own pages.)</div>', unsafe_allow_html=True)

    entity = st.selectbox("What do you want to add?", ["Diagnosis", "Billing entry", "Lab test"])

    if entity == "Diagnosis":
        patients_df = load_table("patients")
        doctors_df = load_table("doctors")
        with st.form("add_diagnosis"):
            patient_choice = st.selectbox("Patient", patients_df.apply(lambda r: f"{r.patient_id} - {r.first_name} {r.last_name}", axis=1))
            doctor_choice = st.selectbox("Doctor", doctors_df.apply(lambda r: f"{r.doctor_id} - Dr. {r.first_name} {r.last_name} ({r.specialty})", axis=1))
            code = st.text_input("Diagnosis code (e.g. J06.9)")
            description = st.text_input("Description")
            severity = st.selectbox("Severity", ["Mild", "Moderate", "Severe"])
            diag_date = st.date_input("Diagnosis date", value=date.today())
            submitted = st.form_submit_button("Add diagnosis")
            if submitted:
                patient_id = int(patient_choice.split(" - ")[0])
                doctor_id = int(doctor_choice.split(" - ")[0])
                conn = get_conn()
                conn.execute(
                    "INSERT INTO diagnoses (patient_id,doctor_id,diagnosis_code,description,severity,diagnosis_date) VALUES (?,?,?,?,?,?)",
                    (patient_id, doctor_id, code, description, severity, diag_date.isoformat()),
                )
                conn.commit(); conn.close()
                st.success("Diagnosis added.")
                st.cache_data.clear()

    elif entity == "Billing entry":
        diagnoses_df = load_table("diagnoses")
        with st.form("add_billing"):
            diag_choice = st.selectbox("Diagnosis", diagnoses_df.apply(lambda r: f"{r.diagnosis_id} - {r.description} (patient {r.patient_id})", axis=1))
            amount = st.number_input("Amount (EGP)", min_value=0.0, value=100.0, step=10.0)
            payment_status = st.selectbox("Payment status", ["Paid", "Pending", "Overdue"])
            payment_method = st.selectbox("Payment method", ["Insurance", "Cash", "Card"])
            billing_date = st.date_input("Billing date", value=date.today())
            submitted = st.form_submit_button("Add billing entry")
            if submitted:
                diag_id = int(diag_choice.split(" - ")[0])
                conn = get_conn()
                conn.execute(
                    "INSERT INTO billing (diagnosis_id,amount,payment_status,payment_method,billing_date) VALUES (?,?,?,?,?)",
                    (diag_id, amount, payment_status, payment_method, billing_date.isoformat()),
                )
                conn.commit(); conn.close()
                st.success("Billing entry added.")
                st.cache_data.clear()

    elif entity == "Lab test":
        diagnoses_df = load_table("diagnoses")
        with st.form("add_lab_test"):
            diag_choice = st.selectbox("Diagnosis", diagnoses_df.apply(lambda r: f"{r.diagnosis_id} - {r.description} (patient {r.patient_id})", axis=1))
            test_type = st.selectbox("Test type", ["Blood Panel", "X-Ray", "MRI", "Urine Test", "ECG"])
            result_status = st.selectbox("Result status", ["Normal", "Abnormal", "Pending"])
            test_date = st.date_input("Test date", value=date.today())
            submitted = st.form_submit_button("Add lab test")
            if submitted:
                diag_id = int(diag_choice.split(" - ")[0])
                conn = get_conn()
                conn.execute(
                    "INSERT INTO lab_tests (diagnosis_id,test_type,result_status,test_date) VALUES (?,?,?,?)",
                    (diag_id, test_type, result_status, test_date.isoformat()),
                )
                conn.commit(); conn.close()
                st.success("Lab test added.")
                st.cache_data.clear()

# ============================================================
# SQL PLAYGROUND
# ============================================================
elif page == "SQL Playground":
    st.markdown('<div class="page-title">SQL Playground</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Run any SELECT query against the database.</div>', unsafe_allow_html=True)
    st.caption("Tables: " + ", ".join(TABLES))

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
