import { useEffect, useState } from "react";
import api from "../api";
import { Plus, Building2, Pencil, Trash2 } from "lucide-react";
import Modal from "../components/Modal";
import ConfirmModal from "../components/ConfirmModal";

export default function Departments() {
  const [departments, setDepartments] = useState([]);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [pendingAction, setPendingAction] = useState(null);
  const [name, setName] = useState("");

  const load = () => api.get("/departments").then((res) => setDepartments(res.data));

  useEffect(() => { load(); }, []);

  const submit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    if (editing) {
      setPendingAction({ type: "edit" });
      return;
    } else {
      await api.post("/departments", { name });
    }
    setName("");
    setEditing(null);
    setOpen(false);
    load();
  };

  const startEdit = (department) => {
    setEditing(department);
    setName(department.name);
    setOpen(true);
  };

  const remove = async (department) => {
    setPendingAction({ type: "delete", department });
  };

  const confirmAction = async () => {
    if (pendingAction.type === "edit") {
      await api.put(`/records/departments/${editing.department_id}`, { name });
      setName("");
      setEditing(null);
      setOpen(false);
    } else {
      await api.delete(`/records/departments/${pendingAction.department.department_id}`);
    }
    setPendingAction(null);
    load();
  };

  const closeModal = () => {
    setOpen(false);
    setEditing(null);
    setName("");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900">Departments</h1>
          <p className="text-gray-500">Clinic departments and specialties.</p>
        </div>
        <button
          onClick={() => setOpen(true)}
          className="glass-action flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm"
        >
          <Plus size={16} /> Add Department
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {departments.map((d) => (
          <div key={d.department_id} className="glass-panel rounded-2xl p-5 flex items-center gap-4">
            <div className="w-11 h-11 rounded-xl bg-brand-50 flex items-center justify-center">
              <Building2 size={20} className="text-brand-600" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="font-semibold text-gray-900">{d.name}</div>
              <div className="text-xs text-gray-400">Department #{d.department_id}</div>
            </div>
            <div className="flex shrink-0 gap-2">
              <button onClick={() => startEdit(d)} className="text-brand-600 hover:text-brand-800" title="Edit department" aria-label="Edit department"><Pencil size={16} /></button>
              <button onClick={() => remove(d)} className="text-red-500 hover:text-red-700" title="Delete department" aria-label="Delete department"><Trash2 size={16} /></button>
            </div>
          </div>
        ))}
      </div>

      <Modal open={open} onClose={closeModal} title={editing ? "Edit Department" : "Add Department"}>
        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-600">Department name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full mt-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              placeholder="e.g. Neurology"
            />
          </div>
          <button type="submit" className="glass-action w-full bg-brand-600 hover:bg-brand-700 text-white py-2.5 rounded-lg font-medium text-sm">
            Save
          </button>
        </form>
      </Modal>
      <ConfirmModal
        open={Boolean(pendingAction)}
        onClose={() => setPendingAction(null)}
        onConfirm={confirmAction}
        title={pendingAction?.type === "delete" ? "Delete department" : "Save edits"}
        message={pendingAction?.type === "delete" ? "Are you sure you want to delete this department?" : "Are you sure you want to save these edits?"}
      />
    </div>
  );
}
