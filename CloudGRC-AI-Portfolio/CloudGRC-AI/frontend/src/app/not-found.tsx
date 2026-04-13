import Link from "next/link";
import { Shield } from "lucide-react";
export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#010a0e] text-center">
      <div>
        <Shield className="w-16 h-16 text-teal mx-auto mb-4 opacity-50" />
        <h1 className="text-4xl font-bold text-white mb-2">404</h1>
        <p className="text-[#688a8a] mb-6">Page not found</p>
        <Link href="/dashboard" className="btn-cyber">Return to Dashboard</Link>
      </div>
    </div>
  );
}
