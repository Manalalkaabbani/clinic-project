import { useEffect, useState } from "react";
import api from "../api";
import { Plus } from "lucide-react";
import DataTable from "../components/DataTable";
import Modal from "../components/Modal";

const COLUMNS = [
  { key: "patient_name", label: "Patient" },
  { key: "diagnosis", label: "Diagnosis" },
  { key: "test_type", label: "Test Type" },
  { key: "test_date", label: "Date" },
  { key: "result_status", label: "Result", badge: true },
];

const TEST_TYPES = ["Blood Panel", "X-Ray", "MRI", "Urine Test", "ECG"];

export default function LabTests() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [testType, setTestType] = useState("");
  const [result, setResult] = useState("");
  const [diagnoses, setDiagnoses] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ diagnosis_id: "", test_type: "Blood Panel", result_status: "Pending", test_date: "" });
  const perPage = 10;

  useEffect(() => { api.get("/diagnoses", { params: { per_page: 200 } }).then((res) => setDiagnoses(res.data.items)); }, []);

  const load = () => {
    api.get("/lab_tests", { params: { page, per_page: perPage, test_type: testType || undefined, result_status: result || undefined } })
      .then((res) => { setItems(res.data.items); setTotal(res.data.total); });
  };

  useEffect(() => { load(); }, [page, testType, result]);

  const submit = async (e) => {
    e.preventDefault();
    if (!form.diagnosis_id) return;
    await api.post("/lab_tests", { ...form, diagnosis_id: parseInt(form.diagnosis_id), test_date: form.test_date || undefined });
    setForm({ diagnosis_id: "", test_type: "Blood Panel", result_status: "Pending", test_date: "" });
    setOpen(false);
    load();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900">Lab Tests</h1>
          <p className="text-gray-500">Requested services and their results.</p>
        </div>
        <button onClick={() => setOpen(true)} className="glass-action flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm">
          <Plus size={16} /> Add Lab Test
        </button>
      </div>

      <div className="flex flex-wrap gap-3">
        <select value={testType} onChange={(e) => { setPage(1); setTestType(e.target.value); }} className="px-3 py-2.5 rounded-xl border border-gray-200 text-sm">
          <option value="">All test types</option>
          {TEST_TYPES.map((t) => <option key={t}>{t}</option>)}
        </select>
        <select value={result} onChange={(e) => { setPage(1); setResult(e.target.value); }} className="px-3 py-2.5 rounded-xl border border-gray-200 text-sm">
          <option value="">All results</option>
          <option>Normal</option>
          <option>Abnormal</option>
          <option>Pending</option>
        </select>
      </div>

      <DataTable columns={COLUMNS} rows={items} page={page} perPage={perPage} total={total} onPageChange={setPage} resource="lab_tests" idKey="lab_test_id" onChanged={load} />

      <Modal open={open} onClose={() => setOpen(false)} title="Add Lab Test">
        <form onSubmit={submit} className="space-y-3">
          <select value={form.diagnosis_id} onChange={(e) => setForm({ ...form, diagnosis_id: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option value="">Select diagnosis</option>
            {diagnoses.map((d) => <option key={d.diagnosis_id} value={d.diagnosis_id}>{d.description} — {d.patient_name}</option>)}
          </select>
          <select value={form.test_type} onChange={(e) => setForm({ ...form, test_type: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            {TEST_TYPES.map((t) => <option key={t}>{t}</option>)}
          </select>
          <select value={form.result_status} onChange={(e) => setForm({ ...form, result_status: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm">
            <option>Normal</option>
            <option>Abnormal</option>
            <option>Pending</option>
          </select>
          <input type="date" value={form.test_date} onChange={(e) => setForm({ ...form, test_date: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
          <button type="submit" className="glass-action w-full bg-brand-600 hover:bg-brand-700 text-white py-2.5 rounded-lg font-medium text-sm">Save</button>
        </form>
      </Modal>
    </div>
  );
}
