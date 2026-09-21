import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, Building2, Stethoscope, Users, ClipboardList,
  CreditCard, FlaskConical, HeartPulse,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/departments", label: "Departments", icon: Building2 },
  { to: "/doctors", label: "Doctors", icon: Stethoscope },
  { to: "/patients", label: "Patients", icon: Users },
  { to: "/diagnoses", label: "Diagnoses", icon: ClipboardList },
  { to: "/payments", label: "Payments", icon: CreditCard },
  { to: "/lab-tests", label: "Lab Tests", icon: FlaskConical },
];

export default function Sidebar() {
  return (
    <aside className="w-64 shrink-0 bg-[#0B3D2E] text-white min-h-screen flex flex-col">
      <div className="flex items-center gap-2 px-6 py-6">
        <div className="w-9 h-9 rounded-xl bg-brand-500 flex items-center justify-center">
          <HeartPulse size={20} className="text-white" />
        </div>
        <div>
          <div className="font-bold text-lg leading-tight">ClinicRCM</div>
          <div className="text-xs text-white/50">Revenue Cycle System</div>
        </div>
      </div>

      <nav className="flex-1 px-3 mt-4 space-y-1">
        <div className="text-xs uppercase tracking-wider text-white/40 px-3 mb-2">Menu</div>
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${
                isActive
                  ? "bg-brand-500 text-white shadow-lg shadow-brand-900/30"
                  : "text-white/70 hover:bg-white/10 hover:text-white"
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-6 py-4 text-xs text-white/40 border-t border-white/10">
        Clinic RCM · Graduation Project
      </div>
    </aside>
  );
}
