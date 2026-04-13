"use client";
import { useQuery, useMutation } from "@tanstack/react-query";
import { billingAPI } from "@/services/api";
import { Plan } from "@/types";
import { useAuthStore } from "@/store/authStore";
import { CheckCircle, Crown, Zap, Building2, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import clsx from "clsx";
import { useState } from "react";

declare global { interface Window { Razorpay: any; } }

const PLAN_ICONS: Record<string,any> = {
  free: Zap, starter: CheckCircle, pro: Crown, enterprise: Building2
};
const PLAN_STYLES: Record<string,string> = {
  free:       "border-[#1e3a45]",
  starter:    "border-teal",
  pro:        "border-cyber shadow-[0_0_20px_rgba(0,255,231,0.15)]",
  enterprise: "border-purple-500",
};
const PLAN_BTN: Record<string,string> = {
  free:       "btn-primary",
  starter:    "btn-primary",
  pro:        "btn-cyber",
  enterprise: "btn-primary",
};

export default function BillingPage() {
  const { user } = useAuthStore();
  const [loadingPlan, setLoadingPlan] = useState<string|null>(null);

  const { data: plansData } = useQuery<{ plans: Plan[] }>({
    queryKey: ["plans"],
    queryFn:  () => billingAPI.plans().then(r => r.data),
  });

  const { data: statusData } = useQuery({
    queryKey: ["billing-status"],
    queryFn:  () => billingAPI.status().then(r => r.data),
  });

  const orderMutation = useMutation({
    mutationFn: (plan: string) => billingAPI.order(plan).then(r => r.data),
  });

  const verifyMutation = useMutation({
    mutationFn: (data: any) => billingAPI.verify(data).then(r => r.data),
    onSuccess: (data) => {
      toast.success(`Upgraded to ${data.plan} plan!`);
      window.location.reload();
    },
    onError: () => toast.error("Payment verification failed. Contact support."),
  });

  const handleUpgrade = async (plan: string) => {
    if (plan === "enterprise") {
      window.open("mailto:sales@cloudgrc.ai?subject=Enterprise Plan Enquiry", "_blank");
      return;
    }
    if (plan === user?.plan) return;

    setLoadingPlan(plan);
    try {
      const order = await orderMutation.mutateAsync(plan);

      // Load Razorpay script dynamically
      if (!window.Razorpay) {
        await new Promise<void>((res, rej) => {
          const s = document.createElement("script");
          s.src = "https://checkout.razorpay.com/v1/checkout.js";
          s.onload = () => res();
          s.onerror = () => rej();
          document.body.appendChild(s);
        });
      }

      const rzp = new window.Razorpay({
        key:         order.key_id,
        amount:      order.amount,
        currency:    order.currency,
        order_id:    order.order_id,
        name:        "CloudGRC-AI",
        description: `Upgrade to ${plan} plan`,
        prefill: {
          name:  order.user_name,
          email: order.user_email,
        },
        theme: { color: "#2a6b7c" },
        handler: (response: any) => {
          verifyMutation.mutate({
            razorpay_order_id:   response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature:  response.razorpay_signature,
            plan,
          });
        },
        modal: { ondismiss: () => setLoadingPlan(null) },
      });
      rzp.open();
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Could not create order");
      setLoadingPlan(null);
    }
  };

  const plans = plansData?.plans || [];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white">Billing & Plans</h1>
        <p className="text-sm text-[#688a8a]">Upgrade to scan real cloud environments</p>
      </div>

      {/* Current usage */}
      {statusData && (
        <div className="card border-teal/30 flex items-center justify-between flex-wrap gap-4">
          <div>
            <p className="text-xs text-[#688a8a] mb-0.5">Current Plan</p>
            <p className="text-white font-bold text-lg capitalize">{statusData.plan}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-[#688a8a] mb-0.5">Scans This Month</p>
            <p className="text-white font-bold">{statusData.scans_used} / {statusData.scans_limit === 9999 ? "∞" : statusData.scans_limit}</p>
          </div>
          <div className="flex-1 min-w-[140px]">
            <div className="h-2 bg-[#1e3a45] rounded-full overflow-hidden">
              <div className="h-full bg-teal rounded-full transition-all"
                style={{ width: `${Math.min(100, (statusData.scans_used / (statusData.scans_limit || 1)) * 100)}%` }} />
            </div>
          </div>
        </div>
      )}

      {/* Pricing cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        {plans.map((plan) => {
          const Icon        = PLAN_ICONS[plan.id] || Zap;
          const isCurrent   = user?.plan === plan.id;
          const isPopular   = plan.id === "pro";
          const isLoading   = loadingPlan === plan.id;

          return (
            <div key={plan.id} className={clsx("card flex flex-col border-2 relative", PLAN_STYLES[plan.id])}>
              {isPopular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-cyber text-navy text-[10px] font-bold px-3 py-0.5 rounded-full">
                  MOST POPULAR
                </div>
              )}
              {isCurrent && (
                <div className="absolute -top-3 right-3 bg-teal text-white text-[10px] font-bold px-2 py-0.5 rounded-full">
                  CURRENT
                </div>
              )}

              <div className="flex items-center gap-2 mb-3">
                <Icon className={clsx("w-5 h-5", isPopular ? "text-cyber" : "text-teal")} />
                <h3 className="font-bold text-white">{plan.name}</h3>
              </div>

              <div className="mb-4">
                {plan.price_inr === null ? (
                  <p className="text-2xl font-bold text-white">Custom</p>
                ) : plan.price_inr === 0 ? (
                  <p className="text-2xl font-bold text-white">Free</p>
                ) : (
                  <p className="text-2xl font-bold text-white">
                    ₹{plan.price_inr.toLocaleString("en-IN")}
                    <span className="text-sm text-[#688a8a] font-normal">/month</span>
                  </p>
                )}
                <p className="text-xs text-[#688a8a] mt-0.5">
                  {plan.scans_per_month >= 999 ? "Unlimited" : plan.scans_per_month} scans/month
                </p>
              </div>

              <ul className="space-y-1.5 flex-1 mb-5">
                {plan.features.map(f => (
                  <li key={f} className="flex items-start gap-2 text-xs text-[#8ab0b0]">
                    <CheckCircle className="w-3.5 h-3.5 text-safe flex-shrink-0 mt-0.5" />
                    {f}
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleUpgrade(plan.id)}
                disabled={isCurrent || isLoading}
                className={clsx(PLAN_BTN[plan.id], "w-full flex items-center justify-center gap-2 text-sm",
                  isCurrent && "opacity-50 cursor-not-allowed"
                )}>
                {isLoading
                  ? <><Loader2 className="w-3.5 h-3.5 animate-spin" />Processing...</>
                  : isCurrent
                    ? "Current Plan"
                    : plan.id === "enterprise"
                      ? "Contact Sales"
                      : `Upgrade to ${plan.name}`}
              </button>
            </div>
          );
        })}
      </div>

      {/* FAQ */}
      <div className="card">
        <h3 className="text-sm font-semibold text-white mb-4">Frequently Asked Questions</h3>
        <div className="grid md:grid-cols-2 gap-4 text-xs text-[#8ab0b0]">
          {[
            ["Can I cancel anytime?",         "Yes — downgrade or cancel at any time from this page with no questions asked."],
            ["Is my payment data secure?",    "All payments are processed by Razorpay. We never store your card details."],
            ["What counts as one scan?",      "One scan = one full multi-cloud check run. You can scan AWS + GCP + Azure in one go."],
            ["Do unused scans roll over?",    "No — scan counts reset at the start of each billing month."],
          ].map(([q, a]) => (
            <div key={q}>
              <p className="text-white font-medium mb-1">{q}</p>
              <p>{a}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
