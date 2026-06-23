import sys, os
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "backend"))

import streamlit as st
import pandas as pd
from utils.styles import GLOBAL_CSS, metric_card_html, score_color_class

st.set_page_config(page_title="Admin · AI Analyzer", page_icon="🛡️", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🧠 AI Resume Analyzer")
    st.page_link("streamlit_app.py",     label="🏠  Upload Resume")
    st.page_link("pages/1_Analysis.py",  label="📄  Resume Analysis")
    st.page_link("pages/2_Matching.py",  label="🎯  Job Matching")
    st.page_link("pages/3_Dashboard.py", label="📊  Analytics")
    st.page_link("pages/4_Admin.py",     label="🛡️  Admin Panel")

st.markdown("## 🛡️ Admin Panel")
st.markdown("Manage all resumes, match reports, and platform data.")

@st.cache_data(ttl=15)
def load_admin_data():
    try:
        from utils.db_helper import get_db_session
        from models import Resume, Candidate, Skill, CandidateSkill
        from models.match_report import MatchReport
        from models.job_description import JobDescription
        from sqlalchemy import func, desc
        
        db = get_db_session()

        stats = {
            "resumes":    db.query(Resume).count(),
            "candidates": db.query(Candidate).count(),
            "skills":     db.query(Skill).count(),
            "matches":    db.query(MatchReport).count(),
            "jds":        db.query(JobDescription).count(),
            "avg_ats":    round(db.query(func.avg(Resume.ats_score)).scalar() or 0, 1),
            "avg_match":  round(db.query(func.avg(MatchReport.overall_match_score)).scalar() or 0, 1),
        }

        resumes_q = (
            db.query(Resume, Candidate)
            .join(Candidate, Resume.candidate_id == Candidate.id)
            .order_by(desc(Resume.created_at)).all()
        )
        resumes = [{
            "id": r.Resume.id, "name": r.Candidate.full_name,
            "email": r.Candidate.email, "file": r.Resume.filename,
            "type": r.Resume.file_type, "ats": r.Resume.ats_score,
            "quality": r.Resume.resume_quality_score,
            "tech": r.Resume.technical_skill_score,
            "employ": r.Resume.employability_score,
            "exp_yrs": r.Resume.total_experience_years,
            "edu": r.Resume.highest_education or "",
            "status": r.Resume.status,
            "created": str(r.Resume.created_at)[:10] if r.Resume.created_at else "",
        } for r in resumes_q]

        reports_q = db.query(MatchReport).order_by(desc(MatchReport.created_at)).limit(50).all()
        reports = []
        for rp in reports_q:
            res = db.query(Resume).filter(Resume.id == rp.resume_id).first()
            cand = db.query(Candidate).filter(Candidate.id == res.candidate_id).first() if res else None
            jd   = db.query(JobDescription).filter(JobDescription.id == rp.job_description_id).first()
            reports.append({
                "id": rp.id, "candidate": cand.full_name if cand else "N/A",
                "job": jd.title if jd else "N/A", "company": jd.company if jd else "",
                "overall": rp.overall_match_score, "skill": rp.skill_match_score,
                "exp": rp.experience_match_score, "ats": rp.ats_compatibility,
                "created": str(rp.created_at)[:10] if rp.created_at else "",
            })

        skills_q = (
            db.query(Skill.name, Skill.category, func.count(CandidateSkill.id).label("cnt"))
            .join(CandidateSkill, Skill.id == CandidateSkill.skill_id)
            .group_by(Skill.id, Skill.name, Skill.category)
            .order_by(desc("cnt")).all()
        )
        skills = [{"Skill": s.name, "Category": s.category, "Candidates": s.cnt} for s in skills_q]

        db.close()
        return {"stats": stats, "resumes": resumes, "reports": reports, "skills": skills, "ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

col_refresh, _ = st.columns([1, 5])
with col_refresh:
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()

data = load_admin_data()

if not data["ok"]:
    st.warning(f"Database not connected — admin features require MySQL. ({data.get('error','')})")
    st.markdown("""
    <div class="info-box">
      Start MySQL and run the app with a valid <code>.env</code> to enable admin features.<br>
      See <strong>README.md</strong> for setup instructions.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

stats = data["stats"]

# ── Stats row ──────────────────────────────────────────────────────────────────
st.markdown("### Platform Summary")
c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
for col, label, val, cc in [
    (c1, "Resumes",    stats["resumes"],    "score-high"),
    (c2, "Candidates", stats["candidates"], "score-high"),
    (c3, "Skills",     stats["skills"],     "score-mid"),
    (c4, "Matches",    stats["matches"],    "score-mid"),
    (c5, "JDs",        stats["jds"],        "score-mid"),
    (c6, "Avg ATS",    f"{stats['avg_ats']}%",   "score-mid"),
    (c7, "Avg Match",  f"{stats['avg_match']}%", "score-mid"),
]:
    col.markdown(metric_card_html(val, label, color_class=cc), unsafe_allow_html=True)

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_resumes, tab_reports, tab_skills = st.tabs(["📄 Resumes", "📊 Match Reports", "⚙️ Skills"])

# ── Resumes tab ────────────────────────────────────────────────────────────────
with tab_resumes:
    resumes = data["resumes"]
    st.markdown(f"**{len(resumes)} resumes** in the system")

    # Search
    search = st.text_input("🔍 Search by name or email", placeholder="Type to filter…")
    if search:
        sl = search.lower()
        resumes = [r for r in resumes if sl in r["name"].lower() or sl in (r["email"] or "").lower()]

    if resumes:
        df = pd.DataFrame(resumes)
        df = df[["id","name","email","file","ats","quality","tech","employ","exp_yrs","edu","status","created"]]
        df.columns = ["ID","Name","Email","File","ATS%","Quality%","Tech%","Employ%","Exp(yrs)","Education","Status","Date"]
        for pct_col in ["ATS%","Quality%","Tech%","Employ%"]:
            df[pct_col] = df[pct_col].apply(lambda x: round(x or 0, 1))
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Delete action
        st.markdown("---")
        st.markdown("**Delete a resume**")
        del_col1, del_col2 = st.columns([1, 3])
        with del_col1:
            del_id = st.number_input("Resume ID to delete", min_value=1, step=1)
        with del_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Delete Resume", type="primary"):
                try:
                    from database import SessionLocal
                    from models import Resume, CandidateSkill
                    from models.match_report import MatchReport
                    db = get_db_session()
                    resume = db.query(Resume).filter(Resume.id == del_id).first()
                    if resume:
                        db.query(MatchReport).filter(MatchReport.resume_id == del_id).delete()
                        db.delete(resume)
                        db.commit()
                        st.success(f"Resume #{del_id} deleted.")
                        st.cache_data.clear()
                    else:
                        st.error("Resume not found.")
                    db.close()
                except Exception as e:
                    st.error(f"Delete failed: {e}")
    else:
        st.info("No resumes match your search.")

# ── Match Reports tab ──────────────────────────────────────────────────────────
with tab_reports:
    reports = data["reports"]
    st.markdown(f"**{len(reports)} match reports** (latest 50)")
    if reports:
        df_r = pd.DataFrame(reports)
        df_r = df_r[["id","candidate","job","company","overall","skill","exp","ats","created"]]
        df_r.columns = ["ID","Candidate","Job Title","Company","Overall%","Skill%","Exp%","ATS%","Date"]
        for c in ["Overall%","Skill%","Exp%","ATS%"]:
            df_r[c] = df_r[c].apply(lambda x: round(x or 0, 1))

        # Highlight overall score
        def highlight_score(val):
            try:
                v = float(val)
                if v >= 75: return "color: #22c55e; font-weight: 600"
                if v >= 50: return "color: #f59e0b; font-weight: 600"
                return "color: #ef4444; font-weight: 600"
            except: return ""

        st.dataframe(df_r.style.applymap(highlight_score, subset=["Overall%"]),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No match reports yet. Run a job matching analysis first.")

# ── Skills tab ─────────────────────────────────────────────────────────────────
with tab_skills:
    skills = data["skills"]
    st.markdown(f"**{len(skills)} unique skills** detected across all resumes")
    if skills:
        cat_filter = st.selectbox("Filter by category",
            ["All"] + sorted(set(s["Category"] for s in skills)))
        filtered = skills if cat_filter == "All" else [s for s in skills if s["Category"] == cat_filter]
        st.dataframe(pd.DataFrame(filtered), use_container_width=True, hide_index=True)
    else:
        st.info("No skills data yet.")
