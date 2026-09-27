import { useCallback, useEffect, useMemo, useState } from "react";
import api from "../api";
import KpiCard from "../components/KpiCard";
import {
  DollarSign, ClipboardList, Users, AlertTriangle, RefreshCw, TrendingUp, CheckCircle2, CalendarDays,
} from "lucide-react";
import {
  ResponsiveContainer, XAxis, YAxis, Tooltip, CartesianGrid,
  PieChart, Pie, Cell, BarChart, Bar, Legend, AreaChart, Area,
} from "recharts";

const COLORS = ["#2563EB", "#60A5FA", "#1D4ED8", "#93C5FD", "#3B82F6", "#1E40AF"];
const STATUS_COLORS = { Paid: "#10B981", Pending: "#F59E0B", Unpaid: "#EF4444", Cancelled: "#9CA3AF" };
const DATE_FILTERS = [
  { label: "All time", days: null },
  { label: "Today", days: 0 },
  { label: "Yesterday", days: 1 },
  { label: "Last week", days: 7 },
  { label: "Last month", months: 1 },
  { label: "Last 3 months", months: 3 },
  { label: "Last 6 months", months: 6 },
  { label: "Last year", months: 12 },
];

function getDateRange(filter) {
  if (filter.days === null) return {};
  const end = new Date();
  const start = new Date(end);
  if (filter.months) {
    start.setMonth(start.getMonth() - filter.months);
  } else {
    start.setDate(start.getDate() - filter.days);
  }

  return {
    date_from: start.toISOString().slice(0, 10),
    date_to: end.toISOString().slice(0, 10),
  };
}

export default function Dashboard({ userName, onChangeName }) {
  const [data, setData] = useState(null);
  const [period, setPeriod] = useState(12);
  const [department, setDepartment] = useState("All departments");
  const [status, setStatus] = useState("All statuses");
  const [dateFilter, setDateFilter] = useState("All time");
  const [insurance, setInsurance] = useState("");
  const [insuranceOptions, setInsuranceOptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDashboard = useCallback(() => {
    setLoading(true);
    setError("");
    const selectedDateFilter = DATE_FILTERS.find((option) => option.label === dateFilter);
    const dateRange = getDateRange(selectedDateFilter || DATE_FILTERS[0]);
    api.get("/dashboard/summary", {
      params: {
        ...dateRange,
        insurance_id: insurance || undefined,
        department: department !== "All departments" ? department : undefined,
        payment_status: status !== "All statuses" ? status : undefined,
      },
    })
      .then((res) => setData(res.data))
      .catch(() => setError("Unable to load dashboard data. Check that the API is running."))
      .finally(() => setLoading(false));
  }, [dateFilter, insurance, department, status]);

  useEffect(() => {
    api.get("/insurance_providers").then((res) => setInsuranceOptions(res.data));
  }, []);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);

  const visibleRevenue = useMemo(
    () => data?.monthly_revenue?.slice(-period) || [],
    [data, period],
  );

  const paymentTotals = useMemo(() => {
    const totals = Object.fromEntries((data?.payment_status || []).map((item) => [item.status, item.count]));
    const total = Object.values(totals).reduce((sum, count) => sum + count, 0);
    return { ...totals, total };
  }, [data]);

  const departmentOptions = useMemo(
    () => ["All departments", ...(data?.revenue_by_department || []).map((item) => item.department)],
    [data],
  );

  const statusOptions = useMemo(
    () => ["All statuses", ...(data?.payment_status || []).map((item) => item.status)],
    [data],
  );

  const departmentRevenue = useMemo(
    () => department === "All departments"
      ? (data?.revenue_by_department || [])
      : (data?.revenue_by_department || []).filter((item) => item.department === department),
    [data, department],
  );

  const statusBreakdown = useMemo(
    () => status === "All statuses"
      ? (data?.payment_status || [])
      : (data?.payment_status || []).filter((item) => item.status === status),
    [data, status],
  );

  if (loading && !data) {
    return <div className="text-gray-400 p-8">Loading dashboard…</div>;
  }

  if (!data) {
    return <div className="glass-panel rounded-2xl p-8 text-center text-red-600">{error}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-brand-600">Clinic overview</p>
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-extrabold text-gray-900">Hello, {userName || "there"} 👋</h1>
            <button
              onClick={onChangeName}
              className="text-xs font-semibold text-brand-600 hover:text-brand-700"
            >
              Change name
            </button>
          </div>
          <p className="text-gray-500">Here's what's happening across the clinic.</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="glass-panel flex rounded-xl p-1">
            {[6, 12, 24].map((months) => (
              <button
                key={months}
                onClick={() => setPeriod(months)}
                className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${period === months ? "bg-brand-600 text-white shadow-sm" : "text-gray-500 hover:bg-brand-50 hover:text-brand-700"}`}
              >
                {months}M
              </button>
            ))}
          </div>
          <button onClick={loadDashboard} className="glass-action rounded-xl border border-blue-100 bg-white/50 p-2.5 text-brand-600" title="Refresh dashboard" aria-label="Refresh dashboard">
            <RefreshCw size={17} className={loading ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {error && <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">{error}</div>}

      <div className="glass-panel flex flex-col gap-4 rounded-2xl p-4 lg:flex-row lg:items-end lg:justify-between">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <label className="text-xs font-semibold text-gray-500">
            Date range
            <span className="relative mt-1 block">
              <CalendarDays size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-brand-500" />
              <select value={dateFilter} onChange={(event) => setDateFilter(event.target.value)} className="block w-full min-w-0 rounded-xl border border-blue-100 bg-white/70 py-2 pl-9 pr-3 text-sm font-medium text-gray-800 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100">
                {DATE_FILTERS.map((option) => <option key={option.label}>{option.label}</option>)}
              </select>
            </span>
          </label>
          <label className="text-xs font-semibold text-gray-500">
            Department
            <select value={department} onChange={(event) => setDepartment(event.target.value)} className="mt-1 block w-full min-w-0 rounded-xl border border-blue-100 bg-white/70 px-3 py-2 text-sm font-medium text-gray-800 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100">
              {departmentOptions.map((option) => <option key={option}>{option}</option>)}
            </select>
          </label>
          <label className="text-xs font-semibold text-gray-500">
            Payment status
            <select value={status} onChange={(event) => setStatus(event.target.value)} className="mt-1 block w-full min-w-0 rounded-xl border border-blue-100 bg-white/70 px-3 py-2 text-sm font-medium text-gray-800 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100">
              {statusOptions.map((option) => <option key={option}>{option}</option>)}
            </select>
          </label>
          <label className="text-xs font-semibold text-gray-500">
            Insurance provider
            <select value={insurance} onChange={(event) => setInsurance(event.target.value)} className="mt-1 block w-full min-w-0 rounded-xl border border-blue-100 bg-white/70 px-3 py-2 text-sm font-medium text-gray-800 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100">
              <option value="">All insurers</option>
              {insuranceOptions.map((option) => <option key={option.insurance_id} value={option.insurance_id}>{option.provider_name}</option>)}
            </select>
          </label>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard icon={DollarSign} label="Total Revenue" value={`EGP ${data.total_revenue.toLocaleString()}`} hint="Across all recorded billing" accent />
        <KpiCard icon={ClipboardList} label="Total Diagnoses" value={data.total_diagnoses.toLocaleString()} hint="Clinical records" />
        <KpiCard icon={Users} label="Total Patients" value={data.total_patients.toLocaleString()} hint="Registered patients" />
        <KpiCard icon={AlertTriangle} label="Unpaid Rate" value={`${data.unpaid_rate}%`} hint={`${data.unpaid_count.toLocaleString()} unpaid invoices`} />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="glass-panel rounded-2xl p-4">
          <div className="flex items-center justify-between text-sm text-gray-500"><span>Billing volume</span><TrendingUp size={18} className="text-brand-600" /></div>
          <div className="mt-2 text-xl font-extrabold text-gray-900">{paymentTotals.total.toLocaleString()}</div>
          <div className="mt-1 text-xs text-gray-500">Total invoices tracked</div>
        </div>
        <div className="glass-panel rounded-2xl p-4">
          <div className="flex items-center justify-between text-sm text-gray-500"><span>Paid invoices</span><CheckCircle2 size={18} className="text-emerald-500" /></div>
          <div className="mt-2 text-xl font-extrabold text-gray-900">{(paymentTotals.Paid || 0).toLocaleString()}</div>
          <div className="mt-1 text-xs text-gray-500">{paymentTotals.total ? Math.round((paymentTotals.Paid || 0) / paymentTotals.total * 100) : 0}% of billing volume</div>
        </div>
        <div className="glass-panel rounded-2xl p-4">
          <div className="flex items-center justify-between text-sm text-gray-500"><span>Selected trend</span><span className="font-semibold text-brand-600">{period} months</span></div>
          <div className="mt-2 text-xl font-extrabold text-gray-900">{visibleRevenue.length} data points</div>
          <div className="mt-1 text-xs text-gray-500">Use the period controls above to compare</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass-panel lg:col-span-2 rounded-2xl p-5">
          <div className="mb-4 flex items-start justify-between gap-4">
            <div>
              <h3 className="font-semibold text-gray-800">Revenue trend</h3>
              <p className="mt-1 text-xs text-gray-500">Monthly billed amount over the selected period</p>
            </div>
            <span className="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-semibold text-brand-700">{visibleRevenue.length} months</span>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={visibleRevenue}>
              <defs>
                <linearGradient id="revenueFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563EB" stopOpacity={0.28} />
                  <stop offset="95%" stopColor="#2563EB" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#DBEAFE" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(value) => [`EGP ${Number(value).toLocaleString()}`, "Revenue"]} />
              <Area type="monotone" dataKey="amount" stroke="#2563EB" strokeWidth={3} fill="url(#revenueFill)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-panel rounded-2xl p-5">
          <h3 className="font-semibold text-gray-800 mb-4">Payment Status</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={statusBreakdown}
                dataKey="count"
                nameKey="status"
                innerRadius={55}
                outerRadius={90}
                paddingAngle={2}
              >
                {statusBreakdown.map((entry, i) => (
                  <Cell key={i} fill={STATUS_COLORS[entry.status] || COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [Number(value).toLocaleString(), "Invoices"]} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel rounded-2xl p-5">
          <div className="mb-4">
            <h3 className="font-semibold text-gray-800">Revenue by department</h3>
            <p className="mt-1 text-xs text-gray-500">{department === "All departments" ? "Which departments drive revenue?" : `Focused on ${department}`}</p>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={departmentRevenue} layout="vertical" margin={{ left: 40 }}>
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="department" tick={{ fontSize: 11 }} width={110} />
              <Tooltip formatter={(value) => [`EGP ${Number(value).toLocaleString()}`, "Revenue"]} />
              <Bar dataKey="revenue" fill="#2563EB" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-panel rounded-2xl p-5">
          <div className="mb-4">
            <h3 className="font-semibold text-gray-800">Top diagnoses</h3>
            <p className="mt-1 text-xs text-gray-500">Most frequent clinical records</p>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={data.top_diagnoses}
                dataKey="count"
                nameKey="diagnosis"
                innerRadius={55}
                outerRadius={90}
                paddingAngle={2}
              >
                {data.top_diagnoses.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [Number(value).toLocaleString(), "Diagnoses"]} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="glass-panel rounded-2xl p-5">
          <div className="mb-4">
            <h3 className="font-semibold text-gray-800">Invoice status volume</h3>
            <p className="mt-1 text-xs text-gray-500">A direct view of each invoice status</p>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={statusBreakdown} margin={{ top: 8, right: 10, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#DBEAFE" />
              <XAxis dataKey="status" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip formatter={(value) => [Number(value).toLocaleString(), "Invoices"]} />
              <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                {statusBreakdown.map((entry, i) => <Cell key={entry.status} fill={STATUS_COLORS[entry.status] || COLORS[i % COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-panel rounded-2xl p-5">
          <div className="mb-4">
            <h3 className="font-semibold text-gray-800">Diagnosis volume</h3>
            <p className="mt-1 text-xs text-gray-500">Where clinical demand is concentrated</p>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data.top_diagnoses} layout="vertical" margin={{ left: 35, right: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#DBEAFE" />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="diagnosis" tick={{ fontSize: 10 }} width={125} />
              <Tooltip formatter={(value) => [Number(value).toLocaleString(), "Cases"]} />
              <Bar dataKey="count" fill="#60A5FA" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
