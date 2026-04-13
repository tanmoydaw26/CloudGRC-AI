"use client";
import { useState } from "react";
import { useAuthStore } from "@/store/authStore";
import { authAPI } from "@/services/api";
import toast from "react-hot-toast";
import { User, Lock, Bell, Loader2 } from "lucide-react";

export default function SettingsPage() {
  const { user, setUser } = useAuthStore();
  const [tab, setTab] = useState<"profile"|"security"|"notifications">("profile");
  const [loading, setLoading] = useState(false);

  const [profile, setProfile] = useState({
    full_name: user?.full_name || "",
    company:   user?.company  || "",
  });

  const [passwords, setPasswords] = useState({
    current: "", newPass: "", confirm: ""
  });

  const saveProfile = async () => {
    setLoading(true);
    try {
      const res = await authAPI.me();
      setUser(res.data);
      toast.success("Profile updated");
    } catch {
      toast.error("Update failed");
    } finally {
      setLoading(false);
    }
  };

  const TABS = [
    { id: "profile",       label: "Profile",       icon: User },
    { id: "security",      label: "Security",       icon: Lock },
    { id: "notifications", label: "Notifications",  icon: Bell },
  ];

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-sm text-[#688a8a]">Manage your account preferences</p>
      </div>

      <div className="card p-0">
        {/* Tab bar */}
        <div className="flex border-b border-[#1e3a45]">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button key={id} onClick={() => setTab(id as any)}
              className={`flex items-center gap-2 px-5 py-3 text-sm transition-colors ${
                tab === id
                  ? "text-cyber border-b-2 border-cyber bg-teal/10"
                  : "text-[#688a8a] hover:text-white"
              }`}>
              <Icon className="w-4 h-4" />{label}
            </button>
          ))}
        </div>

        <div className="p-6 space-y-4">
          {/* Profile Tab */}
          {tab === "profile" && (
            <>
              <div className="flex items-center gap-4 mb-6">
                <div className="w-14 h-14 rounded-full bg-teal flex items-center justify-center text-white text-xl font-bold">
                  {user?.full_name?.[0]?.toUpperCase()}
                </div>
                <div>
                  <p className="font-semibold text-white">{user?.full_name}</p>
                  <p className="text-sm text-[#688a8a]">{user?.email}</p>
                  <span className="text-xs bg-teal/20 text-teal px-2 py-0.5 rounded capitalize">{user?.plan} plan</span>
                </div>
              </div>

              {[
                { key: "full_name", label: "Full Name",   type: "text" },
                { key: "company",   label: "Company",      type: "text" },
              ].map(({ key, label, type }) => (
                <div key={key}>
                  <label className="text-xs text-[#8ab0b0] mb-1 block">{label}</label>
                  <input
                    type={type}
                    value={(profile as any)[key]}
                    onChange={e => setProfile(p => ({ ...p, [key]: e.target.value }))}
                    className="cyber-input"
                  />
                </div>
              ))}

              <div>
                <label className="text-xs text-[#8ab0b0] mb-1 block">Email Address</label>
                <input type="email" value={user?.email || ""} disabled className="cyber-input opacity-50 cursor-not-allowed" />
                <p className="text-[10px] text-[#688a8a] mt-1">Email cannot be changed. Contact support if needed.</p>
              </div>

              <button onClick={saveProfile} disabled={loading}
                className="btn-primary flex items-center gap-2">
                {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Saving...</> : "Save Changes"}
              </button>
            </>
          )}

          {/* Security Tab */}
          {tab === "security" && (
            <>
              <p className="text-sm text-[#8ab0b0]">Change your account password.</p>
              {[
                { key: "current", label: "Current Password" },
                { key: "newPass", label: "New Password (min 8 chars)" },
                { key: "confirm", label: "Confirm New Password" },
              ].map(({ key, label }) => (
                <div key={key}>
                  <label className="text-xs text-[#8ab0b0] mb-1 block">{label}</label>
                  <input type="password"
                    value={(passwords as any)[key]}
                    onChange={e => setPasswords(p => ({ ...p, [key]: e.target.value }))}
                    className="cyber-input" />
                </div>
              ))}
              <button className="btn-primary">Update Password</button>

              <div className="mt-6 p-4 bg-[#0f2030] rounded border border-teal/20">
                <p className="text-sm font-semibold text-white mb-1">Active Sessions</p>
                <p className="text-xs text-[#688a8a]">You are currently logged in on this device.</p>
                <button className="text-xs text-danger hover:underline mt-2">
                  Sign out of all devices
                </button>
              </div>
            </>
          )}

          {/* Notifications Tab */}
          {tab === "notifications" && (
            <div className="space-y-4">
              <p className="text-sm text-[#8ab0b0]">Configure scan and alert notifications.</p>
              {[
                ["Scan completed email",     "Receive an email when a scan finishes",    true],
                ["Critical findings alert",  "Immediate email for Critical severity",     true],
                ["Weekly digest",            "Weekly summary of all scan activity",      false],
                ["Billing alerts",           "Payment and plan change notifications",     true],
              ].map(([label, desc, def]: any) => (
                <div key={label} className="flex items-center justify-between p-3 bg-[#0f2030] rounded border border-[#1e3a45]">
                  <div>
                    <p className="text-sm text-white">{label}</p>
                    <p className="text-xs text-[#688a8a]">{desc}</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" defaultChecked={def} className="sr-only peer" />
                    <div className="w-9 h-5 bg-[#1e3a45] rounded-full peer peer-checked:bg-teal after:absolute after:top-0.5 after:left-0.5 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:after:translate-x-4"></div>
                  </label>
                </div>
              ))}
              <button className="btn-primary">Save Preferences</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
