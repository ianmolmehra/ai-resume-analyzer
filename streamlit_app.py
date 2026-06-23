import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

import streamlit as st
import tempfile
from pathlib import Path

from utils.styles import GLOBAL_CSS, skill_tags_html, metric_card_html, score_color_class, score_label, progress_bar_html

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.6rem;padding:0.5rem 0 1.2rem;">
      <div style="width:36px;height:36px;background:linear-gradient(135deg,#6366f1,#4f46e5);
           border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;">🧠</div>
      <div>
        <div style="font-weight:700;color:#e2e8f0;font-size:0.95rem;">AI Resume Analyzer</div>
        <div style="color:#6366f1;font-size:0.72rem;font-weight:600;">v1.0 · Production</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-size:0.7rem;color:#64748b;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.4rem;">Navigation</div>', unsafe_allow_html=True)
    st.page_link("streamlit_app.py",         label="🏠  Upload Resume",   )
    st.page_link("pages/1_Analysis.py",      label="📄  Resume Analysis" )
    st.page_link("pages/2_Matching.py",      label="🎯  Job Matching"    )
    st.page_link("pages/3_Dashboard.py",     label="📊  Analytics"       )
    st.page_link("pages/4_Admin.py",         label="🛡️  Admin Panel"     )

    st.markdown("---")
    if "resume_id" in st.session_state:
        st.success(f"Resume loaded: #{st.session_state.resume_id}")
    else:
        st.info("No resume loaded yet")

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 1.5rem;">
  <div style="display:inline-flex;align-items:center;gap:0.5rem;background:rgba(99,102,241,0.1);
       border:1px solid rgba(99,102,241,0.25);border-radius:999px;padding:0.3rem 1rem;
       color:#818cf8;font-size:0.82rem;font-weight:600;margin-bottom:1rem;">
    ⚡ AI-Powered Resume Intelligence
  </div>
  <h1 style="font-size:2.4rem;font-weight:800;color:#e2e8f0;margin:0;line-height:1.2;">
    Analyze Your Resume.<br>
    <span style="background:linear-gradient(135deg,#818cf8,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
      Land Your Dream Job.
    </span>
  </h1>
  <p style="color:#94a3b8;font-size:1rem;margin-top:0.75rem;max-width:520px;margin-left:auto;margin-right:auto;">
    Upload your PDF or DOCX resume for instant AI-powered skill extraction,
    candidate scoring, and job match analysis.
  </p>
</div>
""", unsafe_allow_html=True)

# ── Upload card ───────────────────────────────────────────────────────────────
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### 📤 Upload Your Resume")

uploaded_file = st.file_uploader(
    "Drag & drop or click to browse",
    type=["pdf", "docx"],
    help="Max 10MB · PDF or DOCX only",
    label_visibility="visible",
)

if uploaded_file:
    size_kb = len(uploaded_file.getvalue()) / 1024
    st.markdown(f"""
    <div class="glass-card-sm" style="border-color:rgba(99,102,241,0.3);margin-top:0.5rem;">
      <span style="color:#818cf8;font-weight:600;">✓ {uploaded_file.name}</span>
      &nbsp;·&nbsp; <span style="color:#94a3b8;">{size_kb:.1f} KB</span>
      &nbsp;·&nbsp; <span style="color:#94a3b8;">{uploaded_file.type.split('/')[-1].upper()}</span>
    </div>
    """, unsafe_allow_html=True)

analyze_btn = st.button("🧠 Analyze Resume", use_container_width=True, disabled=not uploaded_file)
st.markdown('</div>', unsafe_allow_html=True)

# ── Process ───────────────────────────────────────────────────────────────────
if analyze_btn and uploaded_file:
    ext = Path(uploaded_file.name).suffix.lower()
    if ext not in [".pdf", ".docx"]:
        st.error("Only PDF and DOCX files are supported.")
        st.stop()
    if len(uploaded_file.getvalue()) > 10 * 1024 * 1024:
        st.error("File is too large. Max 10 MB.")
        st.stop()

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    with st.spinner("Parsing resume and extracting skills…"):
        try:
            from services.resume_parser import parse_resume, extract_text
            from services.skill_extractor import extract_skills
            from services.matching_engine import (
                compute_resume_quality, compute_technical_score,
                compute_ats_score, compute_employability
            )

            parsed = parse_resume(tmp_path)
            raw_text = extract_text(tmp_path)
            skills = extract_skills(raw_text)
            parsed.skills = skills

            quality   = compute_resume_quality(parsed, raw_text)
            tech      = compute_technical_score(skills, raw_text)
            ats       = compute_ats_score(raw_text, parsed, [])
            employ    = compute_employability(tech, 50, 70, quality)

            # Persist to SQLite
            from utils.db_helper import get_db_session
            from models import Candidate, Resume, Skill, CandidateSkill
            db = get_db_session()
            candidate = None
            if parsed.email:
                candidate = db.query(Candidate).filter(Candidate.email == parsed.email).first()
            if not candidate:
                candidate = Candidate(
                    full_name=parsed.full_name or "Unknown",
                    email=parsed.email, phone=parsed.phone,
                    linkedin_url=parsed.linkedin_url, github_url=parsed.github_url,
                )
                db.add(candidate); db.flush()

            resume_rec = Resume(
                candidate_id=candidate.id,
                filename=uploaded_file.name,
                file_path=tmp_path,
                file_type=ext,
                file_size_kb=len(uploaded_file.getvalue())/1024,
                raw_text=raw_text[:50000],
                education=[e.dict() for e in parsed.education],
                experience=[e.dict() for e in parsed.experience],
                projects=[p.dict() for p in parsed.projects],
                certifications=[c.dict() for c in parsed.certifications],
                ats_score=ats, resume_quality_score=quality,
                technical_skill_score=tech, employability_score=employ,
                total_experience_years=parsed.total_experience_years,
                highest_education=parsed.highest_education, status="parsed",
            )
            db.add(resume_rec); db.flush()

            for sk in skills:
                skill_rec = db.query(Skill).filter(Skill.name == sk.name).first()
                if not skill_rec:
                    skill_rec = Skill(name=sk.name, category=sk.category)
                    db.add(skill_rec); db.flush()
                if not db.query(CandidateSkill).filter_by(candidate_id=candidate.id, skill_id=skill_rec.id).first():
                    db.add(CandidateSkill(candidate_id=candidate.id, skill_id=skill_rec.id,
                        confidence_score=sk.confidence_score, proficiency_level=sk.proficiency_level))
            db.commit()
            resume_id = resume_rec.id
            db.close()

            # Store in session
            st.session_state.resume_id     = resume_id
            st.session_state.parsed        = parsed
            st.session_state.raw_text      = raw_text
            st.session_state.skills        = [s.dict() for s in skills]
            st.session_state.scorecard     = {
                "ats_score": ats, "resume_quality_score": quality,
                "technical_skill_score": tech, "employability_score": employ,
            }
            st.session_state.filename      = uploaded_file.name
            os.unlink(tmp_path)

        except Exception as e:
            st.error(f"Parsing failed: {e}")
            st.stop()

    st.success(f"✅ Resume parsed! Found **{len(skills)} skills**.")

    # Quick preview scorecard
    sc = st.session_state.scorecard
    cols = st.columns(4)
    for col, (label, key) in zip(cols, [
        ("ATS Score","ats_score"),("Resume Quality","resume_quality_score"),
        ("Tech Skills","technical_skill_score"),("Employability","employability_score"),
    ]):
        val = sc[key]
        col.markdown(metric_card_html(
            f"{val:.0f}", label, score_label(val), score_color_class(val)
        ), unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
      ✅ Resume ready! Use the sidebar to view full <strong>Analysis</strong> or run <strong>Job Matching</strong>.
    </div>
    """, unsafe_allow_html=True)

# ── Features grid ─────────────────────────────────────────────────────────────
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
for col, icon, title, desc in [
    (c1, "📄", "Smart Parsing",   "Extracts name, contact, education, skills, experience & projects"),
    (c2, "🧠", "Skill Detection", "100+ skills across Programming, AI/ML, Cloud, DevOps & more"),
    (c3, "🎯", "Job Matching",    "Match score, skill gap, ATS compatibility & learning paths"),
    (c4, "📊", "Analytics",       "Candidate scorecard, leaderboard, skill distribution charts"),
]:
    col.markdown(f"""
    <div class="glass-card-sm" style="text-align:center;padding:1.25rem;">
      <div style="font-size:1.6rem;margin-bottom:0.5rem;">{icon}</div>
      <div style="font-weight:700;color:#e2e8f0;font-size:0.9rem;">{title}</div>
      <div style="color:#94a3b8;font-size:0.78rem;margin-top:0.3rem;">{desc}</div>
    </div>
    """, unsafe_allow_html=True)
