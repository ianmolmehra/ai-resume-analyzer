from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from database import get_db
from models import Resume, Candidate, Skill, CandidateSkill
from models.match_report import MatchReport
from models.job_description import JobDescription

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
def admin_stats(db: Session = Depends(get_db)):
    return {
        "total_resumes": db.query(Resume).count(),
        "total_candidates": db.query(Candidate).count(),
        "total_skills": db.query(Skill).count(),
        "total_matches": db.query(MatchReport).count(),
        "total_jds": db.query(JobDescription).count(),
        "avg_ats": round(db.query(func.avg(Resume.ats_score)).scalar() or 0, 1),
        "avg_match": round(db.query(func.avg(MatchReport.overall_match_score)).scalar() or 0, 1),
    }


@router.get("/resumes")
def list_all_resumes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    results = (
        db.query(Resume, Candidate)
        .join(Candidate, Resume.candidate_id == Candidate.id)
        .order_by(desc(Resume.created_at))
        .offset(skip).limit(limit).all()
    )
    return [{
        "resume_id": r.Resume.id,
        "candidate_name": r.Candidate.full_name,
        "email": r.Candidate.email,
        "filename": r.Resume.filename,
        "ats_score": r.Resume.ats_score,
        "employability_score": r.Resume.employability_score,
        "status": r.Resume.status,
        "created_at": r.Resume.created_at.isoformat() if r.Resume.created_at else None,
    } for r in results]


@router.get("/match-reports")
def list_match_reports(db: Session = Depends(get_db)):
    reports = db.query(MatchReport).order_by(desc(MatchReport.created_at)).limit(50).all()
    result = []
    for r in reports:
        resume = db.query(Resume).filter(Resume.id == r.resume_id).first()
        candidate = db.query(Candidate).filter(Candidate.id == resume.candidate_id).first() if resume else None
        jd = db.query(JobDescription).filter(JobDescription.id == r.job_description_id).first()
        result.append({
            "id": r.id,
            "candidate_name": candidate.full_name if candidate else "N/A",
            "job_title": jd.title if jd else "N/A",
            "company": jd.company if jd else "N/A",
            "overall_score": r.overall_match_score,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return result


@router.delete("/resumes/{resume_id}")
def admin_delete_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted"}
