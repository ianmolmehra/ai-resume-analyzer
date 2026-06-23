import sys, os
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "backend"))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import tempfile
from pathlib import Path

from styles import (GLOBAL_CSS, metric_card_html, score_color_class,
                           score_label, progress_bar_html, score_color)

st.set_page_config(page_title="Job Matching · AI Analyzer", page_icon="🎯", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🧠 AI Resume Analyzer")
    st.page_link("streamlit_app.py",     label="🏠  Upload Resume")
    st.page_link("pages/1_Analysis.py",  label="📄  Resume Analysis")
    st.page_link("pages/2_Matching.py",  label="🎯  Job Matching")
    st.page_link("pages/3_Dashboard.py", label="📊  Analytics")
    st.page_link("pages/4_Admin.py",     label="🛡️  Admin Panel")
    st.markdown("---")
    if "resume_id" in st.session_state:
        st.success(f"Resume #{st.session_state.resume_id} loaded")

if "parsed" not in st.session_state:
    st.warning("No resume loaded. Please upload one first.")
    st.page_link("streamlit_app.py", label="← Upload Resume")
    st.stop()

st.markdown("## 🎯 Job Description Matching")
st.markdown("Paste a job description to get a detailed match analysis, skill gap report, and ATS score.")

# ── JD Input ──────────────────────────────────────────────────────────────────
with st.form("jd_form"):
    c1, c2 = st.columns(2)
    with c1:
        job_title = st.text_input("Job Title", placeholder="e.g. Senior Data Engineer")
    with c2:
        company   = st.text_input("Company",   placeholder="e.g. Google")

    jd_text = st.text_area(
        "Paste Job Description *",
        height=220,
        placeholder="Copy and paste the full job description here — requirements, qualifications, responsibilities…",
    )

    jd_file = st.file_uploader("Or upload JD file (PDF/DOCX)", type=["pdf","docx"], key="jd_uploader")
    submitted = st.form_submit_button("🎯 Analyze Match", use_container_width=True)

# ── Run matching ───────────────────────────────────────────────────────────────
if submitted:
    final_jd_text = jd_text.strip()

    if jd_file and not final_jd_text:
        ext = Path(jd_file.name).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(jd_file.getvalue())
            tmp_path = tmp.name
        try:
            from services.resume_parser import extract_text
            final_jd_text = extract_text(tmp_path)
        except Exception as e:
            st.error(f"Failed to read JD file: {e}")
            st.stop()
        finally:
            os.unlink(tmp_path)

    if len(final_jd_text) < 30:
        st.error("Please provide a job description (at least 30 characters).")
        st.stop()

    with st.spinner("Running AI match analysis…"):
        from services.jd_analyzer import analyze_job_description
        from services.matching_engine import match_resume_to_jd
        from services.resume_parser import extract_text

        parsed   = st.session_state.parsed
        raw_text = st.session_state.get("raw_text", "")
        skills   = st.session_state.get("skills", [])
        resume_id= st.session_state.get("resume_id", 0)

        # Rebuild skill objects
        from schemas.resume import SkillWithConfidence
        parsed.skills = [SkillWithConfidence(**s) for s in skills]

        jd_data = analyze_job_description(final_jd_text, job_title, company)
        result  = match_resume_to_jd(parsed, raw_text, jd_data, resume_id, 0)

        st.session_state.match_result = result
        st.session_state.jd_data      = jd_data
        st.session_state.job_title    = job_title
        st.session_state.company      = company

# ── Display results ───────────────────────────────────────────────────────────
if "match_result" not in st.session_state:
    st.stop()

result   = st.session_state.match_result
jd_data  = st.session_state.jd_data
scores   = result.get("scores") if isinstance(result.get("scores"), dict) else {
    "overall_match_score":      result.get("overall_match_score", 0),
    "skill_match_score":        result.get("skill_match_score", 0),
    "experience_match_score":   result.get("experience_match_score", 0),
    "education_match_score":    result.get("education_match_score", 0),
    "project_relevance_score":  result.get("project_relevance_score", 0),
    "keyword_match_score":      result.get("keyword_match_score", 0),
    "ats_compatibility":        result.get("ats_compatibility", 0),
}

overall = scores.get("overall_match_score", result.get("overall_match_score", 0))

st.markdown("---")
title_str = st.session_state.get("job_title") or "Job"
comp_str  = st.session_state.get("company") or ""
header    = f"**{title_str}**" + (f" — {comp_str}" if comp_str else "")
st.markdown(f"### 📊 Match Results · {header}")

# ── Overall gauge + breakdown ─────────────────────────────────────────────────
col_gauge, col_breakdown = st.columns([1, 1.4])

with col_gauge:
    color = score_color(overall)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall,
        number={"suffix":"%", "font":{"size":42,"color":"#e2e8f0"}},
        gauge={
            "axis":{"range":[0,100],"tickcolor":"#94a3b8","tickfont":{"color":"#94a3b8"}},
            "bar":{"color":color,"thickness":0.25},
            "bgcolor":"rgba(255,255,255,0.05)",
            "borderwidth":0,
            "steps":[
                {"range":[0,25],  "color":"rgba(239,68,68,0.15)"},
                {"range":[25,50], "color":"rgba(249,115,22,0.12)"},
                {"range":[50,75], "color":"rgba(245,158,11,0.12)"},
                {"range":[75,100],"color":"rgba(34,197,94,0.12)"},
            ],
            "threshold":{"line":{"color":color,"width":4},"thickness":0.8,"value":overall},
        },
        title={"text":"Overall Match Score","font":{"color":"#94a3b8","size":13}},
        domain={"x":[0,1],"y":[0,1]},
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=260, margin=dict(t=30,b=20,l=20,r=20))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f'<div style="text-align:center;"><span class="{score_color_class(overall)}" style="font-size:1.1rem;font-weight:700;">{score_label(overall)} Match</span></div>', unsafe_allow_html=True)

with col_breakdown:
    st.markdown("**Score Breakdown**")
    score_items = [
        ("Skill Match",       scores.get("skill_match_score",0)),
        ("Experience Match",  scores.get("experience_match_score",0)),
        ("Education Match",   scores.get("education_match_score",0)),
        ("Project Relevance", scores.get("project_relevance_score",0)),
        ("Keyword Match",     scores.get("keyword_match_score",0)),
        ("ATS Compatibility", scores.get("ats_compatibility",0)),
    ]
    for lbl, val in score_items:
        c = score_color(val)
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;margin-bottom:2px;">
          <span style="color:#cbd5e1;font-size:0.85rem;">{lbl}</span>
          <span style="color:{c};font-weight:700;font-size:0.85rem;">{val:.0f}%</span>
        </div>
        {progress_bar_html(val, c)}
        """, unsafe_allow_html=True)

# ── Scorecard row ─────────────────────────────────────────────────────────────
sc = result.get("scorecard")
if sc:
    sc_dict = sc.dict() if hasattr(sc, "dict") else sc
    st.markdown("### 🏆 Candidate Scorecard")
    cols = st.columns(4)
    for col, (label, key) in zip(cols, [
        ("ATS Score","ats_score"),("Resume Quality","resume_quality_score"),
        ("Tech Skills","technical_skill_score"),("Employability","employability_score"),
    ]):
        val = sc_dict.get(key, 0)
        col.markdown(metric_card_html(f"{val:.0f}", label, score_label(val), score_color_class(val)),
                     unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_skills, tab_gap, tab_recs, tab_radar = st.tabs([
    "⚙️ Skill Analysis", "🔍 Skill Gap", "💡 Recommendations", "📡 Radar Chart"
])

# Skills tab
with tab_skills:
    matched  = result.get("matched_skills", [])
    missing  = result.get("missing_skills", [])
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**✅ Matched Skills ({len(matched)})**")
        st.markdown("".join(f'<span class="pill-match">✓ {s}</span>' for s in matched) or "<i>None</i>",
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f"**❌ Missing Skills ({len(missing)})**")
        st.markdown("".join(f'<span class="pill-missing">✗ {s}</span>' for s in missing) or "<i>None — great match!</i>",
                    unsafe_allow_html=True)

    kw_opt = result.get("keyword_optimization", [])
    if kw_opt:
        st.markdown("---")
        st.markdown("**📝 ATS Keywords to Add to Resume**")
        st.markdown("".join(f'<span class="skill-tag tag-analytics">{k}</span>' for k in kw_opt),
                    unsafe_allow_html=True)

# Skill gap tab
with tab_gap:
    gap = result.get("skill_gap_analysis", [])
    if not gap:
        st.success("No significant skill gaps found!")
    else:
        st.markdown(f'<div class="warn-box">⚠️ <strong>{len(gap)} skill gap(s)</strong> identified. Expand each to see the recommended learning path.</div>', unsafe_allow_html=True)
        for item in gap:
            item_dict = item.dict() if hasattr(item, "dict") else item
            pri = item_dict.get("priority","Medium")
            pri_color = "#ef4444" if pri=="High" else "#f59e0b" if pri=="Medium" else "#94a3b8"
            with st.expander(f"🔴 {item_dict['skill']}  ·  {item_dict.get('category','')}  ·  Priority: {pri}"):
                lp = item_dict.get("learning_path", [])
                for i, step in enumerate(lp, 1):
                    s = step.dict() if hasattr(step, "dict") else step
                    lvl_color = {"Beginner":"#22c55e","Intermediate":"#3b82f6","Advanced":"#a855f7"}.get(s.get("level",""),"#94a3b8")
                    st.markdown(f"""
                    <div style="display:flex;gap:0.75rem;align-items:flex-start;padding:0.5rem;border-radius:8px;background:rgba(255,255,255,0.03);margin-bottom:0.4rem;">
                      <div style="width:24px;height:24px;background:rgba(99,102,241,0.2);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;color:#818cf8;flex-shrink:0;">{i}</div>
                      <div>
                        <div style="color:#e2e8f0;font-weight:600;font-size:0.88rem;">{s.get('title','')}</div>
                        <div style="font-size:0.78rem;margin-top:2px;">
                          <span style="color:{lvl_color};font-weight:600;">{s.get('level','')}</span>
                          {(' · ' + s['platform']) if s.get('platform') else ''}
                        </div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

# Recommendations tab
with tab_recs:
    recs = result.get("recommendations", [])
    sugs = result.get("improvement_suggestions", [])
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**💡 Recommendations**")
        for i, r in enumerate(recs, 1):
            st.markdown(f"""
            <div class="glass-card-sm" style="display:flex;gap:0.75rem;">
              <span style="color:#818cf8;font-weight:700;font-size:0.85rem;flex-shrink:0;">{str(i).zfill(2)}</span>
              <span style="color:#cbd5e1;font-size:0.85rem;">{r}</span>
            </div>
            """, unsafe_allow_html=True)
    with c2:
        st.markdown("**✏️ Resume Improvement Suggestions**")
        for s in sugs:
            st.markdown(f"""
            <div class="glass-card-sm" style="display:flex;gap:0.75rem;align-items:flex-start;">
              <span style="color:#22c55e;flex-shrink:0;">✓</span>
              <span style="color:#cbd5e1;font-size:0.85rem;">{s}</span>
            </div>
            """, unsafe_allow_html=True)

# Radar tab
with tab_radar:
    labels = ["Skills","Experience","Education","Projects","Keywords","ATS"]
    vals   = [
        scores.get("skill_match_score",0), scores.get("experience_match_score",0),
        scores.get("education_match_score",0), scores.get("project_relevance_score",0),
        scores.get("keyword_match_score",0), scores.get("ats_compatibility",0),
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=vals + [vals[0]], theta=labels + [labels[0]],
        fill='toself', fillcolor='rgba(99,102,241,0.15)',
        line=dict(color='#6366f1', width=2), name="Match Score"
    ))
    fig.add_trace(go.Scatterpolar(
        r=[100]*7, theta=labels + [labels[0]],
        fill='toself', fillcolor='rgba(255,255,255,0.02)',
        line=dict(color='rgba(255,255,255,0.1)', width=1, dash='dot'), name="Max"
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0,100], tickfont=dict(color='#94a3b8'), gridcolor='rgba(255,255,255,0.08)'),
                   angularaxis=dict(tickfont=dict(color='#e2e8f0')), bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#e2e8f0'),
        legend=dict(font=dict(color='#94a3b8')), height=380, margin=dict(t=30,b=20,l=30,r=30),
        title=dict(text="Match Profile Radar", font=dict(color='#e2e8f0'), x=0.5),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── PDF Report button ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📑 Download Report")
if st.button("📄 Generate PDF Report", use_container_width=True):
    with st.spinner("Generating PDF…"):
        try:
            from services.report_generator import generate_match_report_pdf
            parsed_data = st.session_state.parsed
            candidate_dict = {
                "full_name": parsed_data.full_name, "email": parsed_data.email,
                "phone": parsed_data.phone, "linkedin_url": parsed_data.linkedin_url,
                "github_url": parsed_data.github_url,
                "total_experience_years": parsed_data.total_experience_years,
            }
            sc_dict_raw = result.get("scorecard")
            sc_for_pdf  = sc_dict_raw.dict() if hasattr(sc_dict_raw,"dict") else (sc_dict_raw or {})
            report_data = {
                "resume_id": st.session_state.get("resume_id", 0),
                "candidate": candidate_dict,
                "overall_match_score":     scores.get("overall_match_score",0),
                "skill_match_score":       scores.get("skill_match_score",0),
                "experience_match_score":  scores.get("experience_match_score",0),
                "education_match_score":   scores.get("education_match_score",0),
                "project_relevance_score": scores.get("project_relevance_score",0),
                "keyword_match_score":     scores.get("keyword_match_score",0),
                "matched_skills":  result.get("matched_skills",[]),
                "missing_skills":  result.get("missing_skills",[]),
                "skill_gap_analysis": [
                    (g.dict() if hasattr(g,"dict") else g)
                    for g in result.get("skill_gap_analysis",[])
                ],
                "recommendations":         result.get("recommendations",[]),
                "improvement_suggestions": result.get("improvement_suggestions",[]),
                "scorecard": sc_for_pdf,
            }
            os.makedirs("uploads/reports", exist_ok=True)
            pdf_path = generate_match_report_pdf(report_data, output_dir="uploads/reports")
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=f.read(),
                    file_name=f"match_report_{st.session_state.get('resume_id',0)}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            st.success("PDF ready!")
        except Exception as e:
            st.error(f"PDF generation failed: {e}")
