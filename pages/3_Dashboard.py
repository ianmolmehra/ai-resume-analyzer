import sys, os
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "backend"))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.styles import GLOBAL_CSS, metric_card_html, score_color_class, score_label

st.set_page_config(page_title="Analytics · AI Analyzer", page_icon="📊", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🧠 AI Resume Analyzer")
    st.page_link("streamlit_app.py",     label="🏠  Upload Resume")
    st.page_link("pages/1_Analysis.py",  label="📄  Resume Analysis")
    st.page_link("pages/2_Matching.py",  label="🎯  Job Matching")
    st.page_link("pages/3_Dashboard.py", label="📊  Analytics")
    st.page_link("pages/4_Admin.py",     label="🛡️  Admin Panel")

st.markdown("## 📊 Analytics Dashboard")
st.markdown("Platform-wide insights across all uploaded resumes and match reports.")

# ── Load from DB ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_analytics():
    try:
        from utils.db_helper import get_db_session
        from models import Resume, Candidate, Skill, CandidateSkill
        from models.match_report import MatchReport
        from sqlalchemy import func, desc
        
        db = get_db_session()

        total_resumes    = db.query(Resume).count()
        total_candidates = db.query(Candidate).count()
        total_matches    = db.query(MatchReport).count()
        avg_match = db.query(func.avg(MatchReport.overall_match_score)).scalar() or 0
        avg_ats   = db.query(func.avg(Resume.ats_score)).scalar() or 0

        top_skills_q = (
            db.query(Skill.name, Skill.category, func.count(CandidateSkill.id).label("count"))
            .join(CandidateSkill, Skill.id == CandidateSkill.skill_id)
            .group_by(Skill.id, Skill.name, Skill.category)
            .order_by(desc("count")).limit(20).all()
        )
        top_skills = [{"name":s.name,"category":s.category,"count":s.count} for s in top_skills_q]

        cat_dist_q = (
            db.query(Skill.category, func.count(CandidateSkill.id).label("count"))
            .join(CandidateSkill, Skill.id == CandidateSkill.skill_id)
            .group_by(Skill.category).all()
        )
        skill_dist = {c.category: c.count for c in cat_dist_q}

        edu_counts = {}
        for r in db.query(Resume.highest_education).all():
            k = r.highest_education or "Unknown"
            edu_counts[k] = edu_counts.get(k, 0) + 1

        match_dist = {"0-25":0,"26-50":0,"51-75":0,"76-100":0}
        for m in db.query(MatchReport.overall_match_score).all():
            s = m.overall_match_score or 0
            if s <= 25: match_dist["0-25"] += 1
            elif s <= 50: match_dist["26-50"] += 1
            elif s <= 75: match_dist["51-75"] += 1
            else: match_dist["76-100"] += 1

        recent = (
            db.query(Resume, Candidate).join(Candidate, Resume.candidate_id == Candidate.id)
            .order_by(desc(Resume.created_at)).limit(10).all()
        )
        recent_data = [{
            "id": r.Resume.id, "name": r.Candidate.full_name,
            "email": r.Candidate.email, "ats": r.Resume.ats_score,
            "employability": r.Resume.employability_score,
            "created": str(r.Resume.created_at)[:10] if r.Resume.created_at else "",
        } for r in recent]

        top_cands = (
            db.query(Resume, Candidate).join(Candidate, Resume.candidate_id == Candidate.id)
            .order_by(desc(Resume.employability_score)).limit(10).all()
        )
        leaderboard = [{
            "rank": i+1, "id": r.Resume.id, "name": r.Candidate.full_name,
            "email": r.Candidate.email,
            "employability": r.Resume.employability_score,
            "ats": r.Resume.ats_score,
            "tech": r.Resume.technical_skill_score,
        } for i, r in enumerate(top_cands)]

        db.close()
        return {
            "total_resumes": total_resumes, "total_candidates": total_candidates,
            "total_matches": total_matches, "avg_match": round(avg_match,1),
            "avg_ats": round(avg_ats,1), "top_skills": top_skills,
            "skill_dist": skill_dist, "edu_counts": edu_counts,
            "match_dist": match_dist, "recent": recent_data,
            "leaderboard": leaderboard, "db_connected": True,
        }
    except Exception as e:
        return {"db_connected": False, "error": str(e)}

if st.button("🔄 Refresh"):
    st.cache_data.clear()

data = load_analytics()

if not data.get("db_connected"):
    st.info("No data yet — upload a resume to populate the dashboard.")
    # Inject demo data
    data = {
        "total_resumes": 12, "total_candidates": 10, "total_matches": 8,
        "avg_match": 71.4, "avg_ats": 65.2, "db_connected": False,
        "top_skills": [
            {"name":"Python","category":"Programming","count":9},
            {"name":"SQL","category":"Database","count":8},
            {"name":"Machine Learning","category":"AI/ML","count":7},
            {"name":"AWS","category":"Cloud","count":6},
            {"name":"Docker","category":"DevOps","count":5},
            {"name":"React","category":"Framework","count":5},
            {"name":"TensorFlow","category":"AI/ML","count":4},
            {"name":"PostgreSQL","category":"Database","count":4},
        ],
        "skill_dist": {"Programming":18,"AI/ML":12,"Database":10,"Cloud":8,"DevOps":7,"Framework":9},
        "edu_counts": {"Bachelor's":6,"Master's":3,"PhD":1,"B.Tech":2},
        "match_dist": {"0-25":1,"26-50":2,"51-75":3,"76-100":2},
        "recent": [], "leaderboard": [],
    }

# ── Summary Metrics ────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
c1.markdown(metric_card_html(data["total_resumes"],   "Total Resumes",   "Uploaded",        "score-high"),  unsafe_allow_html=True)
c2.markdown(metric_card_html(data["total_candidates"],"Candidates",      "Registered",      "score-high"),  unsafe_allow_html=True)
c3.markdown(metric_card_html(data["total_matches"],   "Match Reports",   "Generated",       "score-mid"),   unsafe_allow_html=True)
c4.markdown(metric_card_html(f"{data['avg_match']}%", "Avg Match Score", "Across reports",  "score-mid"),   unsafe_allow_html=True)
c5.markdown(metric_card_html(f"{data['avg_ats']}%",   "Avg ATS Score",   "Across resumes",  "score-mid"),   unsafe_allow_html=True)

st.markdown("---")

# ── Charts row 1 ──────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

COLORS = {"Programming":"#6366f1","Database":"#3b82f6","Data Analytics":"#f59e0b",
          "AI/ML":"#22c55e","Cloud":"#06b6d4","DevOps":"#f97316","Framework":"#a855f7","Other":"#64748b"}

with col1:
    st.markdown("#### 🔥 Top Skills in Demand")
    top = data["top_skills"][:12]
    df = pd.DataFrame(top).sort_values("count")
    fig = px.bar(df, x="count", y="name", orientation="h",
                 color="category", color_discrete_map=COLORS)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='#e2e8f0'), showlegend=False,
                      xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title=""),
                      yaxis=dict(gridcolor='rgba(255,255,255,0)', title=""),
                      margin=dict(t=10,b=10,l=10,r=10), height=300)
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### 🥧 Skill Category Distribution")
    dist = data["skill_dist"]
    labels = list(dist.keys()); vals = list(dist.values())
    colors = [COLORS.get(l,"#64748b") for l in labels]
    fig2 = go.Figure(go.Pie(
        labels=labels, values=vals, hole=0.55,
        marker=dict(colors=colors, line=dict(width=0)),
        textfont=dict(color='#e2e8f0', size=11),
    ))
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=True,
                       legend=dict(font=dict(color='#94a3b8',size=11), bgcolor='rgba(0,0,0,0)'),
                       margin=dict(t=10,b=10,l=10,r=10), height=300)
    st.plotly_chart(fig2, use_container_width=True)

# ── Charts row 2 ──────────────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown("#### 📈 Match Score Distribution")
    md = data["match_dist"]
    fig3 = go.Figure(go.Bar(
        x=list(md.keys()), y=list(md.values()),
        marker=dict(color=["#ef4444","#f97316","#f59e0b","#22c55e"],
                    line=dict(width=0)),
    ))
    fig3.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                       font=dict(color='#e2e8f0'),
                       xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Score Range"),
                       yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title="Count"),
                       margin=dict(t=10,b=30,l=10,r=10), height=260)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("#### 🎓 Education Breakdown")
    ec = data["edu_counts"]
    if ec:
        fig4 = go.Figure(go.Pie(
            labels=list(ec.keys()), values=list(ec.values()), hole=0.45,
            marker=dict(colors=["#6366f1","#22c55e","#f59e0b","#3b82f6","#a855f7"],
                        line=dict(width=0)),
            textfont=dict(color='#e2e8f0', size=11),
        ))
        fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=True,
                           legend=dict(font=dict(color='#94a3b8',size=11), bgcolor='rgba(0,0,0,0)'),
                           margin=dict(t=10,b=10,l=10,r=10), height=260)
        st.plotly_chart(fig4, use_container_width=True)

# ── Leaderboard ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 🏆 Candidate Leaderboard")
lb = data.get("leaderboard", [])
if lb:
    df_lb = pd.DataFrame(lb)[["rank","name","email","employability","ats","tech"]]
    df_lb.columns = ["Rank","Name","Email","Employability (%)","ATS Score (%)","Tech Score (%)"]
    st.dataframe(df_lb, use_container_width=True, hide_index=True)
else:
    st.info("No candidate data yet. Upload resumes to populate the leaderboard.")

# ── Recent uploads ─────────────────────────────────────────────────────────────
recent = data.get("recent", [])
if recent:
    st.markdown("#### 🕐 Recent Uploads")
    df_r = pd.DataFrame(recent)[["id","name","email","ats","employability","created"]]
    df_r.columns = ["Resume ID","Name","Email","ATS Score (%)","Employability (%)","Date"]
    st.dataframe(df_r, use_container_width=True, hide_index=True)
