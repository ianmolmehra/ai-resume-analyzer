from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(10))
    file_size_kb = Column(Float)
    raw_text = Column(Text)

    # Education
    education = Column(JSON)        # [{degree, university, year, gpa}]
    # Experience
    experience = Column(JSON)       # [{company, role, duration, description}]
    # Projects
    projects = Column(JSON)         # [{name, description, tech_stack}]
    # Certifications
    certifications = Column(JSON)   # [{name, issuer, year}]

    # Scores
    ats_score = Column(Float, default=0.0)
    resume_quality_score = Column(Float, default=0.0)
    technical_skill_score = Column(Float, default=0.0)
    employability_score = Column(Float, default=0.0)

    total_experience_years = Column(Float, default=0.0)
    highest_education = Column(String(255))

    status = Column(String(50), default="parsed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    candidate = relationship("Candidate", back_populates="resumes")
    match_reports = relationship("MatchReport", back_populates="resume", cascade="all, delete-orphan")
