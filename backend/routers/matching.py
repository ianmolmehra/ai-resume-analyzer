from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models import Resume, Candidate, Skill, CandidateSkill
from models.job_description import JobDescription
from models.match_report import MatchReport
from models.analytics import Analytics
from schemas.match import MatchRequest, MatchResponse
from services.jd_analyzer import analyze_job_description
from services.matching_engine import match_resume_to_jd
from services.resume_parser import extract_text
from services.skill_extractor import extract_skills
from schemas.resume import ParsedResumeData, SkillWithConfidence, EducationItem, ExperienceItem, ProjectItem, CertificationItem
from services.report_generator import generate_match_report_pdf
from utils.file_handler import save_upload_file, validate_file
from loguru import logger
import json

router = APIRouter(prefix="/match", tags=["Matching"])


def db_resume_to_parsed(resume: Resume, db: Session) -> ParsedResumeData:
    candidate = db.query(Candidate).filter(Candidate.id == resume.candidate_id).first()
    skills_raw = db.query(CandidateSkill).filter(CandidateSkill.candidate_id == resume.candidate_id).all()
    skills = []
    for cs in skills_raw:
        sk = db.query(Skill).filter(Skill.id == cs.skill_id).first()
        if sk:
            skills.append(SkillWithConfidence(
                name=sk.name, category=sk.category,
                confidence_score=cs.confidence_score,
                proficiency_level=cs.proficiency_level or "Intermediate",
            ))

    edu = [EducationItem(**e) for e in (resume.education or [])]
    exp = [ExperienceItem(**e) for e in (resume.experience or [])]
    proj = [ProjectItem(**p) for p in (resume.projects or [])]
    certs = [ProjectItem(**c) for c in (resume.certifications or [])]

    return ParsedResumeData(
        full_name=candidate.full_name if candidate else None,
        email=candidate.email if candidate else None,
        phone=candidate.phone if candidate else None,
        linkedin_url=candidate.linkedin_url if candidate else None,
        github_url=candidate.github_url if candidate else None,
        education=edu,
        experience=exp,
        projects=proj,
        skills=skills,
        total_experience_years=resume.total_experience_years or 0.0,
        highest_education=resume.highest_education,
    )


@router.post("/analyze", response_model=dict)
async def analyze_match(
    resume_id: int = Form(...),
    jd_text: Optional[str] = Form(None),
    jd_file: Optional[UploadFile] = File(None),
    job_title: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Get JD text
    if jd_file:
        validate_file(jd_file)
        file_path, _ = await save_upload_file(jd_file, subfolder="jd")
        jd_text = extract_text(file_path)
    
    if not jd_text or len(jd_text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Job description text is required")

    # Analyze JD
    jd_data = analyze_job_description(jd_text, job_title, company)
    jd = JobDescription(**{k: v for k, v in jd_data.items()})
    db.add(jd)
    db.flush()

    # Get parsed resume
    parsed = db_resume_to_parsed(resume, db)
    raw_text = resume.raw_text or ""

    # Run matching
    match_result = match_resume_to_jd(parsed, raw_text, jd_data, resume.id, jd.id)

    scorecard = match_result.pop("scorecard", None)
    skill_details = match_result.pop("skill_details", [])
    skill_gap = match_result.pop("skill_gap_analysis", [])

    # Save match report
    match_report = MatchReport(
        resume_id=resume.id,
        job_description_id=jd.id,
        overall_match_score=match_result["overall_match_score"],
        skill_match_score=match_result["skill_match_score"],
        experience_match_score=match_result["experience_match_score"],
        education_match_score=match_result["education_match_score"],
        project_relevance_score=match_result["project_relevance_score"],
        keyword_match_score=match_result["keyword_match_score"],
        matched_skills=match_result["matched_skills"],
        missing_skills=match_result["missing_skills"],
        skill_gap_analysis=[g.dict() for g in skill_gap],
        recommendations=match_result["recommendations"],
        improvement_suggestions=match_result["improvement_suggestions"],
        ats_compatibility=match_result["ats_compatibility"],
        keyword_optimization=match_result["keyword_optimization"],
    )
    db.add(match_report)
    db.flush()

    # Update resume scores from scorecard
    if scorecard:
        resume.ats_score = scorecard.ats_score
        resume.resume_quality_score = scorecard.resume_quality_score
        resume.technical_skill_score = scorecard.technical_skill_score
        resume.employability_score = scorecard.employability_score

    db.add(Analytics(event_type="match_generated", metadata={
        "resume_id": resume.id, "jd_id": jd.id,
        "overall_score": match_result["overall_match_score"]
    }))
    db.commit()
    db.refresh(match_report)

    candidate = db.query(Candidate).filter(Candidate.id == resume.candidate_id).first()

    return {
        "match_report_id": match_report.id,
        "resume_id": resume.id,
        "job_description_id": jd.id,
        "candidate": {
            "full_name": candidate.full_name if candidate else None,
            "email": candidate.email if candidate else None,
            "phone": candidate.phone if candidate else None,
            "linkedin_url": candidate.linkedin_url if candidate else None,
            "github_url": candidate.github_url if candidate else None,
            "total_experience_years": resume.total_experience_years,
        },
        "job": {"title": jd.title, "company": jd.company},
        "scores": {
            "overall_match_score": match_result["overall_match_score"],
            "skill_match_score": match_result["skill_match_score"],
            "experience_match_score": match_result["experience_match_score"],
            "education_match_score": match_result["education_match_score"],
            "project_relevance_score": match_result["project_relevance_score"],
            "keyword_match_score": match_result["keyword_match_score"],
            "ats_compatibility": match_result["ats_compatibility"],
        },
        "scorecard": scorecard.dict() if scorecard else {},
        "matched_skills": match_result["matched_skills"],
        "missing_skills": match_result["missing_skills"],
        "skill_details": [s.dict() for s in skill_details],
        "skill_gap_analysis": [g.dict() for g in skill_gap],
        "recommendations": match_result["recommendations"],
        "improvement_suggestions": match_result["improvement_suggestions"],
        "keyword_optimization": match_result["keyword_optimization"],
    }


@router.get("/{match_report_id}/report/pdf")
def download_pdf_report(match_report_id: int, db: Session = Depends(get_db)):
    report = db.query(MatchReport).filter(MatchReport.id == match_report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Match report not found")

    resume = db.query(Resume).filter(Resume.id == report.resume_id).first()
    candidate = db.query(Candidate).filter(Candidate.id == resume.candidate_id).first() if resume else None
    jd = db.query(JobDescription).filter(JobDescription.id == report.job_description_id).first()

    report_data = {
        "resume_id": report.resume_id,
        "candidate": {
            "full_name": candidate.full_name if candidate else "N/A",
            "email": candidate.email if candidate else "N/A",
            "phone": candidate.phone if candidate else "N/A",
            "linkedin_url": candidate.linkedin_url if candidate else "N/A",
            "github_url": candidate.github_url if candidate else "N/A",
            "total_experience_years": resume.total_experience_years if resume else 0,
        },
        "overall_match_score": report.overall_match_score,
        "skill_match_score": report.skill_match_score,
        "experience_match_score": report.experience_match_score,
        "education_match_score": report.education_match_score,
        "project_relevance_score": report.project_relevance_score,
        "keyword_match_score": report.keyword_match_score,
        "matched_skills": report.matched_skills or [],
        "missing_skills": report.missing_skills or [],
        "skill_gap_analysis": report.skill_gap_analysis or [],
        "recommendations": report.recommendations or [],
        "improvement_suggestions": report.improvement_suggestions or [],
        "scorecard": {
            "ats_score": resume.ats_score if resume else 0,
            "resume_quality_score": resume.resume_quality_score if resume else 0,
            "technical_skill_score": resume.technical_skill_score if resume else 0,
            "employability_score": resume.employability_score if resume else 0,
        },
    }

    try:
        pdf_path = generate_match_report_pdf(report_data)
        report.report_path = pdf_path
        db.commit()
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"match_report_{match_report_id}.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.get("/history/{resume_id}", response_model=list)
def get_match_history(resume_id: int, db: Session = Depends(get_db)):
    reports = db.query(MatchReport).filter(MatchReport.resume_id == resume_id).all()
    result = []
    for r in reports:
        jd = db.query(JobDescription).filter(JobDescription.id == r.job_description_id).first()
        result.append({
            "id": r.id,
            "job_title": jd.title if jd else None,
            "company": jd.company if jd else None,
            "overall_match_score": r.overall_match_score,
            "skill_match_score": r.skill_match_score,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return result
