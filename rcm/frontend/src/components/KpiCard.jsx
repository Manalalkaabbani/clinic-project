export default function KpiCard({ icon: Icon, label, value, accent = false }) {
  return (
    <div
      className={`rounded-2xl p-5 flex flex-col gap-3 shadow-sm border ${
        accent
          ? "bg-gradient-to-br from-brand-600 to-brand-700 text-white border-transparent"
          : "bg-white border-gray-100 text-gray-900"
      }`}
    >
      <div className="flex items-center gap-2">
        <div className={`w-9 h-9 rounded-full flex items-center justify-center ${accent ? "bg-white/20" : "bg-brand-50"}`}>
          <Icon size={18} className={accent ? "text-white" : "text-brand-600"} />
        </div>
        <span className={`text-sm font-medium ${accent ? "text-white/90" : "text-gray-500"}`}>{label}</span>
      </div>
      <div className="text-2xl font-extrabold">{value}</div>
    </div>
  );
}
