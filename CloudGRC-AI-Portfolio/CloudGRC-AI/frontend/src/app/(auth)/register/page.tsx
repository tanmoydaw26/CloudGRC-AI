"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { Shield, Mail, Lock, User, Building2, Loader2 } from "lucide-react";
import { authAPI } from "@/services/api";
import { useAuthStore } from "@/store/authStore";

const schema = z.object({
  full_name: z.string().min(2, "Enter your name"),
  email:     z.string().email("Invalid email"),
  company:   z.string().optional(),
  password:  z.string().min(8, "Minimum 8 characters"),
  confirm:   z.string(),
}).refine((d) => d.password === d.confirm, {
  message: "Passwords do not match", path: ["confirm"],
});
type FormData = z.infer<typeof schema>;

export default function RegisterPage() {
  const router  = useRouter();
  const { setUser, setTokens } = useAuthStore();
  const [loading, setLoading]  = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: FormData) => {
    setLoading(true);
    try {
      const { confirm, ...payload } = data;
      const res = await authAPI.register(payload);
      setTokens(res.data.access_token, res.data.refresh_token);
      setUser(res.data.user);
      toast.success("Account created! Welcome to CloudGRC-AI");
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#010a0e] bg-grid-pattern py-10">
      <div className="w-full max-w-md p-8 card border-teal/40">

        <div className="flex items-center gap-3 mb-8">
          <Shield className="text-cyber w-8 h-8" />
          <div>
            <h1 className="text-xl font-bold text-cyber font-mono">CloudGRC-AI</h1>
            <p className="text-xs text-teal">Start free — no credit card required</p>
          </div>
        </div>

        <h2 className="text-2xl font-bold text-white mb-1">Create Account</h2>
        <p className="text-sm text-[#688a8a] mb-6">Free plan includes 1 demo scan per month</p>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {[
            { name: "full_name", label: "Full Name",     icon: User,      type: "text",     ph: "Tanmoy Daw" },
            { name: "email",     label: "Work Email",    icon: Mail,      type: "email",    ph: "you@company.com" },
            { name: "company",   label: "Company",       icon: Building2, type: "text",     ph: "ISECURION Pvt. Ltd." },
            { name: "password",  label: "Password",      icon: Lock,      type: "password", ph: "Min 8 characters" },
            { name: "confirm",   label: "Confirm",       icon: Lock,      type: "password", ph: "Repeat password" },
          ].map(({ name, label, icon: Icon, type, ph }) => (
            <div key={name}>
              <label className="text-sm text-[#8ab0b0] mb-1 block">{label}</label>
              <div className="relative">
                <Icon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-teal" />
                <input {...register(name as any)} type={type} placeholder={ph}
                  className="cyber-input pl-10" />
              </div>
              {(errors as any)[name] && (
                <p className="text-danger text-xs mt-1">{(errors as any)[name].message}</p>
              )}
            </div>
          ))}

          <button type="submit" disabled={loading}
            className="btn-cyber w-full mt-2 flex items-center justify-center gap-2">
            {loading ? <><Loader2 className="w-4 h-4 animate-spin" />Creating...</> : "CREATE FREE ACCOUNT"}
          </button>
        </form>

        <p className="text-center text-sm text-[#688a8a] mt-6">
          Already have an account?{" "}
          <Link href="/login" className="text-cyber hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
