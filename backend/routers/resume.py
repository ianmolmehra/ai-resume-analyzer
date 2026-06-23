import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Candidate, Resume, Skill, CandidateSkill
from schemas.resume import ResumeResponse, ResumeDetail, ParsedResumeData
from schemas.candidate import CandidateResponse
from services.resume_parser import parse_resume, extract_text
from services.skill_extractor import extract_skills
from utils.file_handler import save_upload_file, validate_file
from loguru import logger

router = APIRouter(prefix="/resumes", tags=["Resume"])


@router.post("/upload", response_model=dict)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    validate_file(file)
    file_path, size_kb = await save_upload_file(file, subfolder="resumes")
    ext = os.path.splitext(file.filename)[1].lower()

    try:
        parsed: ParsedResumeData = parse_resume(file_path)
        raw_text = extract_text(file_path)
        skills = extract_skills(raw_text)
        parsed.skills = skills
    except Exception as e:
        logger.error(f"Parsing failed: {e}")
        raise HTTPException(status_code=422, detail=f"Resume parsing failed: {str(e)}")

    # Upsert candidate
    candidate = None
    if parsed.email:
        candidate = db.query(Candidate).filter(Candidate.email == parsed.email).first()

    if not candidate:
        candidate = Candidate(
            full_name=parsed.full_name or "Unknown",
            email=parsed.email,
            phone=parsed.phone,
            linkedin_url=parsed.linkedin_url,
            github_url=parsed.github_url,
            summary=parsed.summary,
        )
        db.add(candidate)
        db.flush()
    else:
        if parsed.phone: candidate.phone = parsed.phone
        if parsed.linkedin_url: candidate.linkedin_url = parsed.linkedin_url
        if parsed.github_url: candidate.github_url = parsed.github_url

    from services.matching_engine import compute_resume_quality, compute_technical_score
    quality = compute_resume_quality(parsed, raw_text)
    tech = compute_technical_score(skills, raw_text)
    ats = min(100.0, quality * 0.8 + tech * 0.2)
    employability = min(100.0, (quality + tech) / 2)

    resume = Resume(
        candidate_id=candidate.id,
        filename=file.filename,
        file_path=file_path,
        file_type=ext,
        file_size_kb=size_kb,
        raw_text=raw_text[:50000],
        education=[e.dict() for e in parsed.education],
        experience=[e.dict() for e in parsed.experience],
        projects=[p.dict() for p in parsed.projects],
        certifications=[c.dict() for c in parsed.certifications],
        ats_score=ats,
        resume_quality_score=quality,
        technical_skill_score=tech,
        employability_score=employability,
        total_experience_years=parsed.total_experience_years,
        highest_education=parsed.highest_education,
        status="parsed",
    )
    db.add(resume)
    db.flush()

    # Save skills
    for skill_data in skills:
        skill = db.query(Skill).filter(Skill.name == skill_data.name).first()
        if not skill:
            skill = Skill(name=skill_data.name, category=skill_data.category)
            db.add(skill)
            db.flush()

        existing = db.query(CandidateSkill).filter(
            CandidateSkill.candidate_id == candidate.id,
            CandidateSkill.skill_id == skill.id,
        ).first()
        if not existing:
            cs = CandidateSkill(
                candidate_id=candidate.id,
                skill_id=skill.id,
                confidence_score=skill_data.confidence_score,
                proficiency_level=skill_data.proficiency_level,
            )
            db.add(cs)

    db.commit()
    db.refresh(resume)

    # Log analytics
    from models.analytics import Analytics
    db.add(Analytics(event_type="resume_upload", metadata={"resume_id": resume.id, "candidate_id": candidate.id}))
    db.commit()

    return {
        "resume_id": resume.id,
        "candidate_id": candidate.id,
        "parsed_data": parsed.dict(),
        "ats_score": ats,
        "resume_quality_score": quality,
        "technical_skill_score": tech,
        "employability_score": employability,
        "message": "Resume uploaded and parsed successfully",
    }


@router.get("/", response_model=List[dict])
def list_resumes(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    resumes = db.query(Resume).offset(skip).limit(limit).all()
    result = []
    for r in resumes:
        candidate = db.query(Candidate).filter(Candidate.id == r.candidate_id).first()
        result.append({
            "id": r.id,
            "candidate_id": r.candidate_id,
            "candidate_name": candidate.full_name if candidate else "Unknown",
            "candidate_email": candidate.email if candidate else None,
            "filename": r.filename,
            "file_type": r.file_type,
            "ats_score": r.ats_score,
            "resume_quality_score": r.resume_quality_score,
            "technical_skill_score": r.technical_skill_score,
            "employability_score": r.employability_score,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return result


@router.get("/{resume_id}", response_model=dict)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    candidate = db.query(Candidate).filter(Candidate.id == resume.candidate_id).first()
    skills = db.query(CandidateSkill).filter(CandidateSkill.candidate_id == resume.candidate_id).all()
    skill_list = []
    for cs in skills:
        sk = db.query(Skill).filter(Skill.id == cs.skill_id).first()
        if sk:
            skill_list.append({"name": sk.name, "category": sk.category, "confidence_score": cs.confidence_score, "proficiency_level": cs.proficiency_level})
    return {
        "id": resume.id,
        "candidate": {
            "id": candidate.id if candidate else None,
            "full_name": candidate.full_name if candidate else None,
            "email": candidate.email if candidate else None,
            "phone": candidate.phone if candidate else None,
            "linkedin_url": candidate.linkedin_url if candidate else None,
            "github_url": candidate.github_url if candidate else None,
        } if candidate else {},
        "filename": resume.filename,
        "file_type": resume.file_type,
        "file_size_kb": resume.file_size_kb,
        "education": resume.education or [],
        "experience": resume.experience or [],
        "projects": resume.projects or [],
        "certifications": resume.certifications or [],
        "skills": skill_list,
        "ats_score": resume.ats_score,
        "resume_quality_score": resume.resume_quality_score,
        "technical_skill_score": resume.technical_skill_score,
        "employability_score": resume.employability_score,
        "total_experience_years": resume.total_experience_years,
        "highest_education": resume.highest_education,
        "status": resume.status,
        "created_at": resume.created_at.isoformat() if resume.created_at else None,
    }


@router.delete("/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    from utils.file_handler import delete_file
    delete_file(resume.file_path)
    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted"}
