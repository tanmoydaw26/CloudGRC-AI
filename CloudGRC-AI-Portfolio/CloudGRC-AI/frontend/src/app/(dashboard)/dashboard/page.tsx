"use client";
import { useQuery } from "@tanstack/react-query";
import { dashboardAPI, scansAPI } from "@/services/api";
import { Shield, AlertTriangle, CheckCircle, TrendingUp, Clock, Zap } from "lucide-react";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { RadialBarChart, RadialBar, ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from "recharts";
import { DashboardStats, Scan } from "@/types";
import clsx from "clsx";
import { useAuthStore } from "@/store/authStore";

const SEV_COLOURS: Record<string, string> = {
  Critical: "#ff003c", High: "#ff6600", Medium: "#ffaa00", Low: "#00cc66"
};

function RiskGauge({ score }: { score: number }) {
  const colour = score >= 80 ? "#ff003c" : score >= 60 ? "#ff6600" : score >= 30 ? "#ffaa00" : "#00cc66";
  return (
    <div className="relative h-40 flex items-center justify-center">
      <ResponsiveContainer width="100%" height={160}>
        <RadialBarChart cx="50%" cy="80%" innerRadius="60%" outerRadius="90%"
          startAngle={180} endAngle={0} data={[{ value: score, fill: colour }]}>
          <RadialBar dataKey="value" cornerRadius={4} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="absolute bottom-4 text-center">
        <p className="text-3xl font-bold" style={{ color: colour }}>{score}</p>
        <p className="text-xs text-[#688a8a]">Risk Score</p>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    completed: "bg-green-900/40 text-safe",
    running:   "bg-teal/20 text-cyber animate-pulse",
    pending:   "bg-gray-800 text-gray-400",
    failed:    "bg-red-900/40 text-danger",
  };
  return <span className={clsx("text-xs px-2 py-0.5 rounded-full font-medium", map[status])}>{status}</span>;
}

export default function DashboardPage() {
  const { user } = useAuthStore();

  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey: ["dashboard"],
    queryFn:  () => dashboardAPI.stats().then(r => r.data),
  });

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-cyber animate-pulse font-mono">Loading dashboard...</div>
    </div>
  );

  const t = stats?.totals;
  const sevData = [
    { name: "Critical", value: t?.total_critical || 0 },
    { name: "High",     value: t?.total_high || 0 },
  ].filter(d => d.value > 0);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-[#688a8a]">Welcome back, {user?.full_name}</p>
        </div>
        <Link href="/scans" className="btn-cyber text-sm px-4 py-2 flex items-center gap-2">
          <Zap className="w-4 h-4" /> New Scan
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Total Scans",    value: t?.total_scans,    icon: Shield,        colour: "text-cyber" },
          { label: "Avg Risk Score", value: `${t?.avg_risk_score}/100`, icon: TrendingUp,  colour: "text-warn" },
          { label: "Avg Compliance", value: `${t?.avg_compliance}%`,    icon: CheckCircle, colour: "text-safe" },
          { label: "Total Findings", value: t?.total_findings,  icon: AlertTriangle, colour: "text-caution" },
        ].map(({ label, value, icon: Icon, colour }) => (
          <div key={label} className="card">
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs text-[#688a8a]">{label}</p>
              <Icon className={clsx("w-4 h-4", colour)} />
            </div>
            <p className={clsx("text-2xl font-bold", colour)}>{value ?? 0}</p>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid lg:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="text-sm font-semibold text-white mb-2">Overall Risk Score</h3>
          <RiskGauge score={t?.avg_risk_score || 0} />
          <p className="text-center text-xs text-[#688a8a] mt-1">Average across all scans</p>
        </div>

        <div className="card">
          <h3 className="text-sm font-semibold text-white mb-4">Critical & High Findings</h3>
          {sevData.length > 0 ? (
            <ResponsiveContainer width="100%" height={160}>
              <PieChart>
                <Pie data={sevData} cx="50%" cy="50%" outerRadius={60}
                  dataKey="value" label={({ name, value }) => `${name}: ${value}`}
                  labelLine={false}>
                  {sevData.map((entry) => (
                    <Cell key={entry.name} fill={SEV_COLOURS[entry.name]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#0a1a20", border: "1px solid #2a6b7c" }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-40 flex items-center justify-center text-[#688a8a] text-sm">
              No critical findings — run a scan to see results
            </div>
          )}
        </div>
      </div>

      {/* Recent Scans */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-white">Recent Scans</h3>
          <Link href="/scans" className="text-xs text-cyber hover:underline">View all</Link>
        </div>
        {stats?.recent_scans && stats.recent_scans.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-[#688a8a] text-xs border-b border-[#1e3a45]">
                  <th className="pb-2 pr-4">Organisation</th>
                  <th className="pb-2 pr-4">Providers</th>
                  <th className="pb-2 pr-4">Status</th>
                  <th className="pb-2 pr-4">Risk</th>
                  <th className="pb-2">Started</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1e3a45]">
                {stats.recent_scans.map((scan: Scan) => (
                  <tr key={scan.id} className="hover:bg-[#0f2030]">
                    <td className="py-2 pr-4">
                      <Link href={`/scans/${scan.id}`} className="text-cyber hover:underline">
                        {scan.org_name}
                      </Link>
                    </td>
                    <td className="py-2 pr-4">
                      <div className="flex gap-1">
                        {scan.providers.map(p => (
                          <span key={p} className="text-[10px] bg-teal/20 text-teal px-1.5 py-0.5 rounded uppercase">{p}</span>
                        ))}
                      </div>
                    </td>
                    <td className="py-2 pr-4"><StatusBadge status={scan.status} /></td>
                    <td className="py-2 pr-4">
                      <span className={clsx("font-bold",
                        (scan.risk_score || 0) >= 80 ? "text-danger" :
                        (scan.risk_score || 0) >= 60 ? "text-warn" : "text-safe"
                      )}>{scan.risk_score ?? "—"}</span>
                    </td>
                    <td className="py-2 text-[#688a8a] text-xs">
                      <Clock className="inline w-3 h-3 mr-1" />
                      {formatDistanceToNow(new Date(scan.created_at), { addSuffix: true })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-10 text-[#688a8a]">
            <Shield className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p className="text-sm">No scans yet</p>
            <Link href="/scans" className="text-cyber text-sm hover:underline">Run your first scan →</Link>
          </div>
        )}
      </div>
    </div>
  );
}
