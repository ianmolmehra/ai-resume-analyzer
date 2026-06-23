from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database import get_db
from models import Resume, Candidate, Skill, CandidateSkill
from models.match_report import MatchReport
from models.analytics import Analytics

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_resumes = db.query(Resume).count()
    total_candidates = db.query(Candidate).count()
    total_matches = db.query(MatchReport).count()

    avg_match = db.query(func.avg(MatchReport.overall_match_score)).scalar() or 0
    avg_ats = db.query(func.avg(Resume.ats_score)).scalar() or 0
    avg_quality = db.query(func.avg(Resume.resume_quality_score)).scalar() or 0

    # Top skills
    top_skills_query = (
        db.query(Skill.name, Skill.category, func.count(CandidateSkill.id).label("count"))
        .join(CandidateSkill, Skill.id == CandidateSkill.skill_id)
        .group_by(Skill.id, Skill.name, Skill.category)
        .order_by(desc("count"))
        .limit(15)
        .all()
    )
    top_skills = [{"name": s.name, "category": s.category, "count": s.count} for s in top_skills_query]

    # Skill category distribution
    category_dist_query = (
        db.query(Skill.category, func.count(CandidateSkill.id).label("count"))
        .join(CandidateSkill, Skill.id == CandidateSkill.skill_id)
        .group_by(Skill.category)
        .all()
    )
    skill_distribution = {c.category: c.count for c in category_dist_query}

    # Education breakdown
    education_counts = {}
    resumes = db.query(Resume.highest_education).all()
    for r in resumes:
        edu = r.highest_education or "Unknown"
        education_counts[edu] = education_counts.get(edu, 0) + 1

    # Match score distribution
    match_ranges = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
    all_matches = db.query(MatchReport.overall_match_score).all()
    for m in all_matches:
        score = m.overall_match_score or 0
        if score <= 25: match_ranges["0-25"] += 1
        elif score <= 50: match_ranges["26-50"] += 1
        elif score <= 75: match_ranges["51-75"] += 1
        else: match_ranges["76-100"] += 1

    # Recent uploads
    recent_resumes = (
        db.query(Resume, Candidate)
        .join(Candidate, Resume.candidate_id == Candidate.id)
        .order_by(desc(Resume.created_at))
        .limit(5)
        .all()
    )
    recent = [{
        "id": r.Resume.id,
        "name": r.Candidate.full_name,
        "email": r.Candidate.email,
        "ats_score": r.Resume.ats_score,
        "created_at": r.Resume.created_at.isoformat() if r.Resume.created_at else None,
    } for r in recent_resumes]

    # Top candidates by employability
    top_candidates = (
        db.query(Resume, Candidate)
        .join(Candidate, Resume.candidate_id == Candidate.id)
        .order_by(desc(Resume.employability_score))
        .limit(10)
        .all()
    )
    leaderboard = [{
        "rank": i+1,
        "id": r.Resume.id,
        "candidate_id": r.Candidate.id,
        "name": r.Candidate.full_name,
        "email": r.Candidate.email,
        "employability_score": r.Resume.employability_score,
        "technical_skill_score": r.Resume.technical_skill_score,
        "ats_score": r.Resume.ats_score,
    } for i, r in enumerate(top_candidates)]

    return {
        "summary": {
            "total_resumes": total_resumes,
            "total_candidates": total_candidates,
            "total_matches": total_matches,
            "avg_match_score": round(avg_match, 1),
            "avg_ats_score": round(avg_ats, 1),
            "avg_quality_score": round(avg_quality, 1),
        },
        "top_skills": top_skills,
        "skill_distribution": skill_distribution,
        "education_breakdown": education_counts,
        "match_score_distribution": match_ranges,
        "recent_uploads": recent,
        "leaderboard": leaderboard,
    }


@router.get("/skills/top")
def get_top_skills(limit: int = 20, db: Session = Depends(get_db)):
    query = (
        db.query(Skill.name, Skill.category, func.count(CandidateSkill.id).label("count"))
        .join(CandidateSkill, Skill.id == CandidateSkill.skill_id)
        .group_by(Skill.id, Skill.name, Skill.category)
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )
    return [{"name": s.name, "category": s.category, "count": s.count} for s in query]


@router.get("/candidates/ranking")
def get_candidate_ranking(db: Session = Depends(get_db)):
    results = (
        db.query(Resume, Candidate)
        .join(Candidate, Resume.candidate_id == Candidate.id)
        .order_by(desc(Resume.employability_score))
        .all()
    )
    return [{
        "rank": i+1,
        "candidate_id": r.Candidate.id,
        "resume_id": r.Resume.id,
        "name": r.Candidate.full_name,
        "email": r.Candidate.email,
        "employability_score": r.Resume.employability_score,
        "technical_skill_score": r.Resume.technical_skill_score,
        "ats_score": r.Resume.ats_score,
        "resume_quality_score": r.Resume.resume_quality_score,
        "total_experience_years": r.Resume.total_experience_years,
    } for i, r in enumerate(results)]
