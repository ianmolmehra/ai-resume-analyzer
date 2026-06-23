from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class CandidateCreate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None


class CandidateResponse(BaseModel):
    id: int
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    linkedin_url: Optional[str]
    github_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateDetail(CandidateResponse):
    location: Optional[str]
    summary: Optional[str]
    resume_count: Optional[int] = 0
