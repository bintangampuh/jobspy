from jobspy import scrape_jobs
import pandas as pd

# Mengatur agar pandas menampilkan semua kolom
pd.set_option('display.max_columns', None)

print("Mulai mengambil data pekerjaan...")

# Menjalankan scraper dengan parameter spesifik untuk proyek Anda
jobs = scrape_jobs(
    site_name=["indeed"],
    search_term="software engineer",
    location="Netherlands",
    results_wanted=10,
    country_indeed='Netherlands' # Parameter wajib untuk Indeed
)

print(f"\nSelesai! Ditemukan {len(jobs)} pekerjaan.")

# Menampilkan 5 hasil pertama
if not jobs.empty:
    print("Berikut adalah 5 hasil pertama:")
    print(jobs.head())