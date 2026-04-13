"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { Shield, Mail, Lock, Loader2 } from "lucide-react";
import { authAPI } from "@/services/api";
import { useAuthStore } from "@/store/authStore";

const schema = z.object({
  email:    z.string().email("Invalid email"),
  password: z.string().min(6, "Minimum 6 characters"),
});
type FormData = z.infer<typeof schema>;

export default function LoginPage() {
  const router   = useRouter();
  const { setUser, setTokens } = useAuthStore();
  const [loading, setLoading]  = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    try {
      const res = await authAPI.login(data);
      setTokens(res.data.access_token, res.data.refresh_token);
      setUser(res.data.user);
      toast.success(`Welcome back, ${res.data.user.full_name}!`);
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#010a0e] bg-grid-pattern">
      <div className="w-full max-w-md p-8 card border-teal/40">

        {/* Logo */}
        <div className="flex items-center gap-3 mb-8">
          <Shield className="text-cyber w-8 h-8" />
          <div>
            <h1 className="text-xl font-bold text-cyber font-mono">CloudGRC-AI</h1>
            <p className="text-xs text-teal">Cloud Compliance & Risk Scanner</p>
          </div>
        </div>

        <h2 className="text-2xl font-bold text-white mb-1">Sign In</h2>
        <p className="text-sm text-[#688a8a] mb-6">Access your security dashboard</p>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {/* Email */}
          <div>
            <label className="text-sm text-[#8ab0b0] mb-1 block">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-teal" />
              <input {...register("email")} type="email" placeholder="you@company.com"
                className="cyber-input pl-10" />
            </div>
            {errors.email && <p className="text-danger text-xs mt-1">{errors.email.message}</p>}
          </div>

          {/* Password */}
          <div>
            <label className="text-sm text-[#8ab0b0] mb-1 block">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-teal" />
              <input {...register("password")} type="password" placeholder="••••••••"
                className="cyber-input pl-10" />
            </div>
            {errors.password && <p className="text-danger text-xs mt-1">{errors.password.message}</p>}
          </div>

          <button type="submit" disabled={loading} className="btn-cyber w-full mt-2 flex items-center justify-center gap-2">
            {loading ? <><Loader2 className="w-4 h-4 animate-spin" /> Signing in...</> : "SIGN IN"}
          </button>
        </form>

        <p className="text-center text-sm text-[#688a8a] mt-6">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="text-cyber hover:underline">Create one free</Link>
        </p>
      </div>
    </div>
  );
}
