# 🧠 AI Resume Analyzer & Job Matching Platform

A production-quality, fully Python-based AI platform for resume analysis, skill extraction, and intelligent job description matching — built with **Streamlit**, **FastAPI-style services**, **MySQL**, and **Plotly**.

---

## 🚀 Features

| Module | Description |
|--------|-------------|
| 📤 **Resume Upload** | Drag & drop PDF/DOCX, validated, parsed instantly |
| 🧠 **Resume Parsing** | Extracts name, contact, education, experience, projects, certifications |
| ⚙️ **Skill Extraction** | 100+ skills across 8 categories with confidence scores |
| 🎯 **Job Matching** | Overall match %, skill/experience/education/ATS scores |
| 🔍 **Skill Gap Analysis** | Missing skills with step-by-step learning paths |
| 📊 **Analytics Dashboard** | Charts: top skills, category distribution, match trends, leaderboard |
| 🏆 **Candidate Scorecard** | ATS Score, Resume Quality, Technical Skills, Employability (0–100) |
| 📑 **PDF Report** | Downloadable match report with full analysis |
| 🛡️ **Admin Panel** | Manage resumes, match reports, and skill data |

---

## 🏗️ Tech Stack

- **UI**: Streamlit 1.35 + Plotly
- **Parsing**: pdfplumber, PyPDF2, python-docx
- **ML/NLP**: scikit-learn, NLTK, regex pattern matching
- **Database**: SQLite (built-in, zero setup) + SQLAlchemy ORM
- **Reports**: ReportLab (PDF generation)
- **Deployment**: Docker + Docker Compose

---

## 📁 Folder Structure

```
resume-analyzer/
├── streamlit_app.py          # Home page (upload)
├── pages/
│   ├── 1_Analysis.py         # Resume analysis & skills
│   ├── 2_Matching.py         # Job description matching
│   ├── 3_Dashboard.py        # Analytics dashboard
│   └── 4_Admin.py            # Admin panel
├── backend/
│   ├── config.py             # App configuration
│   ├── database.py           # SQLAlchemy engine & session
│   ├── models/               # ORM models
│   │   ├── candidate.py
│   │   ├── resume.py
│   │   ├── skill.py
│   │   ├── job_description.py
│   │   ├── match_report.py
│   │   └── analytics.py
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Core business logic
│   │   ├── resume_parser.py  # PDF/DOCX text extraction
│   │   ├── skill_extractor.py# Pattern-based skill detection
│   │   ├── jd_analyzer.py    # Job description analysis
│   │   ├── matching_engine.py# Scoring algorithms
│   │   └── report_generator.py # PDF report (ReportLab)
│   ├── utils/
│   │   ├── file_handler.py
│   │   └── text_processor.py
│   └── requirements.txt
├── utils/
│   └── styles.py             # Shared Streamlit CSS theme
├── database/
│   ├── schema.sql            # MySQL DDL
│   └── sample_data.sql       # Seed data (5 candidates)
├── uploads/                  # Uploaded files (auto-created)
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## ⚡ Quick Start (2 commands — no database setup needed)

```bash
pip install -r backend/requirements.txt
streamlit run streamlit_app.py
```
Visit **http://localhost:8501** — the SQLite database is created automatically on first run.

---

## ☁️ Deploy to Streamlit Cloud (free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Select your repo, set **Main file** to `streamlit_app.py`
4. Click Deploy — done ✅

No environment variables or database setup required.

---

## 🐳 Docker Quickstart

```bash
docker-compose up --build
```
Visit **http://localhost:8501** — the app and SQLite DB start automatically.

---

## 🗃️ Database Schema (ER Summary)

```
candidates ──< resumes ──< match_reports >── job_descriptions
     │
     └──< candidate_skills >── skills

analytics   (event log)
```

**Tables:** `candidates`, `resumes`, `skills`, `candidate_skills`, `job_descriptions`, `match_reports`, `analytics`

---

## 📊 Scoring Algorithm

| Score | Weight | Description |
|-------|--------|-------------|
| Skill Match | 40% | Required + preferred skills overlap |
| Experience Match | 25% | Years of experience vs requirement |
| Education Match | 15% | Degree level comparison |
| Project Relevance | 10% | Tech stack overlap with JD skills |
| Keyword Match | 10% | ATS keyword density |

**Candidate Scorecard** (independent of JD):
- **ATS Score** — keyword density + completeness
- **Resume Quality** — sections, contact info, length
- **Technical Skills** — skill count + high-value categories
- **Employability** — weighted composite

---

## 🧠 Skill Categories Detected

| Category | Examples |
|----------|----------|
| Programming | Python, Java, C++, JavaScript, Go, R |
| Database | SQL, MySQL, PostgreSQL, MongoDB, Redis |
| Data Analytics | Excel, Power BI, Tableau, Pandas, NumPy |
| AI/ML | Machine Learning, TensorFlow, PyTorch, NLP, LangChain |
| Cloud | AWS, Azure, GCP |
| DevOps | Docker, Kubernetes, Git, CI/CD, Terraform |
| Framework | React, Django, Flask, FastAPI, Spring, Node.js |

---

## 🔧 Configuration

No configuration needed — SQLite is auto-created as `resume_analyzer.db` in the project root on first run.

Optional: set `DEBUG=true` in `backend/.env` to enable SQLAlchemy query logging.

---

## 🏆 Portfolio Use

This project demonstrates:
- End-to-end Python ML application development
- NLP-based information extraction (resume parsing)
- Custom scoring algorithms (weighted matching)
- Streamlit multipage app architecture
- SQLAlchemy ORM with SQLite (zero-setup, file-based)
- PDF generation with ReportLab
- Plotly interactive data visualizations
- Docker containerization

Suitable for **Data Analyst**, **AI/ML Engineer**, or **Software Developer** portfolios.
