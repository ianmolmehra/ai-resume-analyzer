from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobDescriptionCreate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    raw_text: str


class JobDescriptionResponse(BaseModel):
    id: int
    title: Optional[str]
    company: Optional[str]
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []
    experience_required: Optional[float] = 0.0
    education_required: Optional[str] = None
    keywords: Optional[List[str]] = []
    created_at: datetime

    class Config:
        from_attributes = True
