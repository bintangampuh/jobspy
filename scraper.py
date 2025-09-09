import os
import json
import time
import random
import pandas as pd
from sqlalchemy.orm import Session
from jobspy import scrape_jobs
import crud
from database import SessionLocal
from datetime import datetime, timezone

def _scrape_single_site(db: Session, site_name: str, keywords: dict, blocked_companies: list, proxy_config: str = None):
    """
    Helper function to scrape a single website and save the results.
    Returns the number of jobs successfully processed.
    """
    total_jobs_for_site = 0
    
    for location in keywords.get("locations", []):
        for title in keywords.get("job_titles", []):
            print(f"🔍 Searching [{site_name.upper()}]: '{title}' in '{location}'...")
            try:
                scraped_df = scrape_jobs(
                    site_name=[site_name],
                    search_term=f'"{title}"',
                    location=location,
                    results_wanted=25,
                    country_indeed='Netherlands',
                    proxies=[proxy_config] if proxy_config else None,
                    verify=False
                )
                
                if scraped_df is not None and not scraped_df.empty:
                    if 'company' not in scraped_df.columns:
                        print("  -> Invalid scraping result (required column 'company' not found). Skipping.")
                        continue

                    scraped_df.drop_duplicates(subset=['title', 'company', 'location'], keep='first', inplace=True)
                    filtered_df = scraped_df[~scraped_df['company'].isin(blocked_companies)]
                    
                    if not filtered_df.empty:
                        count = crud.bulk_insert_jobs(db, filtered_df)
                        total_jobs_for_site += count
                        print(f"  -> Successfully saved/updated {count} jobs.")
                    else:
                        print("  -> No jobs left after filtering blocked companies.")
                else:
                    print("  -> No results for this query.")
                
                time.sleep(random.uniform(5, 10))
            except Exception as e:
                print(f"🔴 Error on query [{site_name.upper()}]: '{title}' in '{location}'. Error: {e}")
                continue
                
    return total_jobs_for_site

def run_full_scrape_process():
    """Main worker function that runs the entire scraping process."""
    print("🚀 Starting large scraping process...")
    scrape_start_time = datetime.now(timezone.utc)
    print(f"🕒 Cycle start time: {scrape_start_time}")

    try:
        with open('keywords.json', 'r') as f:
            KEYWORDS = json.load(f)
    except FileNotFoundError:
        print("🔴 'keywords.json' file not found. Process cancelled.")
        return

    scraperapi_key = os.getenv('SCRAPERAPI_API_KEY')
    db: Session = SessionLocal()
    total_processed_count = 0
    
    try:
        blocked_companies = crud.get_blocked_companies(db)
        print(f"🚫 Companies to be excluded: {len(blocked_companies)}.")

        # --- STAGE 1: SCRAPING FROM INDEED ---
        print("\n--- STAGE 1: STARTING SCRAPE FROM INDEED ---")
        total_processed_count += _scrape_single_site(
            db=db, 
            site_name="indeed", 
            keywords=KEYWORDS, 
            blocked_companies=blocked_companies
        )
        
        # --- STAGE 2: SCRAPING FROM LINKEDIN ---
        # print("\n--- STAGE 2: STARTING SCRAPE FROM LINKEDIN ---")
        # proxy_config = None
        # if scraperapi_key:
        #     proxy_config = f"http://scraperapi.country_code=nl:{scraperapi_key}@proxy-server.scraperapi.com:8001"
        #     print("✅ ScraperAPI proxy configuration will be used.")
        # else:
        #     print("🟡 Warning: No proxy API Key found. LinkedIn scraping may fail.")

        # total_processed_count += _scrape_single_site(
        #     db=db, 
        #     site_name="linkedin", 
        #     keywords=KEYWORDS, 
        #     blocked_companies=blocked_companies, 
        #     proxy_config=proxy_config
        # )
        
    except Exception as e:
        print(f"🔴 A fatal error occurred during the scraping process: {e}")
    finally:
        print(f"\n✅ Scraping process finished. Total new/updated jobs across all sites: {total_processed_count}")
        
        print("🔄 Starting job status synchronization...")
        crud.mark_unseen_jobs_as_deleted(db=db, scrape_start_time=scrape_start_time)
        
        db.close()
        print("🔚 Database connection closed. Process complete.")