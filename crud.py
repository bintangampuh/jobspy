from sqlalchemy.orm import Session
from sqlalchemy import text, func
import pandas as pd
import models
import schemas
from datetime import datetime, timedelta
from typing import List

def get_blocked_companies(db: Session) -> list[str]:
    blocked_entities = db.query(models.BlockedEntity.entity_name).filter(models.BlockedEntity.entity_type == 'company').all()
    return [entity[0] for entity in blocked_entities]

def bulk_insert_jobs(db: Session, df: pd.DataFrame):
    if df.empty:
        return 0
    
    # Mapping column names from the DataFrame to the database table columns
    column_mapping = {
        'job_url_direct': None,
        'job_posting_url': 'job_url',
        'site': 'source',
        'date_posted': 'posted_at',
        'company': 'company_name'
    }
    df_renamed = df.rename(columns=column_mapping)
    
    # Ensuring all required columns exist, adding None as default if they don't
    required_cols = ['job_url', 'title', 'company_name', 'location', 'description', 'job_type', 'source', 'posted_at']
    for col in required_cols:
        if col not in df_renamed.columns:
            df_renamed[col] = None

    jobs_to_insert = df_renamed[required_cols].to_dict(orient='records')
    
    insert_statement = text("""
        INSERT INTO scraped_jobs (job_url, title, company_name, location, description, job_type, source, posted_at, status, is_imported_to_ats)
        VALUES (:job_url, :title, :company_name, :location, :description, :job_type, :source, :posted_at, 'online', FALSE)
        ON CONFLICT (job_url) DO UPDATE 
        SET 
            last_seen_at = NOW(),
            status = 'online';
    """)
    
    try:
        result = db.execute(insert_statement, jobs_to_insert)
        db.commit()
        return result.rowcount
    except Exception as e:
        db.rollback()
        print(f"🔴 Error during bulk insert: {e}")
        return 0

def block_company(db: Session, request: schemas.BlockCompanyRequest):
    existing_company = db.query(models.BlockedEntity).filter(models.BlockedEntity.entity_name == request.entity_name).first()
    if existing_company:
        return None 

    db_blocked = models.BlockedEntity(
        entity_name=request.entity_name,
        blocked_by_user_id=request.blocked_by_user_id,
        reason=request.reason
    )
    db.add(db_blocked)
    db.commit()
    db.refresh(db_blocked)
    return db_blocked

def create_job_match(db: Session, request: schemas.JobMatchRequest):
    job_exists = db.query(models.ScrapedJob).filter(models.ScrapedJob.id == request.scraped_job_id).first()
    if not job_exists:
        return None

    db_match = models.JobMatch(
        candidate_id=request.candidate_id,
        scraped_job_id=request.scraped_job_id,
        match_status=request.match_status
    )
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def mark_job_as_imported(db: Session, job_id: int):
    """
    Finds a job by its ID and changes its is_imported_to_ats status to True.
    """
    db_job = db.query(models.ScrapedJob).filter(models.ScrapedJob.id == job_id).first()
    
    if db_job:
        db_job.is_imported_to_ats = True
        db.commit()
        db.refresh(db_job)
        return db_job
        
    return None

def mark_unseen_jobs_as_deleted(db: Session, scrape_start_time: datetime):
    """
    Marks all jobs with 'online' status as 'deleted' if they haven't been seen
    since a specific time.
    """
    update_statement = text("""
        UPDATE scraped_jobs
        SET status = 'deleted'
        WHERE last_seen_at < :start_time AND status = 'online';
    """)
    try:
        result = db.execute(update_statement, {"start_time": scrape_start_time})
        db.commit()
        print(f"✅ Status synchronization finished: {result.rowcount} jobs marked as 'deleted'.")
        return result.rowcount
    except Exception as e:
        db.rollback()
        print(f"🔴 Error during status synchronization: {e}")
        return 0

def delete_old_deleted_jobs(db: Session):
    """
    Permanently deletes jobs with 'deleted' status that were last seen
    more than 7 days ago.
    """
    delete_statement = text("""
        DELETE FROM scraped_jobs
        WHERE status = 'deleted' AND last_seen_at < NOW() - INTERVAL '7 days';
    """)
    try:
        result = db.execute(delete_statement)
        db.commit()
        print(f"🧹 Cleanup finished: {result.rowcount} old jobs permanently deleted.")
        return result.rowcount
    except Exception as e:
        db.rollback()
        print(f"🔴 Error during cleanup: {e}")
        return 0

def search_jobs(db: Session, query: str = None, location: str = None, page: int = 1, limit: int = 20):
    """Searches for jobs in the database with filters and pagination."""
    q = db.query(models.ScrapedJob)
    
    if query:
        q = q.filter(models.ScrapedJob.title.ilike(f"%{query}%"))
        
    if location:
        q = q.filter(models.ScrapedJob.location.ilike(f"%{location}%"))
        
    total_jobs = q.count()
    
    offset = (page - 1) * limit
    
    jobs = q.offset(offset).limit(limit).all()
    
    return {"total": total_jobs, "page": page, "limit": limit, "data": jobs}

def find_matches_for_candidate(db: Session, candidate_id: str):
    """
    Finds suitable jobs for a candidate.
    (This logic can be expanded to be more complex).
    """
    # **ASSUMPTION**: In a real-world scenario, we would connect to the main ATS database here
    # to retrieve candidate data based on the candidate_id.
    # For now, we are creating dummy data as if we found it.
    
    candidate_profile = {"location": "Amsterdam", "skills": ["Python", "SQL"]}
    
    if not candidate_profile:
        return []
        
    # Simple matching logic: find jobs in the same location
    # that haven't been imported to the ATS yet.
    matches = db.query(models.ScrapedJob).filter(
        models.ScrapedJob.location.ilike(f"%{candidate_profile['location']}%"),
        models.ScrapedJob.is_imported_to_ats == False 
    ).limit(10).all() # Limit to the top 10 results
    
    return matches

def get_dashboard_stats(db: Session):
    """Retrieves statistics for the dashboard."""
    
    total_jobs = db.query(models.ScrapedJob).count()
    
    time_24h_ago = datetime.utcnow() - timedelta(hours=24)
    
    new_jobs_query = text("SELECT COUNT(id) FROM scraped_jobs WHERE scraped_at >= :time_ago")
    new_jobs = db.execute(new_jobs_query, {"time_ago": time_24h_ago}).scalar_one_or_none() or 0
    
    deleted_jobs_query = text("""
        SELECT COUNT(id) FROM scraped_jobs 
        WHERE status = 'deleted' AND last_seen_at >= :time_ago
    """)
    deleted_jobs = db.execute(deleted_jobs_query, {"time_ago": time_24h_ago}).scalar_one_or_none() or 0
    
    return {
        "total_jobs": total_jobs,
        "new_jobs_last_24h": new_jobs,
        "deleted_jobs_last_24h": deleted_jobs
    }

def get_client_companies_from_ats(db: Session) -> List[str]:
    """
    ASSUMPTION: This function would connect to the main ATS database and retrieve
    a list of company names that are clients. For now, we are creating a dummy list.
    """
    # Replace this list with company names that exist in your scraped_jobs database for testing
    return ["Crocs", "Spearne Gasthuis", "Adyen", "Booking.com"]

def find_new_jobs_from_clients(db: Session, client_companies: List[str]):
    """
    Searches for new jobs (in the last 24 hours) from a list of client companies.
    """
    time_24h_ago = datetime.utcnow() - timedelta(hours=24)
    
    new_client_jobs = db.query(models.ScrapedJob).filter(
        models.ScrapedJob.company_name.in_(client_companies),
        models.ScrapedJob.scraped_at >= time_24h_ago
    ).all()
    
    return new_client_jobs