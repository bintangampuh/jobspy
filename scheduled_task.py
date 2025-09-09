import crud
from database import SessionLocal

def run_cleanup():
    """Runs the database cleanup task for old data."""
    print("Starting database cleanup task...")
    db = SessionLocal()
    try:
        crud.delete_old_deleted_jobs(db)
    finally:
        db.close()
    print("Cleanup task finished.")

if __name__ == "__main__":
    run_cleanup()

def run_scheduled_tasks():
    print("--- Starting scheduled tasks ---")
    db = SessionLocal()
    try:
        print("\n[TASK 1/2] Running cleanup process for old data...")
        crud.delete_old_deleted_jobs(db)

        print("\n[TASK 2/2] Running client job notification check...")
        client_list = crud.get_client_companies_from_ats(db)
        print(f"Searching for new jobs from {len(client_list)} clients...")
        
        new_jobs = crud.find_new_jobs_from_clients(db, client_list)
        
        if new_jobs:
            print(f"✅ FOUND {len(new_jobs)} NEW JOBS FROM CLIENTS:")
            for job in new_jobs:
                print(f"  - Title: {job.title}, Company: {job.company_name}")
            # In a real application, you could add logic here
            # to send an email or a Slack notification.
        else:
            print("ℹ️ No new jobs from clients found in the last 24 hours.")

    finally:
        db.close()
    print("\n--- Scheduled tasks finished ---")

if __name__ == "__main__":
    run_scheduled_tasks()