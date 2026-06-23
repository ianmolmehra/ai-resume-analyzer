"""Shared Streamlit CSS — dark glassmorphism theme."""

GLOBAL_CSS = """
<style>
html, body, [data-testid="stAppViewContainer"] {
    background: #0a0f1e !important;
    color: #e2e8f0;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1629 0%, #0a0f1e 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.07);
}
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none; }

.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.glass-card-sm {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.75rem;
}
.metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    text-align: center;
}
.metric-value { font-size: 2rem; font-weight: 700; line-height: 1; }
.metric-label { font-size: 0.8rem; color: #94a3b8; margin-top: 0.25rem; }
.metric-sub   { font-size: 0.72rem; color: #64748b; margin-top: 0.15rem; }
.score-high { color: #22c55e; }
.score-mid  { color: #f59e0b; }
.score-low  { color: #ef4444; }
.skill-tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 3px;
    border: 1px solid;
}
.tag-programming { background: rgba(99,102,241,0.15); color: #a5b4fc; border-color: rgba(99,102,241,0.3); }
.tag-database    { background: rgba(59,130,246,0.15); color: #93c5fd; border-color: rgba(59,130,246,0.3); }
.tag-analytics   { background: rgba(245,158,11,0.15); color: #fcd34d; border-color: rgba(245,158,11,0.3); }
.tag-aiml        { background: rgba(34,197,94,0.15);  color: #86efac; border-color: rgba(34,197,94,0.3); }
.tag-cloud       { background: rgba(6,182,212,0.15);  color: #67e8f9; border-color: rgba(6,182,212,0.3); }
.tag-devops      { background: rgba(249,115,22,0.15); color: #fdba74; border-color: rgba(249,115,22,0.3); }
.tag-framework   { background: rgba(168,85,247,0.15); color: #d8b4fe; border-color: rgba(168,85,247,0.3); }
.tag-other       { background: rgba(100,116,139,0.15);color: #cbd5e1; border-color: rgba(100,116,139,0.3); }
.progress-wrap { background: rgba(255,255,255,0.07); border-radius: 999px; height: 8px; margin: 4px 0 10px; overflow: hidden; }
.progress-fill { height: 8px; border-radius: 999px; }
.pill-match   { background: rgba(34,197,94,0.12);  color: #86efac; border: 1px solid rgba(34,197,94,0.25);  padding: 3px 10px; border-radius: 999px; font-size: 0.78rem; display: inline-block; margin: 3px; }
.pill-missing { background: rgba(239,68,68,0.12);  color: #fca5a5; border: 1px solid rgba(239,68,68,0.25);  padding: 3px 10px; border-radius: 999px; font-size: 0.78rem; display: inline-block; margin: 3px; }
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; font-weight: 600 !important;
    padding: 0.6rem 1.4rem !important;
}
.stButton > button:hover { box-shadow: 0 0 20px rgba(99,102,241,0.4) !important; }
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 2px dashed rgba(99,102,241,0.4) !important;
    border-radius: 16px !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] { background: transparent !important; border-radius: 8px !important; color: #94a3b8 !important; font-weight: 500 !important; }
.stTabs [aria-selected="true"] { background: #6366f1 !important; color: white !important; }
.section-header {
    font-size: 1rem; font-weight: 700; color: #e2e8f0;
    margin-bottom: 1rem; padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.leaderboard-row {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.65rem 0.75rem; border-radius: 10px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 0.5rem;
}
.rank-badge { width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.75rem; font-weight:700; flex-shrink:0; }
.rank-1 { background: rgba(245,158,11,0.25); color: #fcd34d; }
.rank-2 { background: rgba(148,163,184,0.2);  color: #cbd5e1; }
.rank-3 { background: rgba(249,115,22,0.2);   color: #fdba74; }
.rank-n { background: rgba(99,102,241,0.15);  color: #a5b4fc; }
.info-box { background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.2); border-radius: 12px; padding: 0.9rem 1.1rem; color: #c7d2fe; font-size: 0.88rem; margin-bottom: 1rem; }
.warn-box { background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.25); border-radius: 12px; padding: 0.9rem 1.1rem; color: #fcd34d; font-size: 0.88rem; margin-bottom: 1rem; }
</style>
"""

CATEGORY_CSS_MAP = {
    "Programming":    "tag-programming",
    "Database":       "tag-database",
    "Data Analytics": "tag-analytics",
    "AI/ML":          "tag-aiml",
    "Cloud":          "tag-cloud",
    "DevOps":         "tag-devops",
    "Framework":      "tag-framework",
    "Other":          "tag-other",
}

def score_color(score: float) -> str:
    if score >= 75: return "#22c55e"
    if score >= 50: return "#f59e0b"
    return "#ef4444"

def score_color_class(score: float) -> str:
    if score >= 75: return "score-high"
    if score >= 50: return "score-mid"
    return "score-low"

def score_label(score: float) -> str:
    if score >= 85: return "Excellent"
    if score >= 70: return "Good"
    if score >= 50: return "Moderate"
    return "Needs Work"

def progress_bar_html(score: float, color: str = None) -> str:
    c = color or score_color(score)
    return f'<div class="progress-wrap"><div class="progress-fill" style="width:{score:.1f}%;background:{c};"></div></div>'

def metric_card_html(value, label, sub="", color_class="score-high") -> str:
    sub_html = f"<div class='metric-sub'>{sub}</div>" if sub else ""
    return f'<div class="metric-card"><div class="metric-value {color_class}">{value}</div><div class="metric-label">{label}</div>{sub_html}</div>'

def skill_tags_html(skills: list) -> str:
    html = ""
    for s in skills:
        css = CATEGORY_CSS_MAP.get(s.get("category", "Other"), "tag-other")
        conf = int(s.get("confidence_score", 0.7) * 100)
        html += f'<span class="skill-tag {css}">{s["name"]} <span style="opacity:0.6;font-size:0.7rem">{conf}%</span></span>'
    return html
