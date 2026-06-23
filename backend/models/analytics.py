from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from sqlalchemy.sql import func
from database import Base


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    event_type = Column(String(100))   # resume_upload, match_generated, etc.
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
