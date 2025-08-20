# models.py

from sqlalchemy import Boolean, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class ScrapedJob(Base):
    __tablename__ = "scraped_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_url = Column(Text, unique=True, index=True, nullable=False)
    title = Column(String(255), index=True)
    company_name = Column(String(255), index=True)
    location = Column(String(255))
    description = Column(Text)
    job_type = Column(String(50), nullable=True)
    source = Column(String(50), index=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String(50), default='online', index=True)
    is_imported_to_ats = Column(Boolean, default=False)
    
    matches = relationship("JobMatch", back_populates="scraped_job")

class JobMatch(Base):
    __tablename__ = "job_matches"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(String(255), index=True, nullable=False)
    scraped_job_id = Column(Integer, ForeignKey("scraped_jobs.id"), nullable=False)
    match_status = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    scraped_job = relationship("ScrapedJob", back_populates="matches")

class BlockedEntity(Base):
    __tablename__ = "blocked_entities"

    id = Column(Integer, primary_key=True, index=True)
    entity_name = Column(String(255), unique=True, index=True, nullable=False)
    entity_type = Column(String(50), default='company')
    reason = Column(Text, nullable=True)
    blocked_by_user_id = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())