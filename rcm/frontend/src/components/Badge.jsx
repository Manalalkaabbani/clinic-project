const COLORS = {
  Paid: "bg-green-100 text-green-700",
  Normal: "bg-green-100 text-green-700",
  Mild: "bg-green-100 text-green-700",
  Overdue: "bg-red-100 text-red-700",
  Abnormal: "bg-red-100 text-red-700",
  Severe: "bg-red-100 text-red-700",
  Pending: "bg-yellow-100 text-yellow-700",
  Moderate: "bg-yellow-100 text-yellow-700",
};

export default function Badge({ text }) {
  const cls = COLORS[text] || "bg-gray-100 text-gray-700";
  return <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${cls}`}>{text}</span>;
}
