import { useEffect, useState } from "react";
import api from "../api";
import { Plus, Search } from "lucide-react";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";

const COLUMNS = [
  { key: "patient_name", label: "Patient" },
  { key: "doctor_name", label: "Doctor" },
  { key: "description", label: "Diagnosis" },
  { key: "diagnosis_date", label: "Date" },
  { key: "severity", label: "Severity", badge: true },
];

export default function Diagnoses() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState("");
  const [appointments, setAppointments] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ appointment_id: "", diagnosis_code: "", description: "", severity: "Mild", diagnosis_date: "" });
  const perPage = 10;

  useEffect(() => {
    api.get("/appointments", { params: { per_page: 200 } }).then((res) => setAppointments(res.data.items));
  }, []);

  const load = () => {
    api.get("/diagnoses", { params: { page, per_page: perPage, search: search || undefined, severity: severity || undefined } })
      .then((res) => { setItems(res.data.items); setTotal(res.data.total); });
  };

  useEffect(() => { load(); }, [page, search, severity]);

  const submit = async (e) => {
    e.preventDefault();
    if (!form.appointment_id || !form.description) return;
    await api.post("/diagnoses", {
      ...form,
      appointment_id: Number(form.appointment_id),
      diagnosis_date: form.diagnosis_date || undefined,
    });
    setForm({ appointment_id: "", diagnosis_code: "", description: "", severity: "Mild", diagnosis_date: "" });
    setOpen(false);
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900">Diagnoses</h1>
          <p className="text-gray-500">Every patient visit: who saw whom, and what was found.</p>
        </div>
        <button onClick={() => setOpen(true)} className="glass-action flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm">
          <Plus size={16} /> Add Diagnosis
        </button>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            value={search}
            onChange={(e) => { setPage(1); setSearch(e.target.value); }}
            placeholder="Search diagnosis description…"
            className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
        <select value={severity} onChange={(e) => { setPage(1); setSeverity(e.target.value); }} className="px-3 py-2.5 rounded-xl border border-gray-200 text-sm">
          <option value="">All severities</option>
          <option>Mild</option>
          <option>Moderate</option>
          <option>Severe</option>
        </select>
      </div>

      <DataTable columns={COLUMNS} rows={items} page={page} perPage={perPage} total={total} onPageChange={setPage} resource="diagnoses" idKey="diagnosis_id" onChanged={load} />

      <Modal open={open} onClose={() => setOpen(false)} title="Add Diagnosis">
        <form onSubmit={submit} className="space-y-3">
          <select value={form.appointment_id} onChange={(e) => setForm({ ...form, appointment_id: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Select appointment</option>
            {appointments.map((appointment) => (
              <option key={appointment.appointment_id} value={appointment.appointment_id}>
                {appointment.patient_name} — {appointment.doctor_name} — {appointment.appointment_date}
              </option>
            ))}
          </select>
          <div className="grid grid-cols-2 gap-3">
            <input placeholder="Code (e.g. J06.9)" value={form.diagnosis_code} onChange={(e) => setForm({ ...form, diagnosis_code: e.target.value })} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
            <select value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })} className="px-3 py-2 border border-gray-200 rounded-lg text-sm">
              <option>Mild</option>
              <option>Moderate</option>
              <option>Severe</option>
            </select>
          </div>
          <input placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <input type="date" value={form.diagnosis_date} onChange={(e) => setForm({ ...form, diagnosis_date: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <button type="submit" className="glass-action w-full bg-brand-600 hover:bg-brand-700 text-white py-2.5 rounded-lg font-medium text-sm">Save</button>
        </form>
      </Modal>
    </div>
  );
}
