"""
PDF Audit Report Generator — uses ReportLab to produce a professional, 
formatted PDF audit report from scan findings and AI narrative.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import List, Dict
import os

BRAND_DARK   = colors.HexColor("#0a1a20")
BRAND_ACCENT = colors.HexColor("#00ffe7")
BRAND_RED    = colors.HexColor("#ff003c")
BRAND_YELLOW = colors.HexColor("#ffe600")

SEV_COLORS = {
    "Critical": colors.HexColor("#ff003c"),
    "High":     colors.HexColor("#ff6600"),
    "Medium":   colors.HexColor("#ffaa00"),
    "Low":      colors.HexColor("#00cc66"),
    "Info":     colors.HexColor("#999999"),
}


def generate_pdf_report(
    findings: List[Dict],
    risk_data: Dict,
    ai_report: Dict,
    output_path: str = "CloudGRC_Audit_Report.pdf",
    org_name: str = "Organisation"
) -> str:
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"],
        fontSize=22, textColor=BRAND_DARK, spaceAfter=6, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle("SubtitleStyle", parent=styles["Normal"],
        fontSize=11, textColor=colors.HexColor("#4a7a70"), alignment=TA_CENTER, spaceAfter=4)
    h1_style = ParagraphStyle("H1", parent=styles["Heading1"],
        fontSize=14, textColor=BRAND_DARK, spaceBefore=14, spaceAfter=6,
        borderPad=4, borderColor=BRAND_ACCENT, borderWidth=0)
    body_style = ParagraphStyle("Body", parent=styles["Normal"],
        fontSize=9, leading=14, spaceAfter=6)
    small_style = ParagraphStyle("Small", parent=styles["Normal"],
        fontSize=8, textColor=colors.grey)

    # ─── Cover Page ───
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("CloudGRC-AI", title_style))
    story.append(Paragraph("Cloud Security Compliance & Risk Audit Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=BRAND_ACCENT, spaceAfter=12))
    story.append(Paragraph(f"Organisation: <b>{org_name}</b>", body_style))
    story.append(Paragraph(f"Report Date: <b>{datetime.now().strftime('%d %B %Y, %H:%M UTC')}</b>", body_style))
    story.append(Paragraph(f"Total Findings: <b>{risk_data.get('total_findings', 0)}</b>", body_style))
    story.append(Paragraph(f"Overall Risk Score: <b>{risk_data.get('risk_score', 0)}/100</b>", body_style))
    story.append(Paragraph(f"Compliance Score: <b>{risk_data.get('compliance_pct', 0)}%</b>", body_style))
    story.append(Spacer(1, 0.5*cm))

    # Severity summary table
    breakdown = risk_data.get("breakdown", {})
    sev_data = [["Severity", "Count"]]
    for sev in ["Critical", "High", "Medium", "Low", "Info"]:
        sev_data.append([sev, str(breakdown.get(sev, 0))])
    sev_table = Table(sev_data, colWidths=[6*cm, 4*cm])
    sev_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("ALIGN",      (1, 0), (1, -1), "CENTER"),
    ]))
    story.append(sev_table)
    story.append(PageBreak())

    # ─── AI Report Sections ───
    for section_key, section_title in [
        ("executive_summary", "1. Executive Summary"),
        ("technical_findings", "2. Technical Findings"),
        ("business_impact",    "3. Business Impact"),
        ("remediation_plan",   "4. Remediation Plan"),
    ]:
        story.append(Paragraph(section_title, h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=BRAND_ACCENT, spaceAfter=8))
        content = ai_report.get(section_key, "Not available.")
        for line in content.split("\n"):
            if line.strip():
                story.append(Paragraph(line.strip(), body_style))
        story.append(Spacer(1, 0.5*cm))

    story.append(PageBreak())

    # ─── Detailed Findings Table ───
    story.append(Paragraph("5. Detailed Findings", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BRAND_ACCENT, spaceAfter=8))

    table_data = [["#", "Cloud", "Category", "Severity", "Issue", "ISO 27001"]]
    for i, f in enumerate(findings, 1):
        fw = f.get("frameworks", {})
        iso = fw.get("ISO27001", "")[:40] + "..." if len(fw.get("ISO27001", "")) > 40 else fw.get("ISO27001", "")
        issue_text = f.get("issue", "")[:60] + "..." if len(f.get("issue", "")) > 60 else f.get("issue", "")
        table_data.append([
            str(i),
            f.get("cloud", ""),
            f.get("category", ""),
            f.get("severity", ""),
            issue_text,
            iso,
        ])

    col_widths = [0.8*cm, 1.5*cm, 2*cm, 1.8*cm, 7*cm, 4.5*cm]
    findings_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    style = [
        ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, -1), 7),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("WORDWRAP",   (0, 0), (-1, -1), True),
    ]
    # Colour severity cells
    for i, row in enumerate(table_data[1:], 1):
        sev = row[3]
        c = SEV_COLORS.get(sev, colors.grey)
        style.append(("TEXTCOLOR", (3, i), (3, i), c))
        style.append(("FONTNAME",  (3, i), (3, i), "Helvetica-Bold"))

    findings_table.setStyle(TableStyle(style))
    story.append(findings_table)

    # ─── Footer note ───
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
    story.append(Paragraph(
        "Generated by CloudGRC-AI | Confidential — For authorised recipients only | "
        f"© {datetime.now().year} CloudGRC-AI",
        small_style
    ))

    doc.build(story)
    print(f"[PDF] Report saved to: {output_path}")
    return output_path
