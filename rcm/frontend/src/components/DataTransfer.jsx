import { useState } from "react";
import { Download, Upload } from "lucide-react";
import api from "../api";
import Modal from "./Modal";

const TABLES = [
  "departments",
  "doctors",
  "insurance_providers",
  "patients",
  "diagnoses",
  "billing",
  "lab_tests",
  "appointments",
];

const TABLE_TEMPLATES = {
  departments: ["name"],
  doctors: ["first_name", "last_name", "specialty", "department_id"],
  insurance_providers: ["provider_name", "coverage_type", "contact_phone"],
  patients: ["first_name", "last_name", "dob", "gender", "city", "insurance_id", "registration_date"],
  diagnoses: ["patient_id", "doctor_id", "diagnosis_code", "description", "severity", "diagnosis_date"],
  billing: ["diagnosis_id", "amount", "payment_status", "payment_method", "billing_date"],
  lab_tests: ["diagnosis_id", "test_type", "result_status", "test_date"],
  appointments: ["patient_id", "doctor_id", "nurse_id", "room_id", "appointment_date", "status"],
};

export default function DataTransfer() {
  const [importOpen, setImportOpen] = useState(false);
  const [table, setTable] = useState(TABLES[0]);
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const handleImport = async (event) => {
    event.preventDefault();
    if (!file) {
      setStatus("Please choose a CSV file first.");
      return;
    }

    const formData = new FormData();
    formData.append("table", table);
    formData.append("file", file);

    try {
      const response = await api.post("/import/csv", formData);
      setStatus(response.data.message);
    } catch (error) {
      setStatus(error.response?.data?.error || "Import failed");
    }
  };

  const closeModal = () => {
    setImportOpen(false);
    setStatus("");
  };

  const handleDownloadTemplate = () => {
    const headers = TABLE_TEMPLATES[table] || [];
    const csvContent = `${headers.join(",")}\n`;
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${table}_template.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <>
      <div className="border-t border-white/10 px-3 pb-4 pt-4">
        <div className="mb-2 px-3 text-xs uppercase tracking-wider text-white/40">Data</div>
        <div className="space-y-2">
          <a
            href="http://localhost:5000/api/export/csv"
            download
            className="flex items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-medium text-white/70 hover:bg-white/10 hover:text-white"
          >
            <Download size={18} /> Export All Data
          </a>
          <button
            onClick={() => setImportOpen(true)}
            className="flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-medium text-white/70 hover:bg-white/10 hover:text-white"
          >
            <Upload size={18} /> Import Data
          </button>
        </div>
      </div>

      <Modal open={importOpen} onClose={closeModal} title="Import CSV">
        <form onSubmit={handleImport} className="space-y-3">
          <select value={table} onChange={(event) => setTable(event.target.value)} className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm">
            {TABLES.map((name) => <option key={name} value={name}>{name}</option>)}
          </select>
          <button type="button" onClick={handleDownloadTemplate} className="flex w-full items-center justify-center gap-2 rounded-lg border border-brand-200 bg-brand-50 px-3 py-2 text-sm font-medium text-brand-700 hover:bg-brand-100">
            <Download size={16} /> Download CSV template
          </button>
          <input type="file" accept=".csv" onChange={(event) => setFile(event.target.files?.[0] || null)} className="w-full text-sm" />
          {status && <p className="text-sm text-gray-600">{status}</p>}
          <button type="submit" className="w-full rounded-lg bg-brand-600 py-2.5 text-sm font-medium text-white hover:bg-brand-700">Upload</button>
        </form>
      </Modal>
    </>
  );
}