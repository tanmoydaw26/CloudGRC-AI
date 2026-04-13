"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { scansAPI, credentialsAPI } from "@/services/api";
import { Scan, Credential } from "@/types";
import Link from "next/link";
import { formatDistanceToNow } from "date-fns";
import { Zap, Search, Trash2, Download, Loader2, X, ChevronRight } from "lucide-react";
import toast from "react-hot-toast";
import clsx from "clsx";

const SEV_COLOURS: Record<string, string> = {
  Critical: "text-danger", High: "text-warn", Medium: "text-caution", Low: "text-safe"
};

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    completed: "bg-green-900/40 text-safe border border-green-800",
    running:   "bg-teal/20 text-cyber border border-teal animate-pulse",
    pending:   "bg-gray-800 text-gray-400 border border-gray-700",
    failed:    "bg-red-900/40 text-danger border border-red-900",
  };
  return <span className={clsx("text-xs px-2 py-0.5 rounded-full font-medium", map[status])}>{status}</span>;
}

function NewScanModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [form, setForm] = useState({
    org_name: "", providers: [] as string[], credential_id: "", use_mock: false
  });

  const { data: creds } = useQuery<Credential[]>({
    queryKey: ["credentials"],
    queryFn:  () => credentialsAPI.list().then(r => r.data),
  });

  const mutation = useMutation({
    mutationFn: () => scansAPI.create({
      org_name:      form.org_name,
      providers:     form.providers,
      credential_id: form.credential_id || null,
      use_mock:      form.use_mock,
    }),
    onSuccess: () => {
      toast.success("Scan triggered — results in ~60 seconds");
      qc.invalidateQueries({ queryKey: ["scans"] });
      qc.invalidateQueries({ queryKey: ["dashboard"] });
      onClose();
    },
    onError: (err: any) => toast.error(err.response?.data?.detail || "Scan failed to start"),
  });

  const toggleProvider = (p: string) =>
    setForm(f => ({
      ...f,
      providers: f.providers.includes(p) ? f.providers.filter(x => x !== p) : [...f.providers, p],
    }));

  const PROVIDERS = [
    { id: "aws",   label: "AWS",   colour: "border-[#ff9900] text-[#ff9900]" },
    { id: "gcp",   label: "GCP",   colour: "border-[#4285f4] text-[#4285f4]" },
    { id: "azure", label: "Azure", colour: "border-[#00a4ef] text-[#00a4ef]" },
  ];

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4">
      <div className="card w-full max-w-md border-teal/40 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-[#688a8a] hover:text-white">
          <X className="w-5 h-5" />
        </button>

        <h2 className="text-lg font-bold text-white mb-1">New Scan</h2>
        <p className="text-xs text-[#688a8a] mb-5">Configure and launch a cloud security scan</p>

        <div className="space-y-4">
          {/* Org Name */}
          <div>
            <label className="text-xs text-[#8ab0b0] mb-1 block">Organisation Name</label>
            <input value={form.org_name} onChange={e => setForm(f => ({ ...f, org_name: e.target.value }))}
              placeholder="My Company" className="cyber-input" />
          </div>

          {/* Cloud Providers */}
          <div>
            <label className="text-xs text-[#8ab0b0] mb-2 block">Cloud Providers</label>
            <div className="flex gap-2">
              {PROVIDERS.map(({ id, label, colour }) => (
                <button key={id} type="button"
                  onClick={() => toggleProvider(id)}
                  className={clsx(
                    "flex-1 py-2 rounded border text-xs font-bold transition-all",
                    form.providers.includes(id)
                      ? `${colour} bg-opacity-20 bg-white/10`
                      : "border-[#1e3a45] text-[#688a8a] hover:border-[#2a6b7c]"
                  )}>
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Credentials */}
          <div>
            <label className="text-xs text-[#8ab0b0] mb-1 block">Saved Credentials (optional)</label>
            <select value={form.credential_id}
              onChange={e => setForm(f => ({ ...f, credential_id: e.target.value }))}
              className="cyber-input">
              <option value="">— Select saved credential —</option>
              {creds?.map(c => (
                <option key={c.id} value={c.id}>{c.label} ({c.provider.toUpperCase()})</option>
              ))}
            </select>
          </div>

          {/* Mock Mode */}
          <div className="flex items-center gap-3 p-3 bg-[#0f2030] rounded border border-[#1e3a45]">
            <input type="checkbox" id="mock" checked={form.use_mock}
              onChange={e => setForm(f => ({ ...f, use_mock: e.target.checked }))}
              className="w-4 h-4 accent-teal" />
            <div>
              <label htmlFor="mock" className="text-sm text-white cursor-pointer">Demo Mode</label>
              <p className="text-xs text-[#688a8a]">Use mock data — no credentials needed</p>
            </div>
          </div>

          <button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending || !form.org_name || (form.providers.length === 0 && !form.use_mock)}
            className="btn-cyber w-full flex items-center justify-center gap-2">
            {mutation.isPending
              ? <><Loader2 className="w-4 h-4 animate-spin" />Launching...</>
              : <><Zap className="w-4 h-4" />LAUNCH SCAN</>}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function ScansPage() {
  const qc = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [search, setSearch] = useState("");

  const { data: scans = [], isLoading } = useQuery<Scan[]>({
    queryKey: ["scans"],
    queryFn:  () => scansAPI.list().then(r => r.data),
    refetchInterval: 15_000,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => scansAPI.delete(id),
    onSuccess:  () => { toast.success("Scan deleted"); qc.invalidateQueries({ queryKey: ["scans"] }); },
    onError:    () => toast.error("Delete failed"),
  });

  const filtered = scans.filter(s =>
    s.org_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {showModal && <NewScanModal onClose={() => setShowModal(false)} />}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Scans</h1>
          <p className="text-sm text-[#688a8a]">{scans.length} total scan{scans.length !== 1 ? "s" : ""}</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-cyber flex items-center gap-2 text-sm">
          <Zap className="w-4 h-4" /> New Scan
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-teal" />
        <input value={search} onChange={e => setSearch(e.target.value)}
          placeholder="Search by organisation name..." className="cyber-input pl-10" />
      </div>

      {/* Table */}
      <div className="card overflow-hidden p-0">
        {isLoading ? (
          <div className="flex items-center justify-center h-40 text-cyber animate-pulse">Loading scans...</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 text-[#688a8a]">
            <Zap className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p className="text-sm">No scans found</p>
            <button onClick={() => setShowModal(true)} className="text-cyber text-sm hover:underline mt-1">
              Run your first scan →
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-[#0f2030]">
                <tr className="text-left text-[#688a8a] text-xs">
                  {["Organisation","Providers","Status","Risk","Findings","Compliance","Started","Actions"].map(h => (
                    <th key={h} className="px-4 py-3 font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1e3a45]">
                {filtered.map((scan) => (
                  <tr key={scan.id} className="hover:bg-[#0f2030] transition-colors">
                    <td className="px-4 py-3">
                      <Link href={`/scans/${scan.id}`} className="text-cyber hover:underline font-medium flex items-center gap-1">
                        {scan.org_name} <ChevronRight className="w-3 h-3" />
                      </Link>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex gap-1 flex-wrap">
                        {scan.providers.map(p => (
                          <span key={p} className="text-[10px] bg-teal/20 text-teal px-1.5 py-0.5 rounded uppercase">{p}</span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3"><StatusBadge status={scan.status} /></td>
                    <td className="px-4 py-3">
                      <span className={clsx("font-bold text-base",
                        (scan.risk_score || 0) >= 80 ? "text-danger" :
                        (scan.risk_score || 0) >= 60 ? "text-warn" : "text-safe"
                      )}>{scan.risk_score ?? "—"}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-xs space-y-0.5">
                        {scan.critical_count > 0 && <div className="text-danger">C: {scan.critical_count}</div>}
                        {scan.high_count     > 0 && <div className="text-warn">H: {scan.high_count}</div>}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={clsx("font-medium",
                        (scan.compliance_pct || 0) >= 70 ? "text-safe" :
                        (scan.compliance_pct || 0) >= 40 ? "text-caution" : "text-danger"
                      )}>{scan.compliance_pct != null ? `${scan.compliance_pct}%` : "—"}</span>
                    </td>
                    <td className="px-4 py-3 text-[#688a8a] text-xs">
                      {formatDistanceToNow(new Date(scan.created_at), { addSuffix: true })}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        {scan.pdf_url && (
                          <a href={scan.pdf_url} target="_blank" rel="noreferrer"
                            className="text-teal hover:text-cyber transition-colors" title="Download PDF">
                            <Download className="w-4 h-4" />
                          </a>
                        )}
                        <button onClick={() => deleteMutation.mutate(scan.id)}
                          className="text-[#688a8a] hover:text-danger transition-colors" title="Delete">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
