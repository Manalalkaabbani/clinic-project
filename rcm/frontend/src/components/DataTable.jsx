import Badge from "./Badge";
import { Pencil, Trash2 } from "lucide-react";
import { useState } from "react";
import api from "../api";
import Modal from "./Modal";
import ConfirmModal from "./ConfirmModal";

const FIELD_OPTIONS = {
  gender: ["Male", "Female"],
  severity: ["Mild", "Moderate", "Severe"],
  payment_status: ["Paid", "Pending", "Overdue"],
  payment_method: ["Cash", "Card", "Insurance"],
  result_status: ["Normal", "Abnormal", "Pending"],
  test_type: ["Blood Panel", "X-Ray", "MRI", "Urine Test", "ECG"],
  status: ["Attended", "No-show", "Scheduled", "Cancelled"],
};

export default function DataTable({ columns, rows, page, perPage, total, onPageChange, resource, idKey, onChanged }) {
  const totalPages = Math.max(1, Math.ceil(total / perPage));
  const [editingRow, setEditingRow] = useState(null);
  const [editFields, setEditFields] = useState({});
  const [error, setError] = useState("");
  const [pendingAction, setPendingAction] = useState(null);

  const startEdit = (row) => {
    setEditingRow(row);
    setEditFields(row);
    setError("");
  };

  const saveEdit = async (event) => {
    event.preventDefault();
    setPendingAction({ type: "edit" });
  };

  const confirmAction = async () => {
    try {
      if (pendingAction.type === "edit") {
        await api.put(`/records/${resource}/${editingRow[idKey]}`, editFields);
        setEditingRow(null);
      } else {
        await api.delete(`/records/${resource}/${pendingAction.row[idKey]}`);
      }
      setPendingAction(null);
      onChanged();
    } catch (requestError) {
      setError(requestError.response?.data?.error || "Update failed");
    }
  };

  const deleteRow = async (row) => {
    setPendingAction({ type: "delete", row });
  };

  return (
    <div className="glass-panel rounded-2xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-400 text-xs uppercase tracking-wider border-b border-gray-100">
              {columns.map((c) => (
                <th key={c.key} className="px-4 py-3 font-semibold">{c.label}</th>
              ))}
              <th className="px-4 py-3 text-right font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr>
                <td colSpan={columns.length + 1} className="px-4 py-8 text-center text-gray-400">
                  No results match your filters.
                </td>
              </tr>
            )}
            {rows.map((row, i) => (
              <tr key={i} className="border-b border-blue-50/80 hover:bg-blue-50/50 transition-colors">
                {columns.map((c) => (
                  <td key={c.key} className="px-4 py-3 text-gray-700">
                    {c.badge ? <Badge text={row[c.key]} /> : row[c.key]}
                  </td>
                ))}
                <td className="whitespace-nowrap px-4 py-3 text-right">
                  <button onClick={() => startEdit(row)} className="mr-2 text-brand-600 hover:text-brand-800" title="Edit record" aria-label="Edit record"><Pencil size={16} /></button>
                  <button onClick={() => deleteRow(row)} className="text-red-500 hover:text-red-700" title="Delete record" aria-label="Delete record"><Trash2 size={16} /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal open={Boolean(editingRow)} onClose={() => setEditingRow(null)} title="Edit record">
        <form onSubmit={saveEdit} className="space-y-3">
          <div className="max-h-96 overflow-y-auto rounded-lg border border-gray-200">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs uppercase tracking-wider text-gray-500">
                  <th className="px-3 py-2">Field</th>
                  <th className="px-3 py-2">Value</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(editFields).map(([key, value]) => (
                  <tr key={key} className="border-b border-gray-100 last:border-0">
                    <td className="px-3 py-2 font-medium text-gray-600">{key}</td>
                    <td className="px-3 py-2">
                      {FIELD_OPTIONS[key] ? (
                        <select
                          value={value ?? ""}
                          onChange={(event) => setEditFields({ ...editFields, [key]: event.target.value })}
                          className="w-full rounded border border-gray-200 px-2 py-1 text-sm"
                        >
                          {FIELD_OPTIONS[key].map((option) => <option key={option}>{option}</option>)}
                        </select>
                      ) : (
                        <input
                          value={value ?? ""}
                          onChange={(event) => setEditFields({ ...editFields, [key]: event.target.value })}
                          disabled={key === idKey}
                          className="w-full rounded border border-gray-200 px-2 py-1 text-sm disabled:bg-gray-100 disabled:text-gray-400"
                        />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button type="submit" className="w-full rounded-lg bg-brand-600 py-2.5 text-sm font-medium text-white hover:bg-brand-700">Save changes</button>
        </form>
      </Modal>

      <ConfirmModal
        open={Boolean(pendingAction)}
        onClose={() => setPendingAction(null)}
        onConfirm={confirmAction}
        title={pendingAction?.type === "delete" ? "Delete record" : "Save edits"}
        message={pendingAction?.type === "delete" ? "Are you sure you want to delete this record?" : "Are you sure you want to save these edits?"}
      />

      <div className="flex items-center justify-between px-4 py-3 border-t border-gray-100 text-sm text-gray-500">
        <span>
          Showing {rows.length === 0 ? 0 : (page - 1) * perPage + 1}-{(page - 1) * perPage + rows.length} of {total.toLocaleString()}
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => onPageChange(page - 1)}
            disabled={page <= 1}
            className="glass-action px-3 py-1.5 rounded-lg border border-blue-100 disabled:opacity-40 hover:bg-blue-50"
          >
            Prev
          </button>
          <span>Page {page} of {totalPages}</span>
          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="glass-action px-3 py-1.5 rounded-lg border border-blue-100 disabled:opacity-40 hover:bg-blue-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
