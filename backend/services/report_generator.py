import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from loguru import logger

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    logger.warning("reportlab not installed; PDF generation disabled")


DARK_BLUE = colors.HexColor("#1a1f3a")
ACCENT = colors.HexColor("#6366f1")
LIGHT_GRAY = colors.HexColor("#f8fafc")
MID_GRAY = colors.HexColor("#e2e8f0")
SUCCESS = colors.HexColor("#22c55e")
WARNING = colors.HexColor("#f59e0b")
DANGER = colors.HexColor("#ef4444")


def score_color(score: float):
    if score >= 75:
        return SUCCESS
    elif score >= 50:
        return WARNING
    return DANGER


def generate_match_report_pdf(report_data: Dict[str, Any], output_dir: str = "uploads/reports") -> str:
    if not HAS_REPORTLAB:
        raise RuntimeError("reportlab is required for PDF generation")

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"match_report_{report_data.get('resume_id', 0)}_{timestamp}.pdf"
    output_path = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle("Title", parent=styles["Heading1"],
        fontSize=22, textColor=DARK_BLUE, spaceAfter=6, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"],
        fontSize=11, textColor=colors.gray, spaceAfter=12, alignment=TA_CENTER)
    h2_style = ParagraphStyle("H2", parent=styles["Heading2"],
        fontSize=14, textColor=ACCENT, spaceAfter=6, spaceBefore=14)
    h3_style = ParagraphStyle("H3", parent=styles["Heading3"],
        fontSize=11, textColor=DARK_BLUE, spaceAfter=4, spaceBefore=8)
    body_style = ParagraphStyle("Body", parent=styles["Normal"],
        fontSize=10, leading=14, spaceAfter=4)
    small_style = ParagraphStyle("Small", parent=styles["Normal"],
        fontSize=9, textColor=colors.gray, spaceAfter=2)
    bullet_style = ParagraphStyle("Bullet", parent=styles["Normal"],
        fontSize=10, leading=14, leftIndent=12, spaceAfter=2,
        bulletText="•")

    story = []

    # --- Header ---
    story.append(Paragraph("AI Resume Analyzer", title_style))
    story.append(Paragraph("Candidate Match Report", subtitle_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", small_style))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT))
    story.append(Spacer(1, 12))

    # --- Candidate Info ---
    candidate = report_data.get("candidate", {})
    story.append(Paragraph("Candidate Profile", h2_style))
    info_data = [
        ["Name", candidate.get("full_name", "N/A"), "Email", candidate.get("email", "N/A")],
        ["Phone", candidate.get("phone", "N/A"), "LinkedIn", candidate.get("linkedin_url", "N/A")],
        ["GitHub", candidate.get("github_url", "N/A"), "Experience", f"{candidate.get('total_experience_years', 0):.1f} years"],
    ]
    info_table = Table(info_data, colWidths=[3*cm, 7*cm, 3*cm, 7*cm])
    info_table.setStyle(TableStyle([
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("TEXTCOLOR", (0,0), (0,-1), colors.gray),
        ("TEXTCOLOR", (2,0), (2,-1), colors.gray),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # --- Overall Match Score ---
    overall = report_data.get("overall_match_score", 0)
    story.append(Paragraph("Match Overview", h2_style))

    score_data = [
        ["Overall Match", f"{overall:.1f}%"],
        ["Skill Match", f"{report_data.get('skill_match_score', 0):.1f}%"],
        ["Experience Match", f"{report_data.get('experience_match_score', 0):.1f}%"],
        ["Education Match", f"{report_data.get('education_match_score', 0):.1f}%"],
        ["Project Relevance", f"{report_data.get('project_relevance_score', 0):.1f}%"],
        ["Keyword Match", f"{report_data.get('keyword_match_score', 0):.1f}%"],
    ]
    score_table = Table(score_data, colWidths=[8*cm, 6*cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK_BLUE),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 13),
        ("BACKGROUND", (0,1), (-1,-1), LIGHT_GRAY),
        ("FONTSIZE", (0,1), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("GRID", (0,0), (-1,-1), 0.5, MID_GRAY),
        ("TEXTCOLOR", (1,1), (1,-1), score_color(overall)),
        ("FONTNAME", (1,0), (1,-1), "Helvetica-Bold"),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 12))

    # --- Candidate Scorecard ---
    scorecard = report_data.get("scorecard", {})
    story.append(Paragraph("Candidate Scorecard", h2_style))
    sc_data = [
        ["ATS Score", "Resume Quality", "Technical Skills", "Employability"],
        [
            f"{scorecard.get('ats_score', 0):.1f}",
            f"{scorecard.get('resume_quality_score', 0):.1f}",
            f"{scorecard.get('technical_skill_score', 0):.1f}",
            f"{scorecard.get('employability_score', 0):.1f}",
        ],
    ]
    sc_table = Table(sc_data, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 4.5*cm])
    sc_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), ACCENT),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 10),
        ("FONTSIZE", (0,1), (-1,1), 20),
        ("FONTNAME", (0,1), (-1,1), "Helvetica-Bold"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.5, MID_GRAY),
        ("BACKGROUND", (0,1), (-1,1), LIGHT_GRAY),
    ]))
    story.append(sc_table)
    story.append(Spacer(1, 14))

    # --- Matched Skills ---
    matched_skills = report_data.get("matched_skills", [])
    missing_skills = report_data.get("missing_skills", [])

    story.append(Paragraph("Skill Analysis", h2_style))

    if matched_skills:
        story.append(Paragraph("✓ Matched Skills", h3_style))
        skill_rows = []
        row = []
        for i, skill in enumerate(matched_skills):
            row.append(Paragraph(f"✓ {skill}", ParagraphStyle("sk", parent=body_style, textColor=SUCCESS)))
            if len(row) == 3:
                skill_rows.append(row)
                row = []
        if row:
            while len(row) < 3:
                row.append("")
            skill_rows.append(row)
        if skill_rows:
            sk_table = Table(skill_rows, colWidths=[6*cm, 6*cm, 6*cm])
            sk_table.setStyle(TableStyle([
                ("TOPPADDING", (0,0), (-1,-1), 3),
                ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ]))
            story.append(sk_table)
        story.append(Spacer(1, 6))

    if missing_skills:
        story.append(Paragraph("✗ Missing Skills", h3_style))
        for skill in missing_skills:
            story.append(Paragraph(f"✗ {skill}", ParagraphStyle("ms", parent=body_style, textColor=DANGER)))
        story.append(Spacer(1, 8))

    # --- Skill Gap Analysis ---
    gap = report_data.get("skill_gap_analysis", [])
    if gap:
        story.append(Paragraph("Skill Gap Analysis & Learning Paths", h2_style))
        for item in gap[:6]:
            story.append(Paragraph(f"{item.get('skill')} — Priority: {item.get('priority')}", h3_style))
            for step in item.get("learning_path", []):
                story.append(Paragraph(
                    f"  [{step.get('level')}] {step.get('title')} — {step.get('platform', '')}",
                    bullet_style
                ))
            story.append(Spacer(1, 4))

    # --- Recommendations ---
    recs = report_data.get("recommendations", [])
    if recs:
        story.append(Paragraph("Recommendations", h2_style))
        for rec in recs:
            story.append(Paragraph(f"• {rec}", body_style))
        story.append(Spacer(1, 8))

    # --- Improvement Suggestions ---
    sugs = report_data.get("improvement_suggestions", [])
    if sugs:
        story.append(Paragraph("Resume Improvement Suggestions", h2_style))
        for sug in sugs:
            story.append(Paragraph(f"• {sug}", body_style))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_GRAY))
    story.append(Paragraph("Generated by AI Resume Analyzer Platform", small_style))

    doc.build(story)
    logger.info(f"Report generated: {output_path}")
    return output_path
