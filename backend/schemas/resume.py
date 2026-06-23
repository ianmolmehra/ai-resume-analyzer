from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class EducationItem(BaseModel):
    degree: Optional[str] = None
    university: Optional[str] = None
    graduation_year: Optional[str] = None
    gpa: Optional[str] = None
    field: Optional[str] = None


class ExperienceItem(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = []


class ProjectItem(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = []
    url: Optional[str] = None


class CertificationItem(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    year: Optional[str] = None
    url: Optional[str] = None


class SkillWithConfidence(BaseModel):
    name: str
    category: str
    confidence_score: float
    proficiency_level: str


class ParsedResumeData(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    education: List[EducationItem] = []
    experience: List[ExperienceItem] = []
    projects: List[ProjectItem] = []
    certifications: List[CertificationItem] = []
    skills: List[SkillWithConfidence] = []
    total_experience_years: float = 0.0
    highest_education: Optional[str] = None


class ResumeResponse(BaseModel):
    id: int
    candidate_id: Optional[int]
    filename: str
    file_type: str
    file_size_kb: Optional[float]
    ats_score: float
    resume_quality_score: float
    technical_skill_score: float
    employability_score: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeDetail(ResumeResponse):
    education: Optional[List[Dict]] = []
    experience: Optional[List[Dict]] = []
    projects: Optional[List[Dict]] = []
    certifications: Optional[List[Dict]] = []
    total_experience_years: Optional[float] = 0.0
    highest_education: Optional[str] = None
