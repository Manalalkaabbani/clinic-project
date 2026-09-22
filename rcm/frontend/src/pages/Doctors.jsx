import { useEffect, useState } from "react";
import api from "../api";
import { Plus, Search } from "lucide-react";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";

const COLUMNS = [
  { key: "doctor_name", label: "Doctor" },
  { key: "specialty", label: "Specialty" },
  { key: "department_name", label: "Department" },
];

export default function Doctors() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [specialty, setSpecialty] = useState("");
  const [departments, setDepartments] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ first_name: "", last_name: "", specialty: "", department_id: "" });
  const perPage = 10;

  useEffect(() => { api.get("/departments").then((res) => setDepartments(res.data)); }, []);

  const load = () => {
    api.get("/doctors", { params: { page, per_page: perPage, search: search || undefined, specialty: specialty || undefined } })
      .then((res) => { setItems(res.data.items); setTotal(res.data.total); });
  };

  useEffect(() => { load(); }, [page, search, specialty]);

  const specialties = [...new Set(items.map((i) => i.specialty))];

  const rows = items.map((d) => ({ ...d, doctor_name: `Dr. ${d.first_name} ${d.last_name}` }));

  const submit = async (e) => {
    e.preventDefault();
    if (!form.first_name || !form.last_name || !form.department_id) return;
    await api.post("/doctors", { ...form, department_id: parseInt(form.department_id) });
    setForm({ first_name: "", last_name: "", specialty: "", department_id: "" });
    setOpen(false);
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900">Doctors</h1>
          <p className="text-gray-500">Staff directory, organized by specialty.</p>
        </div>
        <button onClick={() => setOpen(true)} className="glass-action flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm">
          <Plus size={16} /> Add Doctor
        </button>
      </div>

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            value={search}
            onChange={(e) => { setPage(1); setSearch(e.target.value); }}
            placeholder="Search by name or specialty…"
            className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
        <select
          value={specialty}
          onChange={(e) => { setPage(1); setSpecialty(e.target.value); }}
          className="px-3 py-2.5 rounded-xl border border-gray-200 text-sm"
        >
          <option value="">All specialties</option>
          {specialties.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <DataTable columns={COLUMNS} rows={rows} page={page} perPage={perPage} total={total} onPageChange={setPage} resource="doctors" idKey="doctor_id" onChanged={load} />

      <Modal open={open} onClose={() => setOpen(false)} title="Add Doctor">
        <form onSubmit={submit} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input placeholder="First name" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
            <input placeholder="Last name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          </div>
          <input placeholder="Specialty" value={form.specialty} onChange={(e) => setForm({ ...form, specialty: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <select value={form.department_id} onChange={(e) => setForm({ ...form, department_id: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Select department</option>
            {departments.map((d) => <option key={d.department_id} value={d.department_id}>{d.name}</option>)}
          </select>
          <button type="submit" className="glass-action w-full bg-brand-600 hover:bg-brand-700 text-white py-2.5 rounded-lg font-medium text-sm">Save</button>
        </form>
      </Modal>
    </div>
  );
}
