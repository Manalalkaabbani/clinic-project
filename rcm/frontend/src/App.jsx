import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Bell, Search, UserRound } from "lucide-react";
import Sidebar from "./components/Sidebar";
import RegistrationModal from "./components/RegistrationModal";
import Dashboard from "./pages/Dashboard";
import Departments from "./pages/Departments";
import Doctors from "./pages/Doctors";
import Patients from "./pages/Patients";
import Diagnoses from "./pages/Diagnoses";
import Payments from "./pages/Payments";
import LabTests from "./pages/LabTests";
import Appointments from "./pages/Appointments";

export default function App() {
  const [userName, setUserName] = useState(() => localStorage.getItem("carepath_user_name") || "");
  const [registrationOpen, setRegistrationOpen] = useState(() => !localStorage.getItem("carepath_user_name"));

  const registerUser = (name) => {
    localStorage.setItem("carepath_user_name", name);
    setUserName(name);
    setRegistrationOpen(false);
  };

  return (
    <BrowserRouter>
      <div className="app-shell flex min-h-screen min-w-0 flex-col bg-[#eef3ff] lg:flex-row">
        <Sidebar />
        <main className="app-content min-w-0 flex-1">
          <header className="app-topbar">
            <div className="relative hidden min-w-0 max-w-sm flex-1 sm:block">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input className="app-search" placeholder="Search anything..." aria-label="Search anything" />
            </div>
            <div className="ml-auto flex items-center gap-3">
              <button className="topbar-icon" aria-label="Notifications"><Bell size={17} /></button>
              <div className="hidden text-right sm:block">
                <div className="text-sm font-semibold text-slate-800">{userName || "Guest user"}</div>
                <div className="text-[11px] text-slate-400">Clinic administrator</div>
              </div>
              <div className="topbar-avatar"><UserRound size={16} /></div>
            </div>
          </header>
          <div className="app-page">
            <Routes>
              <Route path="/" element={<Dashboard userName={userName} onChangeName={() => setRegistrationOpen(true)} />} />
              <Route path="/departments" element={<Departments />} />
              <Route path="/doctors" element={<Doctors />} />
              <Route path="/patients" element={<Patients />} />
              <Route path="/diagnoses" element={<Diagnoses />} />
              <Route path="/payments" element={<Payments />} />
              <Route path="/lab-tests" element={<LabTests />} />
              <Route path="/appointments" element={<Appointments />} />
            </Routes>
          </div>
        </main>
      </div>
      <RegistrationModal
        open={registrationOpen}
        onClose={() => setRegistrationOpen(false)}
        onRegister={registerUser}
        initialName={userName}
      />
    </BrowserRouter>
  );
}
