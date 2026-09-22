"""
app.py — Clinic RCM Backend API (Flask + SQLAlchemy)
Run with: python app.py
Serves on http://localhost:5000

Reads/writes the same clinic.db used by the rest of the project.
Chain: Departments -> Doctors -> Patients (via Insurance) ->
       Diagnoses -> Billing -> Lab Tests (requested services)
"""

from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import date, datetime
import io
import os
import zipfile

import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "clinic.db")

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# ============================================================
# MODELS (map onto the existing tables — no new tables created)
# ============================================================
class Department(db.Model):
    __tablename__ = "departments"
    department_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {"department_id": self.department_id, "name": self.name}


class Doctor(db.Model):
    __tablename__ = "doctors"
    doctor_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    specialty = db.Column(db.String, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.department_id"), nullable=False)

    def to_dict(self):
        dept = Department.query.get(self.department_id)
        return {
            "doctor_id": self.doctor_id, "first_name": self.first_name, "last_name": self.last_name,
            "specialty": self.specialty, "department_id": self.department_id,
            "department_name": dept.name if dept else None,
        }


class InsuranceProvider(db.Model):
    __tablename__ = "insurance_providers"
    insurance_id = db.Column(db.Integer, primary_key=True)
    provider_name = db.Column(db.String, nullable=False)
    coverage_type = db.Column(db.String, nullable=False)
    contact_phone = db.Column(db.String)

    def to_dict(self):
        return {
            "insurance_id": self.insurance_id, "provider_name": self.provider_name,
            "coverage_type": self.coverage_type, "contact_phone": self.contact_phone,
        }


class Patient(db.Model):
    __tablename__ = "patients"
    patient_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    dob = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    insurance_id = db.Column(db.Integer, db.ForeignKey("insurance_providers.insurance_id"))
    registration_date = db.Column(db.String, nullable=False)

    def to_dict(self):
        ins = InsuranceProvider.query.get(self.insurance_id) if self.insurance_id else None
        age = None
        try:
            d = datetime.strptime(self.dob, "%Y-%m-%d").date()
            age = (date.today() - d).days // 365
        except Exception:
            pass
        return {
            "patient_id": self.patient_id, "first_name": self.first_name, "last_name": self.last_name,
            "dob": self.dob, "age": age, "gender": self.gender, "city": self.city,
            "insurance_id": self.insurance_id, "insurance_name": ins.provider_name if ins else "Self-pay",
            "registration_date": self.registration_date,
        }


class Diagnosis(db.Model):
    __tablename__ = "diagnoses"
    diagnosis_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.patient_id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.doctor_id"), nullable=False)
    diagnosis_code = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    severity = db.Column(db.String, nullable=False)
    diagnosis_date = db.Column(db.String, nullable=False)

    def to_dict(self):
        p = Patient.query.get(self.patient_id)
        d = Doctor.query.get(self.doctor_id)
        return {
            "diagnosis_id": self.diagnosis_id, "patient_id": self.patient_id,
            "patient_name": f"{p.first_name} {p.last_name}" if p else None,
            "doctor_id": self.doctor_id,
            "doctor_name": f"Dr. {d.first_name} {d.last_name}" if d else None,
            "specialty": d.specialty if d else None,
            "diagnosis_code": self.diagnosis_code, "description": self.description,
            "severity": self.severity, "diagnosis_date": self.diagnosis_date,
        }


class Billing(db.Model):
    __tablename__ = "billing"
    billing_id = db.Column(db.Integer, primary_key=True)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey("diagnoses.diagnosis_id"), nullable=False, unique=True)
    amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String, nullable=False)
    payment_method = db.Column(db.String, nullable=False)
    billing_date = db.Column(db.String, nullable=False)

    def to_dict(self):
        dg = Diagnosis.query.get(self.diagnosis_id)
        patient_name = None
        if dg:
            p = Patient.query.get(dg.patient_id)
            patient_name = f"{p.first_name} {p.last_name}" if p else None
        return {
            "billing_id": self.billing_id, "diagnosis_id": self.diagnosis_id,
            "patient_name": patient_name, "diagnosis": dg.description if dg else None,
            "amount": self.amount, "payment_status": self.payment_status,
            "payment_method": self.payment_method, "billing_date": self.billing_date,
        }


class LabTest(db.Model):
    __tablename__ = "lab_tests"
    lab_test_id = db.Column(db.Integer, primary_key=True)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey("diagnoses.diagnosis_id"), nullable=False)
    test_type = db.Column(db.String, nullable=False)
    result_status = db.Column(db.String, nullable=False)
    test_date = db.Column(db.String, nullable=False)

    def to_dict(self):
        dg = Diagnosis.query.get(self.diagnosis_id)
        patient_name = None
        if dg:
            p = Patient.query.get(dg.patient_id)
            patient_name = f"{p.first_name} {p.last_name}" if p else None
        return {
            "lab_test_id": self.lab_test_id, "diagnosis_id": self.diagnosis_id,
            "patient_name": patient_name, "diagnosis": dg.description if dg else None,
            "test_type": self.test_type, "result_status": self.result_status, "test_date": self.test_date,
        }


class Appointment(db.Model):
    __tablename__ = "appointments"
    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False)
    doctor_id = db.Column(db.Integer, nullable=False)
    nurse_id = db.Column(db.Integer, nullable=False)
    room_id = db.Column(db.Integer, nullable=False)
    appointment_date = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)

    def to_dict(self):
        patient = Patient.query.get(self.patient_id)
        doctor = Doctor.query.get(self.doctor_id)
        return {
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "patient_name": f"{patient.first_name} {patient.last_name}" if patient else None,
            "doctor_id": self.doctor_id,
            "doctor_name": f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else None,
            "nurse_id": self.nurse_id, "room_id": self.room_id,
            "appointment_date": self.appointment_date, "status": self.status,
        }


# ============================================================
# HELPERS
# ============================================================
def paginate(query, page, per_page):
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_page_params():
    page = int(request.args.get("page", 1))
    per_page = min(int(request.args.get("per_page", 50)), 200)
    return page, per_page


RECORD_MODELS = {
    "departments": (Department, "department_id"),
    "doctors": (Doctor, "doctor_id"),
    "insurance_providers": (InsuranceProvider, "insurance_id"),
    "patients": (Patient, "patient_id"),
    "diagnoses": (Diagnosis, "diagnosis_id"),
    "billing": (Billing, "billing_id"),
    "lab_tests": (LabTest, "lab_test_id"),
    "appointments": (Appointment, "appointment_id"),
}


@app.route("/api/records/<table>/<int:record_id>", methods=["PUT", "DELETE"])
def modify_record(table, record_id):
    config = RECORD_MODELS.get(table)
    if not config:
        return jsonify({"error": "invalid table name"}), 404

    model, id_field = config
    record = db.session.get(model, record_id)
    if not record:
        return jsonify({"error": "record not found"}), 404

    if request.method == "DELETE":
        db.session.delete(record)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return jsonify({"error": "record cannot be deleted because it is referenced by another record"}), 409
        return jsonify({"message": "Record deleted"})

    data = request.get_json(silent=True) or {}
    editable_fields = {
        column.name for column in model.__table__.columns
        if not column.primary_key
    }
    updates = {key: value for key, value in data.items() if key in editable_fields}
    if not updates:
        return jsonify({"error": "no editable fields supplied"}), 400
    for key, value in updates.items():
        setattr(record, key, value)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "record could not be updated"}), 400
    return jsonify(record.to_dict())


# ============================================================
# DASHBOARD
# ============================================================
@app.route("/api/dashboard/summary")
def dashboard_summary():
    total_revenue = db.session.query(db.func.sum(Billing.amount)).scalar() or 0
    total_diagnoses = Diagnosis.query.count()
    total_patients = Patient.query.count()
    total_doctors = Doctor.query.count()
    overdue_count = Billing.query.filter_by(payment_status="Overdue").count()
    total_bills = Billing.query.count()
    overdue_rate = round(100 * overdue_count / total_bills, 1) if total_bills else 0
    severe_count = Diagnosis.query.filter_by(severity="Severe").count()
    lab_test_count = LabTest.query.count()

    # revenue by month
    rows = db.session.query(Billing.billing_date, Billing.amount).all()
    monthly = {}
    for bdate, amount in rows:
        month = bdate[:7] if bdate else "unknown"
        monthly[month] = monthly.get(month, 0) + amount
    monthly_revenue = [{"month": m, "amount": round(a, 2)} for m, a in sorted(monthly.items())]

    # payment status breakdown
    status_rows = db.session.query(Billing.payment_status, db.func.count(Billing.billing_id)).group_by(Billing.payment_status).all()
    payment_status = [{"status": s, "count": c} for s, c in status_rows]

    # revenue by department
    dept_rows = (
        db.session.query(Department.name, db.func.sum(Billing.amount))
        .join(Doctor, Doctor.department_id == Department.department_id)
        .join(Diagnosis, Diagnosis.doctor_id == Doctor.doctor_id)
        .join(Billing, Billing.diagnosis_id == Diagnosis.diagnosis_id)
        .group_by(Department.name)
        .order_by(db.func.sum(Billing.amount).desc())
        .all()
    )
    revenue_by_department = [{"department": d, "revenue": round(r, 2)} for d, r in dept_rows]

    # top diagnoses
    diag_rows = (
        db.session.query(Diagnosis.description, db.func.count(Diagnosis.diagnosis_id))
        .group_by(Diagnosis.description)
        .order_by(db.func.count(Diagnosis.diagnosis_id).desc())
        .limit(6)
        .all()
    )
    top_diagnoses = [{"diagnosis": d, "count": c} for d, c in diag_rows]

    return jsonify({
        "total_revenue": round(total_revenue, 2),
        "total_diagnoses": total_diagnoses,
        "total_patients": total_patients,
        "total_doctors": total_doctors,
        "overdue_rate": overdue_rate,
        "severe_count": severe_count,
        "lab_test_count": lab_test_count,
        "monthly_revenue": monthly_revenue,
        "payment_status": payment_status,
        "revenue_by_department": revenue_by_department,
        "top_diagnoses": top_diagnoses,
    })


# ============================================================
# DEPARTMENTS
# ============================================================
@app.route("/api/departments", methods=["GET", "POST"])
def departments():
    if request.method == "POST":
        data = request.get_json()
        d = Department(name=data["name"])
        db.session.add(d)
        db.session.commit()
        return jsonify(d.to_dict()), 201
    items = Department.query.order_by(Department.name).all()
    return jsonify([i.to_dict() for i in items])


# ============================================================
# DOCTORS
# ============================================================
@app.route("/api/doctors", methods=["GET", "POST"])
def doctors():
    if request.method == "POST":
        data = request.get_json()
        d = Doctor(first_name=data["first_name"], last_name=data["last_name"],
                    specialty=data["specialty"], department_id=data["department_id"])
        db.session.add(d)
        db.session.commit()
        return jsonify(d.to_dict()), 201

    q = Doctor.query
    search = request.args.get("search")
    specialty = request.args.get("specialty")
    department_id = request.args.get("department_id")
    if search:
        like = f"%{search}%"
        q = q.filter(db.or_(Doctor.first_name.ilike(like), Doctor.last_name.ilike(like), Doctor.specialty.ilike(like)))
    if specialty:
        q = q.filter(Doctor.specialty == specialty)
    if department_id:
        q = q.filter(Doctor.department_id == int(department_id))

    page, per_page = get_page_params()
    items, total = paginate(q, page, per_page)
    return jsonify({"items": [i.to_dict() for i in items], "total": total, "page": page, "per_page": per_page})


# ============================================================
# PATIENTS
# ============================================================
@app.route("/api/patients", methods=["GET", "POST"])
def patients():
    if request.method == "POST":
        data = request.get_json()
        p = Patient(
            first_name=data["first_name"], last_name=data["last_name"], dob=data["dob"],
            gender=data["gender"], city=data["city"], insurance_id=data.get("insurance_id"),
            registration_date=data.get("registration_date", date.today().isoformat()),
        )
        db.session.add(p)
        db.session.commit()
        return jsonify(p.to_dict()), 201

    q = Patient.query
    search = request.args.get("search")
    city = request.args.get("city")
    if search:
        like = f"%{search}%"
        q = q.filter(db.or_(Patient.first_name.ilike(like), Patient.last_name.ilike(like), Patient.city.ilike(like)))
    if city:
        q = q.filter(Patient.city == city)

    page, per_page = get_page_params()
    items, total = paginate(q.order_by(Patient.patient_id.desc()), page, per_page)
    return jsonify({"items": [i.to_dict() for i in items], "total": total, "page": page, "per_page": per_page})


# ============================================================
# DIAGNOSES
# ============================================================
@app.route("/api/diagnoses", methods=["GET", "POST"])
def diagnoses():
    if request.method == "POST":
        data = request.get_json()
        dg = Diagnosis(
            patient_id=data["patient_id"], doctor_id=data["doctor_id"],
            diagnosis_code=data["diagnosis_code"], description=data["description"],
            severity=data["severity"], diagnosis_date=data.get("diagnosis_date", date.today().isoformat()),
        )
        db.session.add(dg)
        db.session.commit()
        return jsonify(dg.to_dict()), 201

    q = Diagnosis.query
    search = request.args.get("search")
    severity = request.args.get("severity")
    department_id = request.args.get("department_id")
    if search:
        like = f"%{search}%"
        q = q.filter(Diagnosis.description.ilike(like))
    if severity:
        q = q.filter(Diagnosis.severity == severity)
    if department_id:
        q = q.join(Doctor, Doctor.doctor_id == Diagnosis.doctor_id).filter(Doctor.department_id == int(department_id))

    page, per_page = get_page_params()
    items, total = paginate(q.order_by(Diagnosis.diagnosis_id.desc()), page, per_page)
    return jsonify({"items": [i.to_dict() for i in items], "total": total, "page": page, "per_page": per_page})


# ============================================================
# BILLING (Payments)
# ============================================================
@app.route("/api/billing", methods=["GET", "POST"])
def billing():
    if request.method == "POST":
        data = request.get_json()
        b = Billing(
            diagnosis_id=data["diagnosis_id"], amount=data["amount"],
            payment_status=data["payment_status"], payment_method=data["payment_method"],
            billing_date=data.get("billing_date", date.today().isoformat()),
        )
        db.session.add(b)
        db.session.commit()
        return jsonify(b.to_dict()), 201

    q = Billing.query
    status = request.args.get("status")
    method = request.args.get("method")
    if status:
        q = q.filter(Billing.payment_status == status)
    if method:
        q = q.filter(Billing.payment_method == method)

    page, per_page = get_page_params()
    items, total = paginate(q.order_by(Billing.billing_id.desc()), page, per_page)
    return jsonify({"items": [i.to_dict() for i in items], "total": total, "page": page, "per_page": per_page})


# ============================================================
# LAB TESTS (Services)
# ============================================================
@app.route("/api/lab_tests", methods=["GET", "POST"])
def lab_tests():
    if request.method == "POST":
        data = request.get_json()
        lt = LabTest(
            diagnosis_id=data["diagnosis_id"], test_type=data["test_type"],
            result_status=data["result_status"], test_date=data.get("test_date", date.today().isoformat()),
        )
        db.session.add(lt)
        db.session.commit()
        return jsonify(lt.to_dict()), 201

    q = LabTest.query
    test_type = request.args.get("test_type")
    result_status = request.args.get("result_status")
    if test_type:
        q = q.filter(LabTest.test_type == test_type)
    if result_status:
        q = q.filter(LabTest.result_status == result_status)

    page, per_page = get_page_params()
    items, total = paginate(q.order_by(LabTest.lab_test_id.desc()), page, per_page)
    return jsonify({"items": [i.to_dict() for i in items], "total": total, "page": page, "per_page": per_page})


@app.route("/api/appointments", methods=["GET", "POST"])
def appointments():
    if request.method == "POST":
        data = request.get_json()
        appointment = Appointment(
            patient_id=data["patient_id"], doctor_id=data["doctor_id"],
            nurse_id=data["nurse_id"], room_id=data["room_id"],
            appointment_date=data["appointment_date"], status=data["status"],
        )
        db.session.add(appointment)
        db.session.commit()
        return jsonify(appointment.to_dict()), 201

    query = Appointment.query
    status = request.args.get("status")
    if status:
        query = query.filter(Appointment.status == status)
    page, per_page = get_page_params()
    items, total = paginate(query.order_by(Appointment.appointment_id.desc()), page, per_page)
    return jsonify({"items": [item.to_dict() for item in items], "total": total, "page": page, "per_page": per_page})


# ============================================================
# INSURANCE PROVIDERS (for dropdowns)
# ============================================================
@app.route("/api/insurance_providers")
def insurance_providers():
    items = InsuranceProvider.query.all()
    return jsonify([i.to_dict() for i in items])


# ============================================================
# CSV IMPORT / EXPORT
# ============================================================
ALL_TABLES = [
    "departments", "doctors", "insurance_providers", "patients",
    "diagnoses", "billing", "lab_tests", "appointments",
]


@app.route("/api/export/csv")
def export_csv():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for table in ALL_TABLES:
            df = pd.read_sql_table(table, db.engine)
            zf.writestr(f"{table}.csv", df.to_csv(index=False).encode("utf-8"))
    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="clinic_data.zip",
    )


@app.route("/api/import/csv", methods=["POST"])
def import_csv():
    table = request.form.get("table")
    file = request.files.get("file")
    if not table or not file:
        return jsonify({"error": "table and file are required"}), 400
    if table not in ALL_TABLES:
        return jsonify({"error": "invalid table name"}), 400
    df = pd.read_csv(file)
    df.to_sql(table, db.engine, if_exists="append", index=False)
    return jsonify({"message": f"Imported {len(df)} rows into {table}"}), 201


if __name__ == "__main__":
    app.run(debug=False, port=5000, host="0.0.0.0", threaded=True)
