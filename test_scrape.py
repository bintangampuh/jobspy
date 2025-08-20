# test_scrape.py
from jobspy import scrape_jobs
import pandas as pd

pd.set_option('display.max_columns', None)

print("Menjalankan tes scraping untuk 'Data Scientist' di 'Utrecht'...")

try:
    jobs = scrape_jobs(
        site_name=["indeed"],
        search_term="Data Scientist",
        location="Utrecht",
        results_wanted=5,
        country_indeed='Netherlands'
    )
    print(f"Tes selesai! Ditemukan {len(jobs)} pekerjaan.")
    if not jobs.empty:
        print(jobs)
except Exception as e:
    print(f"Terjadi error saat tes: {e}")