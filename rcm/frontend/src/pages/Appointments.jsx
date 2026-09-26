import { useEffect, useState } from "react";
import { Plus } from "lucide-react";
import api from "../api";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";

const COLUMNS = [
  { key: "patient_name", label: "Patient" },
  { key: "doctor_name", label: "Doctor" },
  { key: "appointment_date", label: "Date" },
  { key: "appointment_time", label: "Time" },
  { key: "status", label: "Status", badge: true },
  { key: "reason_for_visit", label: "Reason" },
];

export default function Appointments() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");
  const [open, setOpen] = useState(false);
  const [patients, setPatients] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [statuses, setStatuses] = useState([]);
  const [form, setForm] = useState({ patient_id: "", doctor_id: "", appointment_date: "", appointment_time: "", reason_for_visit: "", status: "Scheduled" });
  const perPage = 10;

  const load = () => api.get("/appointments", { params: { page, per_page: perPage, status: status || undefined } }).then((res) => {
    setItems(res.data.items); setTotal(res.data.total);
  });

  useEffect(() => {
    load();
  }, [page, status]);

  useEffect(() => {
    api.get("/options").then((res) => setStatuses(res.data.appointment_statuses));
    api.get("/patients", { params: { per_page: 200 } }).then((res) => setPatients(res.data.items));
    api.get("/doctors", { params: { per_page: 200 } }).then((res) => setDoctors(res.data.items));
  }, []);

  const submit = async (event) => {
    event.preventDefault();
    if (!form.patient_id || !form.doctor_id || !form.appointment_date) return;
    await api.post("/appointments", { ...form, patient_id: Number(form.patient_id), doctor_id: Number(form.doctor_id) });
    setForm({ patient_id: "", doctor_id: "", appointment_date: "", appointment_time: "", reason_for_visit: "", status: "Scheduled" });
    setOpen(false); load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-extrabold text-gray-900">Appointments</h1><p className="text-gray-500">Patient visits and scheduling records.</p></div>
        <button onClick={() => setOpen(true)} className="glass-action flex items-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-700"><Plus size={16} /> Add Appointment</button>
      </div>
      <select value={status} onChange={(event) => { setPage(1); setStatus(event.target.value); }} className="rounded-xl border border-gray-200 px-3 py-2.5 text-sm">
        <option value="">All statuses</option>{statuses.map((value) => <option key={value}>{value}</option>)}
      </select>
      <DataTable columns={COLUMNS} rows={items} page={page} perPage={perPage} total={total} onPageChange={setPage} resource="appointments" idKey="appointment_id" onChanged={load} />
      <Modal open={open} onClose={() => setOpen(false)} title="Add Appointment">
        <form onSubmit={submit} className="space-y-3">
          <select value={form.patient_id} onChange={(e) => setForm({ ...form, patient_id: e.target.value })} className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm"><option value="">Select patient</option>{patients.map((p) => <option key={p.patient_id} value={p.patient_id}>{p.first_name} {p.last_name}</option>)}</select>
          <select value={form.doctor_id} onChange={(e) => setForm({ ...form, doctor_id: e.target.value })} className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm"><option value="">Select doctor</option>{doctors.map((d) => <option key={d.doctor_id} value={d.doctor_id}>Dr. {d.first_name} {d.last_name}</option>)}</select>
          <div className="grid grid-cols-2 gap-3"><input aria-label="Appointment date" type="date" value={form.appointment_date} onChange={(e) => setForm({ ...form, appointment_date: e.target.value })} className="rounded-lg border border-gray-200 px-3 py-2 text-sm" /><input aria-label="Appointment time" type="time" value={form.appointment_time} onChange={(e) => setForm({ ...form, appointment_time: e.target.value })} className="rounded-lg border border-gray-200 px-3 py-2 text-sm" /></div>
          <input placeholder="Reason for visit" value={form.reason_for_visit} onChange={(e) => setForm({ ...form, reason_for_visit: e.target.value })} className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm" />
          <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })} className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm">{statuses.map((value) => <option key={value}>{value}</option>)}</select>
          <button type="submit" className="w-full rounded-lg bg-brand-600 py-2.5 text-sm font-medium text-white hover:bg-brand-700">Save</button>
        </form>
      </Modal>
    </div>
  );
}