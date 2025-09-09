from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class BlockCompanyRequest(BaseModel):
    entity_name: str
    blocked_by_user_id: str
    reason: Optional[str] = None

class JobMatchRequest(BaseModel):
    candidate_id: str
    scraped_job_id: int
    match_status: str

    model_config = ConfigDict(from_attributes=True)

class Job(BaseModel):
    id: int
    title: str
    company_name: str
    location: Optional[str] = None
    job_url: str
    source: str
    is_imported_to_ats: bool

    model_config = ConfigDict(from_attributes=True)

class PaginatedJobs(BaseModel):
    total: int
    page: int
    limit: int
    data: List[Job]

class DashboardStats(BaseModel):
    total_jobs: int
    new_jobs_last_24h: int
    deleted_jobs_last_24h: int