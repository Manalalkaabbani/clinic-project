import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, Building2, Stethoscope, Users, ClipboardList,
  CreditCard, FlaskConical, CalendarDays, HeartPulse,
} from "lucide-react";
import DataTransfer from "./DataTransfer";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/departments", label: "Departments", icon: Building2 },
  { to: "/doctors", label: "Doctors", icon: Stethoscope },
  { to: "/patients", label: "Patients", icon: Users },
  { to: "/diagnoses", label: "Diagnoses", icon: ClipboardList },
  { to: "/payments", label: "Payments", icon: CreditCard },
  { to: "/lab-tests", label: "Lab Tests", icon: FlaskConical },
  { to: "/appointments", label: "Appointments", icon: CalendarDays },
];

export default function Sidebar() {
  return (
    <aside className="app-sidebar flex w-full shrink-0 flex-col text-white lg:min-h-screen lg:w-56">
      <div className="flex items-center gap-2 px-4 py-4 sm:px-6 lg:py-8">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/15">
          <HeartPulse size={20} className="text-white" />
        </div>
        <div>
          <div className="font-bold text-lg leading-tight">CarePath</div>
          <div className="text-xs text-white/60">Clinic workspace</div>
        </div>
      </div>

      <nav className="flex-1 overflow-x-auto px-3 pb-3 lg:mt-4 lg:overflow-visible lg:pb-0">
        <div className="mb-2 hidden px-3 text-[10px] font-bold uppercase tracking-[0.18em] text-white/50 lg:block">Workspace</div>
        <div className="flex min-w-max gap-1 lg:flex-col lg:space-y-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors lg:gap-3 ${
                  isActive
                    ? "bg-white text-brand-700 shadow-lg shadow-blue-950/20"
                    : "text-white/75 hover:bg-white/15 hover:text-white"
                }`
              }
            >
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </div>
      </nav>

      <DataTransfer />

      <div className="hidden px-6 py-5 text-[11px] text-white/45 lg:block">
        <div>CarePath</div>
        <div className="mt-1">v1.0 workspace</div>
      </div>
    </aside>
  );
}
