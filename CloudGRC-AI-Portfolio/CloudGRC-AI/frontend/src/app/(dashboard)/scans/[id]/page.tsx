"use client";
import { useQuery } from "@tanstack/react-query";
import { scansAPI } from "@/services/api";
import { ScanDetail, Finding } from "@/types";
import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft, Download, Shield, AlertTriangle,
  CheckCircle, Activity, FileText, Wrench, TrendingUp
} from "lucide-react";
import clsx from "clsx";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { formatDistanceToNow } from "date-fns";

const SEV_ORDER = ["Critical","High","Medium","Low","Info"];
const SEV_COLOURS: Record<string,string> = {
  Critical:"#ff003c", High:"#ff6600", Medium:"#ffaa00", Low:"#00cc66", Info:"#888888"
};
const SEV_BG: Record<string,string> = {
  Critical:"bg-red-900/30 border-red-800",
  High:    "bg-orange-900/30 border-orange-800",
  Medium:  "bg-yellow-900/30 border-yellow-800",
  Low:     "bg-green-900/30 border-green-800",
  Info:    "bg-gray-800 border-gray-700",
};

function SeverityBadge({ sev }: { sev: string }) {
  return (
    <span className={clsx("text-xs px-2 py-0.5 rounded border font-bold", SEV_BG[sev])}
      style={{ color: SEV_COLOURS[sev] }}>{sev}</span>
  );
}

function FindingsTable({ findings }: { findings: Finding[] }) {
  const [sev,  setSev]  = useState("All");
  const [cat,  setCat]  = useState("All");
  const [cloud,setCloud]= useState("All");

  const sevs   = ["All", ...SEV_ORDER.filter(s => findings.some(f => f.severity === s))];
  const cats   = ["All", ...Array.from(new Set(findings.map(f => f.category)))];
  const clouds = ["All", ...Array.from(new Set(findings.map(f => f.cloud)))];

  const filtered = findings.filter(f =>
    (sev   === "All" || f.severity === sev) &&
    (cat   === "All" || f.category === cat) &&
    (cloud === "All" || f.cloud    === cloud)
  );

  return (
    <div className="space-y-3">
      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        {[
          { label: "Severity", value: sev,   set: setSev,   opts: sevs   },
          { label: "Category", value: cat,   set: setCat,   opts: cats   },
          { label: "Cloud",    value: cloud, set: setCloud, opts: clouds },
        ].map(({ label, value, set, opts }) => (
          <select key={label} value={value} onChange={e => set(e.target.value)}
            className="cyber-input w-auto text-xs py-1">
            {opts.map(o => <option key={o}>{o}</option>)}
          </select>
        ))}
        <span className="text-xs text-[#688a8a] self-center ml-1">
          {filtered.length} of {findings.length} findings
        </span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded border border-[#1e3a45]">
        <table className="w-full text-xs">
          <thead className="bg-[#0f2030]">
            <tr className="text-left text-[#688a8a]">
              {["Cloud","Category","Severity","Issue","Resource","ISO 27001","NIST CSF","CIS"].map(h => (
                <th key={h} className="px-3 py-2 font-medium whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1e3a45]">
            {filtered.map((f, i) => (
              <tr key={i} className="hover:bg-[#0f2030] transition-colors">
                <td className="px-3 py-2">
                  <span className="text-[10px] bg-teal/20 text-teal px-1.5 py-0.5 rounded uppercase">{f.cloud}</span>
                </td>
                <td className="px-3 py-2 text-[#8ab0b0]">{f.category}</td>
                <td className="px-3 py-2"><SeverityBadge sev={f.severity} /></td>
                <td className="px-3 py-2 text-white max-w-[200px]">
                  <div title={f.detail} className="truncate">{f.issue}</div>
                  <div className="text-[#688a8a] text-[10px] truncate">{f.resource}</div>
                </td>
                <td className="px-3 py-2 text-[#688a8a] font-mono text-[10px] max-w-[100px] truncate">{f.resource}</td>
                <td className="px-3 py-2 text-[#8ab0b0] max-w-[120px] truncate">{f.frameworks?.ISO27001}</td>
                <td className="px-3 py-2 text-[#8ab0b0] max-w-[120px] truncate">{f.frameworks?.NIST_CSF}</td>
                <td className="px-3 py-2 text-[#8ab0b0] max-w-[100px] truncate">{f.frameworks?.CIS}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function ScanDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [tab, setTab] = useState<"findings"|"executive"|"technical"|"impact"|"remediation">("findings");

  const { data: scan, isLoading } = useQuery<ScanDetail>({
    queryKey: ["scan", id],
    queryFn:  () => scansAPI.get(id).then(r => r.data),
    refetchInterval: (data) => data?.status === "running" || data?.status === "pending" ? 5_000 : false,
  });

  if (isLoading) return (
    <div className="flex items-center justify-center h-64 text-cyber animate-pulse font-mono">
      Loading scan results...
    </div>
  );

  if (!scan) return <div className="text-danger">Scan not found</div>;

  const breakdown = SEV_ORDER.map(s => ({
    name: s,
    count: scan.findings?.filter(f => f.severity === s).length || 0,
  })).filter(d => d.count > 0);

  const TABS = [
    { id: "findings",    label: "Findings",         icon: AlertTriangle },
    { id: "executive",   label: "Executive Summary", icon: FileText },
    { id: "technical",   label: "Technical",         icon: Activity },
    { id: "impact",      label: "Business Impact",   icon: TrendingUp },
    { id: "remediation", label: "Remediation",       icon: Wrench },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Back */}
      <Link href="/scans" className="flex items-center gap-1 text-sm text-[#688a8a] hover:text-cyber transition-colors">
        <ArrowLeft className="w-4 h-4" /> Back to Scans
      </Link>

      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">{scan.org_name}</h1>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            {scan.providers.map(p => (
              <span key={p} className="text-xs bg-teal/20 text-teal px-2 py-0.5 rounded uppercase">{p}</span>
            ))}
            <span className="text-xs text-[#688a8a]">
              {formatDistanceToNow(new Date(scan.created_at), { addSuffix: true })}
            </span>
          </div>
        </div>
        {scan.pdf_url && (
          <a href={scan.pdf_url} target="_blank" rel="noreferrer"
            className="btn-cyber flex items-center gap-2 text-sm">
            <Download className="w-4 h-4" /> Download PDF
          </a>
        )}
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        {[
          { label: "Risk Score",    value: `${scan.risk_score ?? "—"}/100`,        colour: (scan.risk_score||0)>=80?"text-danger":(scan.risk_score||0)>=60?"text-warn":"text-safe" },
          { label: "Compliance",    value: `${scan.compliance_pct ?? "—"}%`,        colour: (scan.compliance_pct||0)>=70?"text-safe":"text-caution" },
          { label: "Total",         value: scan.total_findings,                      colour: "text-white" },
          { label: "Critical",      value: scan.critical_count,                      colour: "text-danger" },
          { label: "High",          value: scan.high_count,                          colour: "text-warn" },
        ].map(({ label, value, colour }) => (
          <div key={label} className="card text-center py-3">
            <p className={clsx("text-xl font-bold", colour)}>{value}</p>
            <p className="text-xs text-[#688a8a] mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {/* Bar Chart */}
      {breakdown.length > 0 && (
        <div className="card">
          <h3 className="text-sm font-semibold text-white mb-3">Findings by Severity</h3>
          <ResponsiveContainer width="100%" height={120}>
            <BarChart data={breakdown} layout="vertical">
              <XAxis type="number" tick={{ fill: "#688a8a", fontSize: 11 }} />
              <YAxis type="category" dataKey="name" tick={{ fill: "#688a8a", fontSize: 11 }} width={65} />
              <Tooltip
                contentStyle={{ background: "#0a1a20", border: "1px solid #2a6b7c", fontSize: 12 }}
                cursor={{ fill: "rgba(42,107,124,0.1)" }}
              />
              <Bar dataKey="count" radius={[0,3,3,0]}>
                {breakdown.map((entry) => (
                  <Cell key={entry.name} fill={SEV_COLOURS[entry.name]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Tabs */}
      <div className="card p-0">
        <div className="flex overflow-x-auto border-b border-[#1e3a45]">
          {TABS.map(({ id: tid, label, icon: Icon }) => (
            <button key={tid} onClick={() => setTab(tid as any)}
              className={clsx(
                "flex items-center gap-1.5 px-4 py-3 text-xs font-medium whitespace-nowrap transition-colors",
                tab === tid
                  ? "text-cyber border-b-2 border-cyber bg-teal/10"
                  : "text-[#688a8a] hover:text-white"
              )}>
              <Icon className="w-3.5 h-3.5" /> {label}
            </button>
          ))}
        </div>

        <div className="p-5">
          {tab === "findings" && (
            scan.findings?.length > 0
              ? <FindingsTable findings={scan.findings} />
              : <p className="text-[#688a8a] text-sm">No findings available yet</p>
          )}
          {tab === "executive"   && <div className="prose prose-invert max-w-none text-sm text-[#c9e8e0] whitespace-pre-wrap leading-7">{scan.ai_report?.executive_summary || "AI report not available"}</div>}
          {tab === "technical"   && <div className="prose prose-invert max-w-none text-sm text-[#c9e8e0] whitespace-pre-wrap leading-7">{scan.ai_report?.technical_findings || "No technical findings report"}</div>}
          {tab === "impact"      && <div className="prose prose-invert max-w-none text-sm text-[#c9e8e0] whitespace-pre-wrap leading-7">{scan.ai_report?.business_impact || "No business impact report"}</div>}
          {tab === "remediation" && <div className="prose prose-invert max-w-none text-sm text-[#c9e8e0] whitespace-pre-wrap leading-7">{scan.ai_report?.remediation_plan || "No remediation plan available"}</div>}
        </div>
      </div>

      {scan.error_message && (
        <div className="card border-danger/40 bg-red-900/20 text-danger text-sm p-4">
          ⚠️ Scan error: {scan.error_message}
        </div>
      )}
    </div>
  );
}
