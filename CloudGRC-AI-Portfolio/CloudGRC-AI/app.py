"""
CloudGRC-AI — Streamlit Dashboard
A clean, dark-themed web UI to run scans, view findings, and download reports.

Run with: streamlit run app.py
"""
import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

# ── Page Config ──
st.set_page_config(
    page_title="CloudGRC-AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS — Dark Cyber Theme ──
st.markdown("""
<style>
    .stApp { background-color: #010a0e; color: #c9e8e0; }
    .main .block-container { padding-top: 2rem; }
    h1, h2, h3 { font-family: 'Courier New', monospace; color: #00ffe7 !important; }
    .metric-card {
        background: #0a1a20;
        border: 1px solid #00ffe7;
        border-radius: 4px;
        padding: 1rem;
        text-align: center;
    }
    .critical { color: #ff003c; font-weight: bold; }
    .high     { color: #ff6600; font-weight: bold; }
    .medium   { color: #ffaa00; font-weight: bold; }
    .low      { color: #00cc66; font-weight: bold; }
    div[data-testid="stSidebar"] { background-color: #0a1a20; }
    .stButton > button {
        background-color: #00ffe7 !important;
        color: #010a0e !important;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        border: none;
        border-radius: 2px;
    }
    .stSelectbox > div { background-color: #0a1a20; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown("## 🛡️ CloudGRC-AI")
    st.markdown("---")
    st.markdown("### Configuration")

    providers = st.multiselect(
        "Select Cloud Providers",
        ["AWS", "GCP", "Azure"],
        default=["AWS"]
    )
    org_name = st.text_input("Organisation Name", value="My Organisation")
    use_mock = st.checkbox("Use Mock Data (Demo Mode)", value=True)

    st.markdown("---")
    st.markdown("### AWS Credentials")
    aws_key    = st.text_input("AWS Access Key ID", type="password")
    aws_secret = st.text_input("AWS Secret Access Key", type="password")
    aws_region = st.text_input("AWS Region", value="us-east-1")

    st.markdown("### GCP Credentials")
    gcp_project = st.text_input("GCP Project ID")
    gcp_cred    = st.file_uploader("Service Account JSON", type="json")

    st.markdown("### Azure Credentials")
    az_subscription = st.text_input("Subscription ID", type="password")
    az_tenant       = st.text_input("Tenant ID", type="password")
    az_client       = st.text_input("Client ID", type="password")
    az_secret       = st.text_input("Client Secret", type="password")

    st.markdown("### OpenAI")
    openai_key = st.text_input("OpenAI API Key (optional)", type="password")

    st.markdown("---")
    run_scan = st.button("▶  RUN SCAN", use_container_width=True)


# ── Header ──
st.markdown("# 🛡️ CloudGRC-AI")
st.markdown("#### Automated Cloud Compliance & Risk Scanner")
st.markdown("---")

# ── Session State ──
if "findings" not in st.session_state:
    st.session_state.findings   = []
if "risk_data" not in st.session_state:
    st.session_state.risk_data  = {}
if "ai_report" not in st.session_state:
    st.session_state.ai_report  = {}
if "scan_done" not in st.session_state:
    st.session_state.scan_done  = False


def set_env_vars():
    if aws_key:    os.environ["AWS_ACCESS_KEY_ID"]     = aws_key
    if aws_secret: os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret
    if aws_region: os.environ["AWS_DEFAULT_REGION"]    = aws_region
    if gcp_project: os.environ["GCP_PROJECT_ID"]       = gcp_project
    if az_subscription: os.environ["AZURE_SUBSCRIPTION_ID"] = az_subscription
    if az_tenant:  os.environ["AZURE_TENANT_ID"]       = az_tenant
    if az_client:  os.environ["AZURE_CLIENT_ID"]       = az_client
    if az_secret:  os.environ["AZURE_CLIENT_SECRET"]   = az_secret
    if openai_key: os.environ["OPENAI_API_KEY"]        = openai_key
    if gcp_cred:
        cred_path = "/tmp/gcp_creds.json"
        with open(cred_path, "wb") as f:
            f.write(gcp_cred.read())
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path


# ── Run Scan ──
if run_scan:
    set_env_vars()
    with st.spinner("Scanning cloud environments..."):
        from main import load_mock_findings, run_aws_checks, run_gcp_checks, run_azure_checks
        from compliance.mapping import map_all_findings, calculate_risk_score
        from reporting.ai_summary import generate_ai_report

        SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}
        all_findings = []

        if use_mock:
            all_findings = load_mock_findings()
        else:
            if "AWS" in providers:
                try:
                    import boto3
                    session = boto3.Session(
                        aws_access_key_id=aws_key,
                        aws_secret_access_key=aws_secret,
                        region_name=aws_region
                    )
                    all_findings += run_aws_checks()
                except Exception as e:
                    st.warning(f"AWS scan failed: {e}")
            if "GCP" in providers:
                try:
                    all_findings += run_gcp_checks()
                except Exception as e:
                    st.warning(f"GCP scan failed: {e}")
            if "Azure" in providers:
                try:
                    all_findings += run_azure_checks()
                except Exception as e:
                    st.warning(f"Azure scan failed: {e}")

        all_findings = map_all_findings(all_findings)
        all_findings.sort(key=lambda x: SEVERITY_ORDER.get(x.get("severity", "Info"), 99))
        risk_data = calculate_risk_score(all_findings)
        ai_report = generate_ai_report(all_findings, risk_data)

        st.session_state.findings  = all_findings
        st.session_state.risk_data = risk_data
        st.session_state.ai_report = ai_report
        st.session_state.scan_done = True

    st.success("Scan complete!")


# ── Results Dashboard ──
if st.session_state.scan_done:
    findings  = st.session_state.findings
    risk_data = st.session_state.risk_data
    ai_report = st.session_state.ai_report
    breakdown = risk_data.get("breakdown", {})

    # ── KPI Row ──
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Findings",  risk_data.get("total_findings", 0))
    c2.metric("Risk Score",      f"{risk_data.get('risk_score', 0)}/100", delta=None)
    c3.metric("Compliance",      f"{risk_data.get('compliance_pct', 0)}%")
    c4.metric("Critical",        breakdown.get("Critical", 0))
    c5.metric("High",            breakdown.get("High", 0))

    st.markdown("---")

    # ── Charts Row ──
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("#### Findings by Severity")
        sev_df = pd.DataFrame([
            {"Severity": k, "Count": v}
            for k, v in breakdown.items() if v > 0
        ])
        fig1 = px.pie(
            sev_df, names="Severity", values="Count",
            color="Severity",
            color_discrete_map={
                "Critical": "#ff003c", "High": "#ff6600",
                "Medium": "#ffaa00", "Low": "#00cc66", "Info": "#888888"
            },
            template="plotly_dark"
        )
        fig1.update_layout(paper_bgcolor="#010a0e", plot_bgcolor="#010a0e")
        st.plotly_chart(fig1, use_container_width=True)

    with col_chart2:
        st.markdown("#### Findings by Cloud Provider")
        cloud_counts = {}
        for f in findings:
            cloud = f.get("cloud", "Unknown")
            cloud_counts[cloud] = cloud_counts.get(cloud, 0) + 1
        cloud_df = pd.DataFrame([{"Cloud": k, "Count": v} for k, v in cloud_counts.items()])
        fig2 = px.bar(
            cloud_df, x="Cloud", y="Count",
            color="Cloud",
            color_discrete_map={"AWS": "#ff9900", "GCP": "#4285f4", "Azure": "#00a4ef"},
            template="plotly_dark"
        )
        fig2.update_layout(paper_bgcolor="#010a0e", plot_bgcolor="#010a0e")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Risk Gauge ──
    st.markdown("#### Overall Risk Score")
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=risk_data.get("risk_score", 0),
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#00ffe7"},
            "steps": [
                {"range": [0, 30],  "color": "#003300"},
                {"range": [30, 60], "color": "#333300"},
                {"range": [60, 80], "color": "#332200"},
                {"range": [80, 100],"color": "#330000"},
            ],
            "threshold": {"line": {"color": "#ff003c", "width": 4}, "value": 80}
        },
        title={"text": "Risk Score (0=Safe, 100=Critical)", "font": {"color": "#c9e8e0"}},
        number={"font": {"color": "#00ffe7"}}
    ))
    gauge.update_layout(paper_bgcolor="#010a0e", font_color="#c9e8e0", height=280)
    st.plotly_chart(gauge, use_container_width=True)

    st.markdown("---")

    # ── Findings Table ──
    st.markdown("#### Detailed Findings")

    # Filters
    f_col1, f_col2, f_col3 = st.columns(3)
    sev_filter   = f_col1.multiselect("Filter by Severity", ["Critical","High","Medium","Low","Info"],
                                       default=["Critical","High","Medium"])
    cloud_filter = f_col2.multiselect("Filter by Cloud", ["AWS","GCP","Azure"],
                                       default=["AWS","GCP","Azure"])
    cat_filter   = f_col3.multiselect("Filter by Category", ["IAM","Storage","Network","Logging"],
                                       default=["IAM","Storage","Network","Logging"])

    filtered = [
        f for f in findings
        if f.get("severity") in sev_filter
        and f.get("cloud") in cloud_filter
        and f.get("category") in cat_filter
    ]

    if filtered:
        df = pd.DataFrame([{
            "Cloud":    f.get("cloud",""),
            "Category": f.get("category",""),
            "Severity": f.get("severity",""),
            "Issue":    f.get("issue",""),
            "Resource": f.get("resource",""),
            "ISO 27001":f.get("frameworks",{}).get("ISO27001",""),
            "NIST CSF": f.get("frameworks",{}).get("NIST_CSF",""),
            "CIS":      f.get("frameworks",{}).get("CIS",""),
        } for f in filtered])

        def colour_severity(val):
            colours = {"Critical":"background-color:#330000;color:#ff003c",
                       "High":"background-color:#2a1500;color:#ff6600",
                       "Medium":"background-color:#2a2200;color:#ffaa00",
                       "Low":"background-color:#002200;color:#00cc66"}
            return colours.get(val, "")

        st.dataframe(
            df.style.applymap(colour_severity, subset=["Severity"]),
            use_container_width=True,
            height=400
        )
    else:
        st.info("No findings match the current filters.")

    st.markdown("---")

    # ── AI Report Sections ──
    st.markdown("#### AI Audit Report")
    tab1, tab2, tab3, tab4 = st.tabs([
        "Executive Summary", "Technical Findings", "Business Impact", "Remediation Plan"
    ])
    with tab1: st.markdown(ai_report.get("executive_summary", ""))
    with tab2: st.markdown(ai_report.get("technical_findings", ""))
    with tab3: st.markdown(ai_report.get("business_impact", ""))
    with tab4: st.markdown(ai_report.get("remediation_plan", ""))

    st.markdown("---")

    # ── Download Row ──
    st.markdown("#### Export Reports")
    dl1, dl2, dl3 = st.columns(3)

    # JSON
    json_bytes = json.dumps({
        "scan_timestamp": datetime.now().isoformat(),
        "risk_summary": risk_data,
        "ai_report": ai_report,
        "findings": findings,
    }, indent=2, default=str).encode()
    dl1.download_button("⬇ Download JSON", json_bytes,
                         file_name="cloudgrc_report.json", mime="application/json")

    # CSV
    if findings:
        flat_findings = [{k: v for k, v in f.items() if k != "frameworks"} for f in findings]
        csv_str = pd.DataFrame(flat_findings).to_csv(index=False)
        dl2.download_button("⬇ Download CSV", csv_str,
                             file_name="cloudgrc_findings.csv", mime="text/csv")

    # PDF
    try:
        from reporting.pdf_generator import generate_pdf_report
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            pdf_path = tmp.name
        generate_pdf_report(findings, risk_data, ai_report, pdf_path, org_name)
        with open(pdf_path, "rb") as f:
            dl3.download_button("⬇ Download PDF", f.read(),
                                 file_name="cloudgrc_audit_report.pdf", mime="application/pdf")
    except Exception as e:
        dl3.warning(f"PDF generation requires ReportLab: {e}")

else:
    st.info("Configure your credentials in the sidebar and click **RUN SCAN** to begin.")
    st.markdown("""
    ### How to Use
    1. Select your cloud provider(s) in the sidebar
    2. Enter credentials OR enable **Mock Data** for a demo
    3. Click **RUN SCAN**
    4. Review findings, risk score, and compliance charts
    5. Download your audit report as PDF, JSON, or CSV

    ### Supported Frameworks
    | Framework | Reference |
    |---|---|
    | ISO/IEC 27001:2022 | Annex A Controls |
    | NIST Cybersecurity Framework | Identify, Protect, Detect, Respond |
    | CIS Benchmarks | Cloud Security Controls |
    """)
