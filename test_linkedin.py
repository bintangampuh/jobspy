# test_linkedin.py (Versi untuk ScraperAPI)
import os
import pandas as pd
from dotenv import load_dotenv
from jobspy import scrape_jobs

# Muat environment variables
load_dotenv()

# API key ScraperAPI
scraperapi_key = os.getenv("SCRAPERAPI_API_KEY")
proxy_config = None

if scraperapi_key:
    # Format proxy untuk ScraperAPI
    proxy_config = f"http://scraperapi:{scraperapi_key}@proxy-server.scraperapi.com:8001"
    print("✅ Proxy ScraperAPI terdeteksi dan akan digunakan.")
else:
    print("⚠️ API Key ScraperAPI tidak ditemukan di .env")

print("\n🚀 Mulai mengambil data pekerjaan dari LinkedIn...")

try:
    jobs = scrape_jobs(
        site_name=["linkedin"],
        search_term="software engineer",
        location="Netherlands",
        results_wanted=10,
        proxies=[proxy_config] if proxy_config else None,
        verify=False,
    )

    print(f"\n🎉 Selesai! Ditemukan {len(jobs)} pekerjaan.")

    if not jobs.empty:
        print("📌 Berikut adalah 5 hasil pertama:")
        print(jobs.head())
    else:
        print("⚠️ Tidak ada pekerjaan ditemukan. Coba cek apakah request sudah melebihi kuota trial (1.000 req).")

except Exception as e:
    print("\n❌ ERROR saat scraping LinkedIn:")
    print(str(e))
