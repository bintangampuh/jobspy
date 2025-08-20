# crud.py

from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
import models
import schemas

def get_blocked_companies(db: Session) -> list[str]:
    blocked_entities = db.query(models.BlockedEntity.entity_name).filter(models.BlockedEntity.entity_type == 'company').all()
    return [entity[0] for entity in blocked_entities]

def bulk_insert_jobs(db: Session, df: pd.DataFrame):
    if df.empty:
        return 0
    
    # Menyesuaikan nama kolom dari DataFrame ke nama kolom di tabel database
    column_mapping = {
        'job_url_direct': None,
        'job_posting_url': 'job_url',
        'site': 'source',
        'date_posted': 'posted_at',
        'company': 'company_name'  # <-- TAMBAHKAN BARIS INI
    }
    df_renamed = df.rename(columns=column_mapping)
    
    # Memastikan semua kolom yang dibutuhkan ada, jika tidak ada beri nilai default None
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
        print(f"Error saat bulk insert: {e}")
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