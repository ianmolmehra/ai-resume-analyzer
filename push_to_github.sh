#!/bin/bash
# ─────────────────────────────────────────────────────────────
# push_to_github.sh — One-shot GitHub push for AI Resume Analyzer
# Run from the project folder:  bash push_to_github.sh
# ─────────────────────────────────────────────────────────────

set -e
cd "$(dirname "$0")"

REPO_NAME="ai-resume-analyzer"
GITHUB_USER=""   # ← optional: set your GitHub username to skip the prompt

# ── 1. Clean up any stale git state ──────────────────────────
echo "🔧 Cleaning up git state..."
rm -f .git/index.lock 2>/dev/null || true

# If .git already exists from a previous attempt, reset it cleanly
if [ -d .git ]; then
  echo "  Found existing .git — resetting to a clean state"
  rm -rf .git
fi

# ── 2. Initialize repo ───────────────────────────────────────
echo "📁 Initializing git repository..."
git init
git branch -m main
git config user.email "anmol2005mehra@gmail.com"
git config user.name "Anmol Mehra"

# ── 3. Stage and commit ──────────────────────────────────────
echo "📦 Staging files..."
git add .
echo "💾 Creating initial commit..."
git commit -m "Initial commit: AI Resume Analyzer & Job Matching Platform

- Streamlit multipage app (Upload, Analysis, Matching, Dashboard, Admin)
- PDF/DOCX resume parsing with pdfplumber + python-docx
- Pattern-based skill extraction (100+ skills, 8 categories)
- Weighted job matching engine (skill/experience/education/ATS)
- Skill gap analysis with learning paths
- Analytics dashboard with Plotly charts
- Candidate scorecard (ATS, Quality, Technical, Employability)
- PDF report generation with ReportLab
- SQLite database via SQLAlchemy (zero setup, file-based)
- Docker single-container deployment
- Streamlit Cloud ready (packages.txt, config.toml)"

# ── 4. Create GitHub repo ────────────────────────────────────
echo ""
echo "🌐 Creating GitHub repository..."

# Try GitHub CLI (gh) first — most reliable
if command -v gh &>/dev/null; then
  gh repo create "$REPO_NAME" \
    --public \
    --description "AI-powered resume analyzer and job matching platform built with Streamlit + SQLite" \
    --source=. \
    --remote=origin \
    --push
  echo ""
  echo "✅ Done! Repository pushed to GitHub."
  echo "   View it at: https://github.com/$(gh api user --jq .login)/$REPO_NAME"
  echo ""
  echo "🚀 Deploy to Streamlit Cloud (free):"
  echo "   1. Go to https://share.streamlit.io → New app"
  echo "   2. Select this repo, set Main file: streamlit_app.py"
  echo "   3. Click Deploy"
else
  # No gh CLI — ask user to create repo manually
  echo ""
  echo "──────────────────────────────────────────────────────"
  echo "  GitHub CLI (gh) not found. Do this in 30 seconds:"
  echo ""
  echo "  1. Open: https://github.com/new"
  echo "  2. Repository name: $REPO_NAME"
  echo "  3. Set to Public, do NOT check any init options"
  echo "  4. Click 'Create repository'"
  echo "  5. Copy the HTTPS URL (looks like https://github.com/YOU/$REPO_NAME.git)"
  echo "──────────────────────────────────────────────────────"
  echo ""
  read -p "Paste your GitHub repo URL here: " REMOTE_URL

  if [ -z "$REMOTE_URL" ]; then
    echo "❌ No URL provided. Run this command manually after creating the repo:"
    echo "   git remote add origin <your-url> && git push -u origin main"
    exit 1
  fi

  git remote add origin "$REMOTE_URL"
  echo "📤 Pushing to GitHub..."
  git push -u origin main

  echo ""
  echo "✅ Done! Repository pushed to GitHub."
  echo ""
  echo "🚀 Deploy to Streamlit Cloud (free):"
  echo "   1. Go to https://share.streamlit.io → New app"
  echo "   2. Select this repo, set Main file: streamlit_app.py"
  echo "   3. Click Deploy"
fi
