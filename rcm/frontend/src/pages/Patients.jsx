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
  const [gender, setGender] = useState("");
  const [city, setCity] = useState("");
  const [insuranceId, setInsuranceId] = useState("");
  const [cityOptions, setCityOptions] = useState([]);
  const [insuranceOptions, setInsuranceOptions] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ first_name: "", last_name: "", dob: "", gender: "Male", city: "", insurance_id: "" });
  const perPage = 10;

  useEffect(() => {
    api.get("/insurance_providers").then((res) => setInsuranceOptions(res.data));
    api.get("/patient-options").then((res) => setCityOptions(res.data.cities));
  }, []);

  const load = () => {
    api.get("/patients", {
      params: {
        page,
        per_page: perPage,
        search: search || undefined,
        gender: gender || undefined,
        city: city || undefined,
        insurance_id: insuranceId || undefined,
      },
    })
      .then((res) => { setItems(res.data.items); setTotal(res.data.total); });
  };

  useEffect(() => { load(); }, [page, search, gender, city, insuranceId]);

  const updateFilter = (setter) => (event) => {
    setPage(1);
    setter(event.target.value);
  };

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
        <button onClick={() => setOpen(true)} className="glass-action flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm">
          <Plus size={16} /> Add Patient
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative min-w-64 max-w-md flex-1">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          value={search}
          onChange={(e) => { setPage(1); setSearch(e.target.value); }}
          placeholder="Search by name or city…"
          className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        </div>
        <select value={gender} onChange={updateFilter(setGender)} aria-label="Filter by gender" className="rounded-xl border border-gray-200 px-3 py-2.5 text-sm text-gray-700">
          <option value="">All genders</option>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
        </select>
        <select value={city} onChange={updateFilter(setCity)} aria-label="Filter by city" className="rounded-xl border border-gray-200 px-3 py-2.5 text-sm text-gray-700">
          <option value="">All cities</option>
          {cityOptions.map((option) => <option key={option} value={option}>{option}</option>)}
        </select>
        <select value={insuranceId} onChange={updateFilter(setInsuranceId)} aria-label="Filter by insurance" className="rounded-xl border border-gray-200 px-3 py-2.5 text-sm text-gray-700">
          <option value="">All insurance</option>
          <option value="none">Self-pay</option>
          {insuranceOptions.map((option) => <option key={option.insurance_id} value={option.insurance_id}>{option.provider_name}</option>)}
        </select>
      </div>

      <DataTable columns={COLUMNS} rows={rows} page={page} perPage={perPage} total={total} onPageChange={setPage} resource="patients" idKey="patient_id" onChanged={load} />

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
          <button type="submit" className="glass-action w-full bg-brand-600 hover:bg-brand-700 text-white py-2.5 rounded-lg font-medium text-sm">Save</button>
        </form>
      </Modal>
    </div>
  );
}
