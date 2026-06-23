from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class MatchReport(Base):
    __tablename__ = "match_reports"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_description_id = Column(Integer, ForeignKey("job_descriptions.id"), nullable=False)

    overall_match_score = Column(Float, default=0.0)
    skill_match_score = Column(Float, default=0.0)
    experience_match_score = Column(Float, default=0.0)
    education_match_score = Column(Float, default=0.0)
    project_relevance_score = Column(Float, default=0.0)
    keyword_match_score = Column(Float, default=0.0)

    matched_skills = Column(JSON)     # [skill_name]
    missing_skills = Column(JSON)     # [skill_name]
    skill_gap_analysis = Column(JSON) # [{skill, learning_path: []}]
    recommendations = Column(JSON)    # [recommendation_text]
    improvement_suggestions = Column(JSON)

    ats_compatibility = Column(Float, default=0.0)
    keyword_optimization = Column(JSON)

    report_path = Column(String(1000))  # path to generated PDF
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="match_reports")
    job_description = relationship("JobDescription", back_populates="match_reports")
