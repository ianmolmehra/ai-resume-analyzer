from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class MatchRequest(BaseModel):
    resume_id: int
    job_description_id: Optional[int] = None
    job_description_text: Optional[str] = None
    job_title: Optional[str] = None
    company: Optional[str] = None


class LearningResource(BaseModel):
    title: str
    level: str
    platform: Optional[str] = None
    url: Optional[str] = None


class SkillGapItem(BaseModel):
    skill: str
    category: str
    priority: str  # High/Medium/Low
    learning_path: List[LearningResource] = []


class SkillMatchDetail(BaseModel):
    skill: str
    matched: bool
    confidence: Optional[float] = None
    category: Optional[str] = None


class ScoreCard(BaseModel):
    ats_score: float
    resume_quality_score: float
    technical_skill_score: float
    employability_score: float


class MatchResponse(BaseModel):
    id: int
    resume_id: int
    job_description_id: int
    overall_match_score: float
    skill_match_score: float
    experience_match_score: float
    education_match_score: float
    project_relevance_score: float
    keyword_match_score: float
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    skill_details: List[SkillMatchDetail] = []
    skill_gap_analysis: List[SkillGapItem] = []
    recommendations: List[str] = []
    improvement_suggestions: List[str] = []
    ats_compatibility: float
    keyword_optimization: Optional[List[str]] = []
    scorecard: Optional[ScoreCard] = None
    created_at: datetime

    class Config:
        from_attributes = True
