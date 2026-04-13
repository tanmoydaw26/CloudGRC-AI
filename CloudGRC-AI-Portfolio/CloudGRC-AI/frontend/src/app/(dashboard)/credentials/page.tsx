"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { credentialsAPI } from "@/services/api";
import { Credential } from "@/types";
import { Key, Plus, Trash2, X, Loader2, Cloud } from "lucide-react";
import toast from "react-hot-toast";
import clsx from "clsx";

const PROVIDER_STYLE: Record<string,string> = {
  aws:   "bg-[#ff9900]/10 text-[#ff9900] border-[#ff9900]/30",
  gcp:   "bg-[#4285f4]/10 text-[#4285f4] border-[#4285f4]/30",
  azure: "bg-[#00a4ef]/10 text-[#00a4ef] border-[#00a4ef]/30",
};

function AddCredentialModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const [provider, setProvider] = useState<"aws"|"gcp"|"azure">("aws");
  const [form, setForm] = useState<Record<string,string>>({ label: "" });
  const [loading, setLoading] = useState(false);

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));

  const handleSubmit = async () => {
    if (!form.label) return toast.error("Label is required");
    setLoading(true);
    try {
      await credentialsAPI.save({ provider, ...form });
      toast.success("Credentials saved securely");
      qc.invalidateQueries({ queryKey: ["credentials"] });
      onClose();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Save failed");
    } finally {
      setLoading(false);
    }
  };

  const Field = ({ name, label, type="text", ph="" }: any) => (
    <div>
      <label className="text-xs text-[#8ab0b0] mb-1 block">{label}</label>
      <input value={form[name]||""} onChange={e => set(name, e.target.value)}
        type={type} placeholder={ph} className="cyber-input" />
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4">
      <div className="card w-full max-w-lg border-teal/40 relative max-h-[90vh] overflow-y-auto">
        <button onClick={onClose} className="absolute top-4 right-4 text-[#688a8a] hover:text-white">
          <X className="w-5 h-5" />
        </button>
        <h2 className="text-lg font-bold text-white mb-1">Add Cloud Credentials</h2>
        <p className="text-xs text-[#688a8a] mb-5">
          All credentials are encrypted with AES-256 before storage. Secrets are never returned via API.
        </p>

        <div className="space-y-4">
          <Field name="label" label="Label" ph="e.g. Production AWS" />

          {/* Provider tabs */}
          <div>
            <label className="text-xs text-[#8ab0b0] mb-2 block">Cloud Provider</label>
            <div className="flex gap-2">
              {(["aws","gcp","azure"] as const).map(p => (
                <button key={p} onClick={() => setProvider(p)}
                  className={clsx("flex-1 py-2 rounded border text-xs font-bold uppercase transition-all",
                    provider === p ? PROVIDER_STYLE[p] : "border-[#1e3a45] text-[#688a8a]"
                  )}>{p}</button>
              ))}
            </div>
          </div>

          {/* AWS fields */}
          {provider === "aws" && <>
            <Field name="aws_access_key_id"     label="Access Key ID"     ph="AKIAIOSFODNN7EXAMPLE" />
            <Field name="aws_secret_access_key" label="Secret Access Key" type="password" ph="wJalrXUtnFEMI/K7MDENG" />
            <Field name="aws_region"             label="Default Region"    ph="ap-south-1" />
          </>}

          {/* GCP fields */}
          {provider === "gcp" && <>
            <Field name="gcp_project_id" label="Project ID" ph="my-project-123" />
            <div>
              <label className="text-xs text-[#8ab0b0] mb-1 block">Service Account JSON</label>
              <textarea
                value={form.gcp_service_account_json||""}
                onChange={e => set("gcp_service_account_json", e.target.value)}
                placeholder='Paste your service account JSON here...'
                rows={5} className="cyber-input font-mono text-xs resize-none" />
            </div>
          </>}

          {/* Azure fields */}
          {provider === "azure" && <>
            <Field name="azure_subscription_id" label="Subscription ID"  type="password" />
            <Field name="azure_tenant_id"        label="Tenant ID"        type="password" />
            <Field name="azure_client_id"        label="Client ID"        type="password" />
            <Field name="azure_client_secret"    label="Client Secret"    type="password" />
          </>}

          <div className="flex items-center gap-2 p-3 bg-[#0f2030] rounded border border-teal/20 text-xs text-teal">
            🔒 Credentials are encrypted with Fernet (AES-256) before being stored in the database.
          </div>

          <button onClick={handleSubmit} disabled={loading}
            className="btn-cyber w-full flex items-center justify-center gap-2">
            {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Saving...</> : "SAVE CREDENTIALS"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function CredentialsPage() {
  const qc = useQueryClient();
  const [showModal, setShowModal] = useState(false);

  const { data: creds = [], isLoading } = useQuery<Credential[]>({
    queryKey: ["credentials"],
    queryFn:  () => credentialsAPI.list().then(r => r.data),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => credentialsAPI.delete(id),
    onSuccess:  () => { toast.success("Credential deleted"); qc.invalidateQueries({ queryKey: ["credentials"] }); },
    onError:    () => toast.error("Delete failed"),
  });

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {showModal && <AddCredentialModal onClose={() => setShowModal(false)} />}

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Cloud Credentials</h1>
          <p className="text-sm text-[#688a8a]">Encrypted and stored securely — secrets never exposed</p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn-cyber flex items-center gap-2 text-sm">
          <Plus className="w-4 h-4" /> Add Credentials
        </button>
      </div>

      {isLoading ? (
        <div className="text-cyber animate-pulse text-sm">Loading credentials...</div>
      ) : creds.length === 0 ? (
        <div className="card text-center py-16 text-[#688a8a]">
          <Key className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <p className="text-sm mb-1">No credentials saved yet</p>
          <p className="text-xs mb-4">Add cloud credentials to enable real environment scanning</p>
          <button onClick={() => setShowModal(true)} className="btn-primary text-sm">Add First Credential</button>
        </div>
      ) : (
        <div className="space-y-3">
          {creds.map(cred => (
            <div key={cred.id} className="card flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className={clsx("p-2 rounded border", PROVIDER_STYLE[cred.provider])}>
                  <Cloud className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-white font-medium">{cred.label}</p>
                  <p className={clsx("text-xs font-bold uppercase mt-0.5", `text-[${cred.provider === "aws" ? "#ff9900" : cred.provider === "gcp" ? "#4285f4" : "#00a4ef"}]`)}>
                    {cred.provider}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-teal bg-teal/10 px-2 py-1 rounded border border-teal/20">
                  🔒 Encrypted
                </span>
                <button onClick={() => deleteMutation.mutate(cred.id)}
                  className="text-[#688a8a] hover:text-danger transition-colors p-1">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
