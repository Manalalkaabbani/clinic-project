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
];

export default function DataTransfer() {
  const [importOpen, setImportOpen] = useState(false);
  const [table, setTable] = useState(TABLES[0]);
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const handleImport = async (event) => {
    event.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("table", table);
    formData.append("file", file);

    try {
      const response = await api.post("/import/csv", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatus(response.data.message);
    } catch (error) {
      setStatus(error.response?.data?.error || "Import failed");
    }
  };

  const closeModal = () => {
    setImportOpen(false);
    setStatus("");
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
          <input type="file" accept=".csv" onChange={(event) => setFile(event.target.files?.[0] || null)} className="w-full text-sm" />
          {status && <p className="text-sm text-gray-600">{status}</p>}
          <button type="submit" className="w-full rounded-lg bg-brand-600 py-2.5 text-sm font-medium text-white hover:bg-brand-700">Upload</button>
        </form>
      </Modal>
    </>
  );
}