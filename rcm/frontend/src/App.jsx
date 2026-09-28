import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Bell, LogOut, Search, UserRound } from "lucide-react";
import Sidebar from "./components/Sidebar";
import AccessGate from "./components/AccessGate";
import UserManagement from "./pages/UserManagement";
import Dashboard from "./pages/Dashboard";
import Departments from "./pages/Departments";
import Doctors from "./pages/Doctors";
import Patients from "./pages/Patients";
import Diagnoses from "./pages/Diagnoses";
import Payments from "./pages/Payments";
import LabTests from "./pages/LabTests";
import Appointments from "./pages/Appointments";
import api from "./api";

export default function App() {
  const [authSession, setAuthSession] = useState(null);
  const [authError, setAuthError] = useState("");
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    api.get("/auth/session")
      .then(({ data }) => setAuthSession(data))
      .catch(() => setAuthError("The account service is unavailable. Make sure the backend is running."))
      .finally(() => setCheckingSession(false));
  }, []);

  const signOut = async () => {
    try {
      await api.post("/auth/logout");
    } finally {
      setAuthSession({ setup_required: false, user: null });
    }
  };

  if (checkingSession) {
    return <div className="flex min-h-screen items-center justify-center bg-canvas text-sm text-slate-500">Checking secure access…</div>;
  }

  if (authError) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-canvas px-4">
        <div className="max-w-md rounded-2xl border border-white bg-ivory p-7 text-center shadow-xl">
          <h1 className="text-xl font-bold text-slate-900">CarePath is unavailable</h1>
          <p className="mt-2 text-sm text-slate-500">{authError}</p>
          <button onClick={() => window.location.reload()} className="mt-5 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-700">Retry</button>
        </div>
      </main>
    );
  }

  if (!authSession?.user) {
    return (
      <AccessGate
        setupRequired={Boolean(authSession?.setup_required)}
        onAuthenticated={(user) => setAuthSession({ setup_required: false, user })}
      />
    );
  }

  const roleLabel = {
    super_admin: "Platform owner",
    admin: "Administrator",
    staff: "Staff",
    viewer: "Viewer",
  }[authSession.user.role] || "User";

  return (
    <BrowserRouter>
      <div className="app-shell flex min-h-screen min-w-0 flex-col bg-canvas lg:flex-row">
        <Sidebar
          isSuperAdmin={authSession.user.role === "super_admin"}
          canImport={authSession.user.role === "super_admin" || authSession.user.role === "admin"}
        />
        <main className="app-content min-w-0 flex-1">
          <header className="app-topbar">
            <div className="relative hidden min-w-0 max-w-sm flex-1 sm:block">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input className="app-search" placeholder="Search anything..." aria-label="Search anything" />
            </div>
            <div className="ml-auto flex items-center gap-3">
              <button className="topbar-icon" aria-label="Notifications"><Bell size={17} /></button>
              <div className="hidden text-right sm:block">
                <div className="text-sm font-semibold text-slate-800">{authSession.user.display_name}</div>
                <div className="text-[11px] text-slate-400">{roleLabel}</div>
              </div>
              <div className="topbar-avatar"><UserRound size={16} /></div>
              <button
                type="button"
                onClick={signOut}
                className="topbar-icon"
                aria-label="Sign out"
                title="Sign out"
              >
                <LogOut size={17} />
              </button>
            </div>
          </header>
          <div className="app-page">
            <Routes>
              <Route path="/" element={<Dashboard userName={authSession.user.display_name} />} />
              <Route path="/departments" element={<Departments />} />
              <Route path="/doctors" element={<Doctors />} />
              <Route path="/patients" element={<Patients />} />
              <Route path="/diagnoses" element={<Diagnoses />} />
              <Route path="/payments" element={<Payments />} />
              <Route path="/lab-tests" element={<LabTests />} />
              <Route path="/appointments" element={<Appointments />} />
              <Route
                path="/admin/users"
                element={authSession.user.role === "super_admin" ? <UserManagement currentUser={authSession.user} /> : <Navigate to="/" replace />}
              />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}
