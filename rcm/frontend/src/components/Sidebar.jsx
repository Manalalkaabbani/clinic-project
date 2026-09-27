import { useState } from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, Building2, Stethoscope, Users, ClipboardList,
  CreditCard, FlaskConical, CalendarDays, HeartPulse, PanelLeftClose, PanelLeftOpen,
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
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside className={`app-sidebar flex w-full shrink-0 flex-col overflow-hidden text-white transition-all duration-300 lg:sticky lg:top-0 lg:h-screen ${collapsed ? "lg:w-20" : "lg:w-56"}`}>
      <div className={`relative flex items-center gap-2 px-4 py-4 sm:px-6 lg:py-8 ${collapsed ? "lg:justify-center" : ""}`}>
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/15">
          <HeartPulse size={20} className="text-white" />
        </div>
        {!collapsed && <div className="min-w-0">
          <div className="font-bold text-lg leading-tight">CarePath</div>
          <div className="whitespace-nowrap text-xs text-white/60">Clinic Management</div>
        </div>}
        <button
          type="button"
          onClick={() => setCollapsed((value) => !value)}
          className="absolute right-4 top-1/2 -translate-y-1/2 rounded-lg p-2 text-white/70 transition-colors hover:bg-white/15 hover:text-white"
          aria-label={collapsed ? "Open sidebar" : "Close sidebar"}
          title={collapsed ? "Open sidebar" : "Close sidebar"}
        >
          {collapsed ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />}
        </button>
      </div>

      <nav className="flex-1 overflow-x-auto px-3 pb-3 lg:mt-4 lg:overflow-visible lg:pb-0">
        {!collapsed && <div className="mb-2 hidden px-3 text-[10px] font-bold uppercase tracking-[0.18em] text-white/50 lg:block">Workspace</div>}
        <div className="flex min-w-max gap-1 lg:flex-col lg:space-y-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors lg:gap-3 ${collapsed ? "lg:justify-center" : ""} ${
                  isActive
                    ? "bg-white text-brand-700 shadow-lg shadow-blue-950/20"
                    : "text-white/75 hover:bg-white/15 hover:text-white"
                }`
              }
            >
              <Icon size={18} aria-hidden="true" />
              {!collapsed && <span>{label}</span>}
            </NavLink>
          ))}
        </div>
      </nav>

      {!collapsed && <DataTransfer />}

      {!collapsed && <div className="hidden px-6 py-5 text-[11px] text-white/45 lg:block">
        <div>CarePath</div>
        <div className="mt-1">v1.0 workspace</div>
      </div>}
    </aside>
  );
}
