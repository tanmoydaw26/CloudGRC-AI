"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Shield, LayoutDashboard, Search, Key,
  CreditCard, Settings, LogOut, Menu, X
} from "lucide-react";
import { useState } from "react";
import { useAuthStore } from "@/store/authStore";
import { authAPI } from "@/services/api";
import toast from "react-hot-toast";
import clsx from "clsx";

const NAV = [
  { href: "/dashboard",    label: "Dashboard",    icon: LayoutDashboard },
  { href: "/scans",        label: "Scans",         icon: Search },
  { href: "/credentials",  label: "Credentials",   icon: Key },
  { href: "/billing",      label: "Billing",        icon: CreditCard },
  { href: "/settings",     label: "Settings",       icon: Settings },
];

const PLAN_COLOURS: Record<string, string> = {
  free:       "bg-gray-600",
  starter:    "bg-teal",
  pro:        "bg-cyber text-navy",
  enterprise: "bg-purple-600",
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, logout } = useAuthStore();
  const router   = useRouter();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) router.push("/login");
  }, [isAuthenticated, router]);

  const handleLogout = async () => {
    try { await authAPI.logout(); } catch {}
    logout();
    toast.success("Logged out");
    router.push("/login");
  };

  const Sidebar = ({ mobile = false }) => (
    <aside className={clsx(
      "flex flex-col h-full bg-[#0a1a20] border-r border-[#1e3a45]",
      mobile ? "w-full" : "w-64"
    )}>
      {/* Logo */}
      <div className="p-5 border-b border-[#1e3a45]">
        <div className="flex items-center gap-3">
          <Shield className="text-cyber w-7 h-7" />
          <div>
            <p className="font-mono font-bold text-cyber text-sm">CloudGRC-AI</p>
            <p className="text-[10px] text-teal">Compliance Scanner</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1">
        {NAV.map(({ href, label, icon: Icon }) => (
          <Link key={href} href={href} onClick={() => setOpen(false)}
            className={clsx(
              "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-colors",
              pathname === href
                ? "bg-teal/20 text-cyber border-l-2 border-cyber"
                : "text-[#8ab0b0] hover:bg-[#142030] hover:text-white"
            )}>
            <Icon className="w-4 h-4" />
            {label}
          </Link>
        ))}
      </nav>

      {/* User block */}
      <div className="p-4 border-t border-[#1e3a45]">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-teal flex items-center justify-center text-white text-sm font-bold">
            {user?.full_name?.[0]?.toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-white truncate">{user?.full_name}</p>
            <span className={clsx(
              "text-[10px] px-1.5 py-0.5 rounded uppercase font-bold",
              PLAN_COLOURS[user?.plan || "free"]
            )}>{user?.plan}</span>
          </div>
        </div>
        <button onClick={handleLogout}
          className="flex items-center gap-2 text-xs text-[#688a8a] hover:text-danger transition-colors w-full">
          <LogOut className="w-3.5 h-3.5" /> Sign Out
        </button>
      </div>
    </aside>
  );

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Desktop sidebar */}
      <div className="hidden lg:flex flex-shrink-0">
        <Sidebar />
      </div>

      {/* Mobile sidebar overlay */}
      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={() => setOpen(false)} />
          <div className="relative w-72 h-full">
            <Sidebar mobile />
          </div>
        </div>
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile top bar */}
        <header className="lg:hidden flex items-center justify-between p-4 border-b border-[#1e3a45] bg-[#0a1a20]">
          <div className="flex items-center gap-2">
            <Shield className="text-cyber w-5 h-5" />
            <span className="font-mono text-cyber text-sm font-bold">CloudGRC-AI</span>
          </div>
          <button onClick={() => setOpen(!open)}>
            {open ? <X className="text-white w-5 h-5" /> : <Menu className="text-white w-5 h-5" />}
          </button>
        </header>

        <main className="flex-1 overflow-y-auto p-6 bg-[#010a0e]">
          {children}
        </main>
      </div>
    </div>
  );
}
