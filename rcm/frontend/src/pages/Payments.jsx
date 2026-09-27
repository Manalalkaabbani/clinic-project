import { useEffect, useState } from "react";
import api from "../api";
import { Plus, DollarSign, CheckCircle2, Clock, AlertTriangle } from "lucide-react";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";
import KpiCard from "../components/KpiCard";

const COLUMNS = [
  { key: "patient_name", label: "Patient" },
  { key: "diagnosis", label: "Diagnosis" },
  { key: "amount", label: "Amount (EGP)" },
  { key: "billing_date", label: "Date" },
  { key: "payment_method", label: "Method" },
  { key: "payment_status", label: "Status", badge: true },
];

export default function Payments() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [status, setStatus] = useState("");
  const [method, setMethod] = useState("");
  const [diagnoses, setDiagnoses] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ diagnosis_id: "", amount: "", payment_status: "Paid", payment_method: "Cash", billing_date: "" });
  const [summary, setSummary] = useState(null);
  const [options, setOptions] = useState({ payment_statuses: [], payment_methods: [] });
  const perPage = 10;

  useEffect(() => {
    api.get("/dashboard/summary").then((res) => setSummary(res.data));
    api.get("/options").then((res) => setOptions(res.data));
    api.get("/diagnoses", { params: { per_page: 200 } }).then((res) => setDiagnoses(res.data.items));
  }, []);

  const load = () => {
    api.get("/billing", { params: { page, per_page: perPage, status: status || undefined, method: method || undefined } })
      .then((res) => { setItems(res.data.items); setTotal(res.data.total); });
  };

  useEffect(() => { load(); }, [page, status, method]);

  const submit = async (e) => {
    e.preventDefault();
    if (!form.diagnosis_id || !form.amount) return;
    await api.post("/billing", { ...form, diagnosis_id: parseInt(form.diagnosis_id), amount: parseFloat(form.amount), billing_date: form.billing_date || undefined });
    setForm({ diagnosis_id: "", amount: "", payment_status: "Paid", payment_method: "Cash", billing_date: "" });
    setOpen(false);
    load();
  };

  const statusCounts = summary?.payment_status.reduce((acc, s) => ({ ...acc, [s.status]: s.count }), {}) || {};

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900">Payments</h1>
          <p className="text-gray-500">Billing records, payment status, and collections.</p>
        </div>
        <button onClick={() => setOpen(true)} className="glass-action flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm">
          <Plus size={16} /> Add Billing Entry
        </button>
      </div>

      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard icon={DollarSign} label="Total Billed" value={`EGP ${summary.total_revenue.toLocaleString()}`} accent />
          <KpiCard icon={CheckCircle2} label="Paid Bills" value={(statusCounts.Paid || 0).toLocaleString()} />
          <KpiCard icon={Clock} label="Pending Bills" value={(statusCounts.Pending || 0).toLocaleString()} />
          <KpiCard icon={AlertTriangle} label="Unpaid Bills" value={(statusCounts.Unpaid || 0).toLocaleString()} />
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        <select value={status} onChange={(e) => { setPage(1); setStatus(e.target.value); }} className="px-3 py-2.5 rounded-xl border border-gray-200 text-sm">
          <option value="">All statuses</option>
          {options.payment_statuses.map((value) => <option key={value}>{value}</option>)}
        </select>
        <select value={method} onChange={(e) => { setPage(1); setMethod(e.target.value); }} className="px-3 py-2.5 rounded-xl border border-gray-200 text-sm">
          <option value="">All methods</option>
          {options.payment_methods.map((value) => <option key={value}>{value}</option>)}
        </select>
      </div>

      <DataTable columns={COLUMNS} rows={items} page={page} perPage={perPage} total={total} onPageChange={setPage} resource="billing" idKey="billing_id" onChanged={load} />

      <Modal open={open} onClose={() => setOpen(false)} title="Add Billing Entry">
        <form onSubmit={submit} className="space-y-3">
          <select value={form.diagnosis_id} onChange={(e) => setForm({ ...form, diagnosis_id: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Select diagnosis</option>
            {diagnoses.map((d) => <option key={d.diagnosis_id} value={d.diagnosis_id}>{d.description} — {d.patient_name}</option>)}
          </select>
          <input type="number" step="0.01" placeholder="Amount (EGP)" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <div className="grid grid-cols-2 gap-3">
            <select value={form.payment_status} onChange={(e) => setForm({ ...form, payment_status: e.target.value })} className="px-3 py-2 border border-gray-200 rounded-lg text-sm">
              {options.payment_statuses.map((value) => <option key={value}>{value}</option>)}
            </select>
            <select value={form.payment_method} onChange={(e) => setForm({ ...form, payment_method: e.target.value })} className="px-3 py-2 border border-gray-200 rounded-lg text-sm">
              {options.payment_methods.map((value) => <option key={value}>{value}</option>)}
            </select>
          </div>
          <input type="date" value={form.billing_date} onChange={(e) => setForm({ ...form, billing_date: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <button type="submit" className="glass-action w-full bg-brand-600 hover:bg-brand-700 text-white py-2.5 rounded-lg font-medium text-sm">Save</button>
        </form>
      </Modal>
    </div>
  );
}
