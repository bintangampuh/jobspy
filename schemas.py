# schemas.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

class BlockCompanyRequest(BaseModel):
    entity_name: str
    blocked_by_user_id: str
    reason: Optional[str] = None

class JobMatchRequest(BaseModel):
    candidate_id: str
    scraped_job_id: int
    match_status: str

    model_config = ConfigDict(from_attributes=True)