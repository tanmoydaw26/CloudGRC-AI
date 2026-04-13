export interface User {
  id: string;
  email: string;
  full_name: string;
  company?: string;
  plan: "free" | "starter" | "pro" | "enterprise";
  scans_used_this_month: number;
  is_verified: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface Scan {
  id: string;
  org_name: string;
  providers: string[];
  status: "pending" | "running" | "completed" | "failed";
  risk_score: number | null;
  compliance_pct: number | null;
  total_findings: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  pdf_url?: string;
  created_at: string;
  completed_at?: string;
}

export interface Finding {
  cloud: string;
  category: string;
  issue: string;
  resource: string;
  severity: "Critical" | "High" | "Medium" | "Low" | "Info";
  detail: string;
  frameworks: {
    ISO27001: string;
    NIST_CSF: string;
    CIS: string;
  };
}

export interface ScanDetail extends Scan {
  findings: Finding[];
  ai_report?: {
    executive_summary: string;
    technical_findings: string;
    business_impact: string;
    remediation_plan: string;
  };
  error_message?: string;
}

export interface Credential {
  id: string;
  provider: "aws" | "gcp" | "azure";
  label: string;
}

export interface DashboardStats {
  user: { name: string; plan: string; scans_used: number };
  totals: {
    total_scans: number;
    avg_risk_score: number;
    avg_compliance: number;
    total_findings: number;
    total_critical: number;
    total_high: number;
  };
  recent_scans: Scan[];
}

export interface Plan {
  id: string;
  name: string;
  price_inr: number | null;
  scans_per_month: number;
  features: string[];
}
