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
    <aside className="flex w-full shrink-0 flex-col bg-[#102A56] text-white lg:min-h-screen lg:w-64">
      <div className="flex items-center gap-2 px-4 py-4 sm:px-6 lg:py-6">
        <div className="w-9 h-9 rounded-xl bg-brand-500 flex items-center justify-center">
          <HeartPulse size={20} className="text-white" />
        </div>
        <div>
          <div className="font-bold text-lg leading-tight">CarePath</div>
          <div className="text-xs text-white/50">Revenue Cycle System</div>
        </div>
      </div>

      <nav className="flex-1 overflow-x-auto px-3 pb-3 lg:mt-4 lg:overflow-visible lg:pb-0">
        <div className="mb-2 hidden px-3 text-xs uppercase tracking-wider text-white/40 lg:block">Menu</div>
        <div className="flex min-w-max gap-1 lg:flex-col lg:space-y-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors lg:gap-3 ${
                  isActive
                    ? "bg-brand-500 text-white shadow-lg shadow-brand-900/30"
                    : "text-white/70 hover:bg-white/10 hover:text-white"
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

      <div className="hidden border-t border-white/10 px-6 py-4 text-xs text-white/40 lg:block">
        CarePath
      </div>
    </aside>
  );
}
