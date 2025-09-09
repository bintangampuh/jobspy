from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import crud
import schemas
import scraper 
from database import get_db
from typing import Optional, List

app = FastAPI(
    title="JobSpy Scraper API",
    description="An API to manage scraped job posting data."
)

@app.get("/", summary="Status Check Endpoint")
def read_root():
    """Endpoint for the main page to indicate that the server is running."""
    return {"message": "Welcome to the JobSpy Scraping Service!"}

@app.post("/scrape/start", summary="Start Full-Scale Scraping Process")
def start_full_scrape(background_tasks: BackgroundTasks):
    """
    Starts the complete scraping process (Indeed and LinkedIn) in the background.
    This is a long-running process.
    """
    background_tasks.add_task(scraper.run_full_scrape_process)
    return {"message": "The scraping process has been started in the background. Check the server logs for progress."}

@app.put("/jobs/{job_id}/import", summary="Mark a Job as 'Imported'")
def import_job_to_ats(job_id: int, db: Session = Depends(get_db)):
    """
    Changes the 'is_imported_to_ats' status to True for a specific job.
    This is the implementation of the "One-Click Import" feature.
    """
    imported_job = crud.mark_job_as_imported(db=db, job_id=job_id)
    if not imported_job:
        raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found.")
    
    return {"message": f"Job '{imported_job.title}' has been successfully marked as imported."}

@app.post("/companies/block", summary="Block a Company", status_code=201)
def block_a_company(request: schemas.BlockCompanyRequest, db: Session = Depends(get_db)):
    """
    Adds a company to the blocklist to prevent it from being scraped in the future.
    Will return a 409 error if the company already exists.
    """
    result = crud.block_company(db=db, request=request)
    if result:
        return result
    else:
        raise HTTPException(
            status_code=409,  # 409 Conflict
            detail=f"The company '{request.entity_name}' is already in the blocklist."
        )

@app.post("/matches/create", summary="Create a Candidate Match", status_code=201)
def create_a_match(request: schemas.JobMatchRequest, db: Session = Depends(get_db)):
    """
    Saves a match between a candidate (from the ATS) and a scraped job.
    Will return a 404 error if the job ID is not found in the database.
    """
    result = crud.create_job_match(db=db, request=request)
    if result:
        return result
    else:
        raise HTTPException(
            status_code=404,  # 404 Not Found
            detail=f"Job with ID '{request.scraped_job_id}' not found."
        )
    
@app.get("/jobs/search", summary="Search for Job Postings", response_model=schemas.PaginatedJobs)
def search_for_jobs(
    q: Optional[str] = None, 
    location: Optional[str] = None, 
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Searches for job postings based on a text query (title) and/or location
    with pagination support.
    Example: /jobs/search?q=Software Engineer&location=Amsterdam&page=1&limit=10
    """
    jobs_data = crud.search_jobs(db=db, query=q, location=location, page=page, limit=limit)
    return jobs_data

@app.get("/candidates/{candidate_id}/matches", summary="Find Suitable Jobs for a Candidate", response_model=List[schemas.Job])
def get_candidate_matches(candidate_id: str, db: Session = Depends(get_db)):
    """
    Finds and recommends the top 10 jobs from scraped_jobs
    that are suitable for a specific candidate, simulated by location.
    """
    matched_jobs = crud.find_matches_for_candidate(db=db, candidate_id=candidate_id)
    return matched_jobs

@app.get("/analytics/dashboard", summary="Get Dashboard Statistics", response_model=schemas.DashboardStats)
def get_stats_for_dashboard(db: Session = Depends(get_db)):
    """
    Provides aggregate data to be displayed on an analytics dashboard,
    such as total jobs, new jobs, and deleted jobs.
    """
    stats = crud.get_dashboard_stats(db=db)
    return stats