from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class SkillCategory(str, enum.Enum):
    PROGRAMMING = "Programming"
    DATABASE = "Database"
    DATA_ANALYTICS = "Data Analytics"
    AI_ML = "AI/ML"
    CLOUD = "Cloud"
    DEVOPS = "DevOps"
    FRAMEWORK = "Framework"
    SOFT_SKILL = "Soft Skill"
    OTHER = "Other"


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), default="Other")
    aliases = Column(String(500))  # comma-separated aliases
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    candidate_skills = relationship("CandidateSkill", back_populates="skill")


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    confidence_score = Column(Float, default=0.0)
    years_of_experience = Column(Float, default=0.0)
    proficiency_level = Column(String(50), default="Beginner")  # Beginner/Intermediate/Advanced/Expert
    source = Column(String(100))  # extracted_from: skills_section, experience, projects
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    candidate = relationship("Candidate", back_populates="skills")
    skill = relationship("Skill", back_populates="candidate_skills")
