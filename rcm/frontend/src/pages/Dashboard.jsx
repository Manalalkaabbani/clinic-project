import { useEffect, useState } from "react";
import api from "../api";
import KpiCard from "../components/KpiCard";
import {
  DollarSign, ClipboardList, Users, AlertTriangle,
} from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid,
  PieChart, Pie, Cell, BarChart, Bar, Legend,
} from "recharts";

const COLORS = ["#10B981", "#F59E0B", "#EF4444", "#6366F1", "#06B6D4", "#EC4899"];
const STATUS_COLORS = { Paid: "#10B981", Pending: "#F59E0B", Overdue: "#EF4444" };

export default function Dashboard() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get("/dashboard/summary").then((res) => setData(res.data));
  }, []);

  if (!data) {
    return <div className="text-gray-400 p-8">Loading dashboard…</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900">Hello, Manal 👋</h1>
        <p className="text-gray-500">Here's what's happening across the clinic.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard icon={DollarSign} label="Total Revenue" value={`EGP ${data.total_revenue.toLocaleString()}`} accent />
        <KpiCard icon={ClipboardList} label="Total Diagnoses" value={data.total_diagnoses.toLocaleString()} />
        <KpiCard icon={Users} label="Total Patients" value={data.total_patients.toLocaleString()} />
        <KpiCard icon={AlertTriangle} label="Overdue Rate" value={`${data.overdue_rate}%`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h3 className="font-semibold text-gray-800 mb-4">Monthly Revenue Trend</h3>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={data.monthly_revenue}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
              <XAxis dataKey="month" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="amount" stroke="#10B981" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h3 className="font-semibold text-gray-800 mb-4">Payment Status</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={data.payment_status} dataKey="count" nameKey="status" innerRadius={55} outerRadius={90} paddingAngle={2}>
                {data.payment_status.map((entry, i) => (
                  <Cell key={i} fill={STATUS_COLORS[entry.status] || COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h3 className="font-semibold text-gray-800 mb-4">Revenue by Department</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.revenue_by_department} layout="vertical" margin={{ left: 40 }}>
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="department" tick={{ fontSize: 11 }} width={110} />
              <Tooltip />
              <Bar dataKey="revenue" fill="#10B981" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
          <h3 className="font-semibold text-gray-800 mb-4">Top Diagnoses</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie data={data.top_diagnoses} dataKey="count" nameKey="diagnosis" innerRadius={55} outerRadius={90} paddingAngle={2}>
                {data.top_diagnoses.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
