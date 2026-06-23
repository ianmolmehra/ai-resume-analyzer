from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    company = Column(String(255))
    raw_text = Column(Text, nullable=False)

    required_skills = Column(JSON)    # [skill_name]
    preferred_skills = Column(JSON)   # [skill_name]
    experience_required = Column(Float, default=0.0)
    education_required = Column(String(255))
    keywords = Column(JSON)           # extracted keywords

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    match_reports = relationship("MatchReport", back_populates="job_description")
