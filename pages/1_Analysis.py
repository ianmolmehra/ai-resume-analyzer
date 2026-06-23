import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.styles import (GLOBAL_CSS, skill_tags_html, metric_card_html,
                           score_color_class, score_label, progress_bar_html, score_color)

st.set_page_config(page_title="Resume Analysis · AI Analyzer", page_icon="📄", layout="wide")
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

# ── Guard ─────────────────────────────────────────────────────────────────────
if "parsed" not in st.session_state:
    st.warning("No resume loaded. Please upload one first.")
    st.page_link("streamlit_app.py", label="← Go to Upload")
    st.stop()

parsed   = st.session_state.parsed
skills   = st.session_state.get("skills", [])
sc       = st.session_state.get("scorecard", {})
filename = st.session_state.get("filename", "resume")

# ── Header ────────────────────────────────────────────────────────────────────
name = parsed.full_name or "Candidate"
st.markdown(f"""
<div style="margin-bottom:1.5rem;">
  <h1 style="font-size:1.8rem;font-weight:800;color:#e2e8f0;margin:0;">{name}</h1>
  <p style="color:#94a3b8;margin:0.25rem 0 0;">{filename} · {len(skills)} skills extracted</p>
</div>
""", unsafe_allow_html=True)

col_btn1, col_btn2 = st.columns([1,5])
with col_btn1:
    if st.button("🎯 Match to Job"):
        st.switch_page("pages/2_Matching.py")

st.markdown("---")

# ── Scorecard ─────────────────────────────────────────────────────────────────
st.markdown("### 🏆 Candidate Scorecard")
cols = st.columns(4)
for col, (label, key) in zip(cols, [
    ("ATS Score","ats_score"),("Resume Quality","resume_quality_score"),
    ("Technical Skills","technical_skill_score"),("Employability","employability_score"),
]):
    val = sc.get(key, 0)
    col.markdown(metric_card_html(f"{val:.0f}", label, score_label(val), score_color_class(val)),
                 unsafe_allow_html=True)

st.markdown("")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_profile, tab_skills, tab_edu, tab_exp, tab_proj, tab_certs = st.tabs([
    "👤 Profile", "⚙️ Skills", "🎓 Education", "💼 Experience", "🗂 Projects", "🏅 Certifications"
])

# ── Profile Tab ───────────────────────────────────────────────────────────────
with tab_profile:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Contact Information")
        rows = [
            ("Full Name",   parsed.full_name),
            ("Email",       parsed.email),
            ("Phone",       parsed.phone),
            ("LinkedIn",    parsed.linkedin_url),
            ("GitHub",      parsed.github_url),
            ("Location",    parsed.location),
        ]
        for label, val in rows:
            if val:
                st.markdown(f"**{label}:** {val}")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Career Summary")
        if parsed.total_experience_years:
            st.metric("Total Experience", f"{parsed.total_experience_years:.1f} years")
        if parsed.highest_education:
            st.metric("Highest Education", parsed.highest_education)
        if parsed.summary:
            st.markdown(f"*{parsed.summary}*")
        else:
            st.info("No summary section detected in resume.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Scorecard gauge chart
    if sc:
        fig = go.Figure(go.Scatterpolar(
            r=[sc.get("ats_score",0), sc.get("resume_quality_score",0),
               sc.get("technical_skill_score",0), sc.get("employability_score",0), sc.get("ats_score",0)],
            theta=["ATS Score","Resume Quality","Technical Skills","Employability","ATS Score"],
            fill='toself', fillcolor='rgba(99,102,241,0.15)',
            line=dict(color='#6366f1', width=2),
            name="Score"
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(range=[0,100], showticklabels=True, gridcolor='rgba(255,255,255,0.1)',
                                       tickfont=dict(color='#94a3b8')),
                       angularaxis=dict(tickfont=dict(color='#94a3b8')),
                       bgcolor='rgba(0,0,0,0)'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'), showlegend=False,
            title=dict(text="Score Profile Radar", font=dict(color='#e2e8f0'), x=0.5),
            margin=dict(t=60,b=20,l=20,r=20), height=320,
        )
        st.plotly_chart(fig, use_container_width=True)

# ── Skills Tab ────────────────────────────────────────────────────────────────
with tab_skills:
    if not skills:
        st.info("No skills detected. The resume may need better formatting.")
        st.stop()

    # Category filter
    categories = sorted(set(s["category"] for s in skills))
    selected_cat = st.selectbox("Filter by category", ["All"] + categories)
    filtered = skills if selected_cat == "All" else [s for s in skills if s["category"] == selected_cat]

    st.markdown(f"**{len(filtered)} skills** {('in ' + selected_cat) if selected_cat != 'All' else 'total'}")
    st.markdown(skill_tags_html(filtered), unsafe_allow_html=True)
    st.markdown("")

    # Category bar chart
    cat_counts = {}
    for s in skills:
        cat_counts[s["category"]] = cat_counts.get(s["category"], 0) + 1
    df_cat = pd.DataFrame(list(cat_counts.items()), columns=["Category","Count"]).sort_values("Count", ascending=True)
    COLORS = {"Programming":"#6366f1","Database":"#3b82f6","Data Analytics":"#f59e0b",
              "AI/ML":"#22c55e","Cloud":"#06b6d4","DevOps":"#f97316","Framework":"#a855f7","Other":"#64748b"}
    fig2 = px.bar(df_cat, x="Count", y="Category", orientation="h",
                  color="Category", color_discrete_map=COLORS, title="Skills by Category")
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font=dict(color='#e2e8f0'), showlegend=False,
                       yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                       xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                       title_font=dict(color='#e2e8f0'), margin=dict(t=40,b=20,l=20,r=20), height=280)
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)

    # Top skills by confidence
    top_skills = sorted(skills, key=lambda x: x["confidence_score"], reverse=True)[:15]
    df_top = pd.DataFrame(top_skills)[["name","confidence_score","category"]]
    df_top["confidence_score"] = (df_top["confidence_score"] * 100).round(1)
    df_top.columns = ["Skill","Confidence (%)","Category"]
    st.dataframe(df_top, use_container_width=True, hide_index=True)

# ── Education Tab ─────────────────────────────────────────────────────────────
with tab_edu:
    edu_list = parsed.education
    if not edu_list:
        st.info("No education details detected.")
    else:
        for edu in edu_list:
            st.markdown(f"""
            <div class="glass-card-sm">
              <div style="font-weight:700;color:#818cf8;font-size:1rem;">{edu.degree or 'Degree'}</div>
              <div style="color:#e2e8f0;font-size:0.9rem;">{edu.university or ''}</div>
              <div style="color:#94a3b8;font-size:0.82rem;margin-top:0.2rem;">
                {('Class of ' + edu.graduation_year) if edu.graduation_year else ''}
                {(' · GPA: ' + edu.gpa) if edu.gpa else ''}
              </div>
            </div>
            """, unsafe_allow_html=True)

# ── Experience Tab ────────────────────────────────────────────────────────────
with tab_exp:
    exp_list = parsed.experience
    if not exp_list:
        st.info("No work experience detected.")
    else:
        for exp in exp_list:
            st.markdown(f"""
            <div class="glass-card-sm">
              <div style="font-weight:700;color:#e2e8f0;">{exp.role or 'Role'}</div>
              {f'<div style="color:#818cf8;font-size:0.88rem;">{exp.company}</div>' if exp.company else ''}
              {f'<div style="color:#94a3b8;font-size:0.8rem;">{exp.duration}</div>' if exp.duration else ''}
              {f'<div style="color:#cbd5e1;font-size:0.85rem;margin-top:0.4rem;">{exp.description[:300]}...</div>' if exp.description else ''}
            </div>
            """, unsafe_allow_html=True)

# ── Projects Tab ──────────────────────────────────────────────────────────────
with tab_proj:
    proj_list = parsed.projects
    if not proj_list:
        st.info("No projects detected.")
    else:
        for proj in proj_list:
            techs = "".join(f'<span class="skill-tag tag-programming">{t}</span>' for t in (proj.tech_stack or []))
            st.markdown(f"""
            <div class="glass-card-sm">
              <div style="font-weight:700;color:#e2e8f0;">{proj.name or 'Project'}</div>
              {f'<div style="color:#94a3b8;font-size:0.85rem;margin:0.3rem 0;">{proj.description[:250]}</div>' if proj.description else ''}
              <div style="margin-top:0.4rem;">{techs}</div>
            </div>
            """, unsafe_allow_html=True)

# ── Certifications Tab ────────────────────────────────────────────────────────
with tab_certs:
    cert_list = parsed.certifications
    if not cert_list:
        st.info("No certifications detected.")
    else:
        for cert in cert_list:
            st.markdown(f"""
            <div class="glass-card-sm" style="display:flex;justify-content:space-between;align-items:center;">
              <div>
                <div style="font-weight:600;color:#e2e8f0;">{cert.name or 'Certification'}</div>
                {f'<div style="color:#94a3b8;font-size:0.8rem;">{cert.issuer}</div>' if cert.issuer else ''}
              </div>
              {f'<span style="color:#818cf8;font-size:0.85rem;font-weight:600;">{cert.year}</span>' if cert.year else ''}
            </div>
            """, unsafe_allow_html=True)
