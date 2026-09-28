import { useEffect, useState } from "react";
import { KeyRound, Pencil, Plus, ShieldCheck, UserRound, Users } from "lucide-react";
import api from "../api";
import Modal from "../components/Modal";

const ROLE_OPTIONS = [
  { value: "admin", label: "Administrator" },
  { value: "staff", label: "Staff" },
  { value: "viewer", label: "Viewer" },
];

const ROLE_DESCRIPTIONS = {
  super_admin: "Platform owner",
  admin: "Manage clinic records and import data",
  staff: "View and add clinic records",
  viewer: "Read-only access",
};

const EMPTY_FORM = {
  display_name: "",
  username: "",
  role: "staff",
  password: "",
  is_active: true,
};

const fieldClass = "mt-1.5 block w-full rounded-lg border border-stone-200 bg-white px-3 py-2.5 text-sm text-slate-800 outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-100 disabled:bg-stone-100";

export default function UserManagement({ currentUser }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get("/auth/users")
      .then(({ data }) => setUsers(data))
      .catch((requestError) => setLoadError(requestError.response?.data?.error || "Could not load user accounts."))
      .finally(() => setLoading(false));
  }, []);

  const openCreate = () => {
    setEditingUser(null);
    setForm(EMPTY_FORM);
    setFormError("");
    setModalOpen(true);
  };

  const openEdit = (user) => {
    setEditingUser(user);
    setForm({
      display_name: user.display_name,
      username: user.username,
      role: user.role,
      password: "",
      is_active: user.is_active,
    });
    setFormError("");
    setModalOpen(true);
  };

  const submit = async (event) => {
    event.preventDefault();
    setFormError("");
    setSaving(true);

    const payload = {
      display_name: form.display_name.trim(),
      username: form.username.trim().toLowerCase(),
      role: form.role,
      is_active: form.is_active,
    };
    if (form.password) payload.password = form.password;

    try {
      const response = editingUser
        ? await api.patch(`/auth/users/${editingUser.user_id}`, payload)
        : await api.post("/auth/users", payload);
      setUsers((items) => editingUser
        ? items.map((user) => user.user_id === response.data.user_id ? response.data : user)
        : [response.data, ...items]);
      setModalOpen(false);
    } catch (requestError) {
      setFormError(requestError.response?.data?.error || "Could not save this account.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2 text-brand-700">
            <ShieldCheck size={18} aria-hidden="true" />
            <p className="text-xs font-bold uppercase tracking-[0.14em]">Platform owner</p>
          </div>
          <h1 className="mt-2 text-2xl font-bold text-slate-900">Users &amp; access</h1>
        </div>
        <button
          type="button"
          onClick={openCreate}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-700"
        >
          <Plus size={17} aria-hidden="true" />
          Add user
        </button>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        {ROLE_OPTIONS.map((role) => (
          <div key={role.value} className="rounded-xl border border-stone-200 bg-white/70 p-4">
            <p className="text-sm font-semibold text-slate-800">{role.label}</p>
            <p className="mt-1 text-xs leading-5 text-slate-500">{ROLE_DESCRIPTIONS[role.value]}</p>
          </div>
        ))}
      </div>

      {loadError && <p role="alert" className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{loadError}</p>}

      <div className="data-card overflow-hidden">
        <div className="flex items-center gap-2 border-b border-stone-100 px-4 py-3 text-sm font-semibold text-slate-700">
          <Users size={17} className="text-brand-600" aria-hidden="true" />
          Accounts <span className="text-xs font-normal text-slate-400">{users.length}</span>
        </div>
        {loading ? (
          <p className="px-4 py-10 text-center text-sm text-slate-400">Loading accounts…</p>
        ) : users.length === 0 ? (
          <p className="px-4 py-10 text-center text-sm text-slate-500">No user accounts yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px] text-sm">
              <thead>
                <tr className="border-b border-stone-100 text-left text-[11px] uppercase text-slate-400">
                  <th className="px-4 py-3 font-semibold">Account</th>
                  <th className="px-4 py-3 font-semibold">Role</th>
                  <th className="px-4 py-3 font-semibold">Status</th>
                  <th className="px-4 py-3 font-semibold">Created</th>
                  <th className="px-4 py-3 text-right font-semibold">Action</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.user_id} className="border-b border-stone-100 last:border-0 hover:bg-brand-50/40">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2.5">
                        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-50 text-brand-700">
                          {user.role === "super_admin" ? <ShieldCheck size={16} /> : <UserRound size={16} />}
                        </span>
                        <span>
                          <span className="block font-semibold text-slate-800">{user.display_name}{user.user_id === currentUser.user_id ? " (you)" : ""}</span>
                          <span className="text-xs text-slate-500">@{user.username}</span>
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-600">{ROLE_OPTIONS.find((role) => role.value === user.role)?.label || ROLE_DESCRIPTIONS[user.role]}</td>
                    <td className="px-4 py-3">
                      <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${user.is_active ? "bg-emerald-100 text-emerald-800" : "bg-stone-100 text-stone-600"}`}>
                        {user.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500">{user.created_at ? new Date(user.created_at).toLocaleDateString() : "—"}</td>
                    <td className="px-4 py-3 text-right">
                      <button
                        type="button"
                        onClick={() => openEdit(user)}
                        className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-brand-700 hover:bg-brand-50"
                        aria-label={`Edit ${user.username}`}
                      >
                        <Pencil size={14} aria-hidden="true" /> Edit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingUser ? "Edit account" : "Add user"}
      >
        <form onSubmit={submit} className="space-y-4">
          <label className="block text-sm font-semibold text-slate-700">
            Full name
            <input
              value={form.display_name}
              onChange={(event) => setForm({ ...form, display_name: event.target.value })}
              maxLength={100}
              required
              className={fieldClass}
            />
          </label>
          <label className="block text-sm font-semibold text-slate-700">
            Username
            <input
              value={form.username}
              onChange={(event) => setForm({ ...form, username: event.target.value.toLowerCase() })}
              minLength={3}
              maxLength={50}
              pattern="[a-z0-9][a-z0-9._-]{2,49}"
              required
              disabled={Boolean(editingUser)}
              className={fieldClass}
            />
          </label>
          <label className="block text-sm font-semibold text-slate-700">
            Role
            <select
              value={form.role === "super_admin" ? "admin" : form.role}
              onChange={(event) => setForm({ ...form, role: event.target.value })}
              disabled={editingUser?.role === "super_admin"}
              className={fieldClass}
            >
              {ROLE_OPTIONS.map((role) => <option key={role.value} value={role.value}>{role.label}</option>)}
            </select>
            {editingUser?.role === "super_admin" && <span className="mt-1 block text-xs font-normal text-slate-500">The platform owner role cannot be changed.</span>}
          </label>
          <label className="block text-sm font-semibold text-slate-700">
            {editingUser ? "Reset password" : "Temporary password"}
            <span className="relative block">
              <KeyRound size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" aria-hidden="true" />
              <input
                type="password"
                value={form.password}
                onChange={(event) => setForm({ ...form, password: event.target.value })}
                minLength={12}
                required={!editingUser}
                autoComplete="new-password"
                placeholder={editingUser ? "Leave blank to keep current password" : "At least 12 characters"}
                className={`${fieldClass} pl-9`}
              />
            </span>
          </label>
          {editingUser && (
            <label className="flex items-center gap-3 rounded-lg border border-stone-200 bg-white px-3 py-3 text-sm font-medium text-slate-700">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(event) => setForm({ ...form, is_active: event.target.checked })}
                disabled={editingUser.role === "super_admin" || editingUser.user_id === currentUser.user_id}
                className="h-4 w-4 accent-brand-600"
              />
              Account active
              {editingUser.user_id === currentUser.user_id && <span className="ml-auto text-xs font-normal text-slate-400">Current account</span>}
            </label>
          )}
          {formError && <p role="alert" className="text-sm text-red-600">{formError}</p>}
          <button type="submit" disabled={saving} className="w-full rounded-lg bg-brand-600 py-2.5 text-sm font-semibold text-white hover:bg-brand-700 disabled:opacity-60">
            {saving ? "Saving…" : editingUser ? "Save changes" : "Create account"}
          </button>
        </form>
      </Modal>
    </section>
  );
}