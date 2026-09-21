import { useEffect, useState } from "react";
import api from "../api";
import { Plus, Search } from "lucide-react";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";

const COLUMNS = [
  { key: "patient_name", label: "Patient" },
  { key: "age", label: "Age" },
  { key: "gender", label: "Gender" },
  { key: "city", label: "City" },
  { key: "insurance_name", label: "Insurance" },
  { key: "registration_date", label: "Registered" },
];

export default function Patients() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [insuranceOptions, setInsuranceOptions] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ first_name: "", last_name: "", dob: "", gender: "Male", city: "", insurance_id: "" });
  const perPage = 10;

  useEffect(() => { api.get("/insurance_providers").then((res) => setInsuranceOptions(res.data)); }, []);

  const load = () => {
    api.get("/patients", { params: { page, per_page: perPage, search: search || undefined } })
      .then((res) => { setItems(res.data.items); setTotal(res.data.total); });
  };

  useEffect(() => { load(); }, [page, search]);

  const rows = items.map((p) => ({ ...p, patient_name: `${p.first_name} ${p.last_name}` }));

  const submit = async (e) => {
    e.preventDefault();
    if (!form.first_name || !form.last_name || !form.dob || !form.city) return;
    await api.post("/patients", { ...form, insurance_id: form.insurance_id ? parseInt(form.insurance_id) : null });
    setForm({ first_name: "", last_name: "", dob: "", gender: "Male", city: "", insurance_id: "" });
    setOpen(false);
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900">Patients</h1>
          <p className="text-gray-500">Patient directory and registration.</p>
        </div>
        <button onClick={() => setOpen(true)} className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm">
          <Plus size={16} /> Add Patient
        </button>
      </div>

      <div className="relative max-w-md">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          value={search}
          onChange={(e) => { setPage(1); setSearch(e.target.value); }}
          placeholder="Search by name or city…"
          className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
      </div>

      <DataTable columns={COLUMNS} rows={rows} page={page} perPage={perPage} total={total} onPageChange={setPage} />

      <Modal open={open} onClose={() => setOpen(false)} title="Add Patient">
        <form onSubmit={submit} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input placeholder="First name" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
            <input placeholder="Last name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <input type="date" value={form.dob} onChange={(e) => setForm({ ...form, dob: e.target.value })} className="px-3 py-2 border border-gray-200 rounded-lg text-sm" />
            <select value={form.gender} onChange={(e) => setForm({ ...form, gender: e.target.value })} className="px-3 py-2 border border-gray-200 rounded-lg text-sm">
              <option>Male</option>
              <option>Female</option>
            </select>
          </div>
          <input placeholder="City" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <select value={form.insurance_id} onChange={(e) => setForm({ ...form, insurance_id: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Self-pay (no insurance)</option>
            {insuranceOptions.map((i) => <option key={i.insurance_id} value={i.insurance_id}>{i.provider_name}</option>)}
          </select>
          <button type="submit" className="w-full bg-brand-600 hover:bg-brand-700 text-white py-2.5 rounded-lg font-medium text-sm">Save</button>
        </form>
      </Modal>
    </div>
  );
}
