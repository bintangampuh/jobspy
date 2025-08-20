# scraper.py (FINAL VERSION)

import os
import json
import time
import random
import pandas as pd
from sqlalchemy.orm import Session
from jobspy import scrape_jobs
import crud
from database import SessionLocal

def run_full_scrape_process():
    """Fungsi worker utama yang melakukan seluruh proses scraping."""
    print("Memulai proses scraping besar...")
    
    try:
        with open('keywords.json', 'r') as f:
            KEYWORDS = json.load(f)
    except FileNotFoundError:
        print("File 'keywords.json' tidak ditemukan. Proses dibatalkan.")
        return

    scraperapi_key = os.getenv('SCRAPERAPI_API_KEY')
    db: Session = SessionLocal()
    
    total_processed_count = 0
    
    try:
        blocked_companies = crud.get_blocked_companies(db)
        print(f"Perusahaan yang akan dikecualikan: {len(blocked_companies)} perusahaan.")

        SITES_TO_SCRAPE = ["indeed", "linkedin"]

        for site_name in SITES_TO_SCRAPE:
            if site_name == "indeed":
                print("\n--- TAHAP 1: MEMULAI SCRAPING DARI INDEED (TANPA PROXY) ---")
                proxy_config = None
            elif site_name == "linkedin":
                print("\n--- TAHAP 2: MEMULAI SCRAPING DARI LINKEDIN (DENGAN PROXY) ---")
                if scraperapi_key:
                    proxy_config = f"http://scraperapi.country_code=nl:{scraperapi_key}@proxy-server.scraperapi.com:8001"
                    print("Konfigurasi proxy ScraperAPI akan digunakan.")
                else:
                    proxy_config = None
                    print("Peringatan: Tidak ada API Key proxy untuk LinkedIn. Scraping mungkin gagal.")
            else:
                continue

            for location in KEYWORDS.get("locations", []):
                for title in KEYWORDS.get("job_titles", []):
                    print(f"Mencari [{site_name.upper()}]: '{title}' di '{location}'...")
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
                            # PASTIKAN MENGGUNAKAN 'company' SESUAI OUTPUT jobspy
                            if 'company' not in scraped_df.columns or 'title' not in scraped_df.columns:
                                print("  -> Hasil scraping tidak valid (kolom penting tidak ada). Dilewati.")
                                continue

                            scraped_df.drop_duplicates(subset=['title', 'company', 'location'], keep='first', inplace=True)
                            filtered_df = scraped_df[~scraped_df['company'].isin(blocked_companies)]
                            
                            if not filtered_df.empty:
                                count = crud.bulk_insert_jobs(db, filtered_df)
                                total_processed_count += count
                                print(f"  -> Berhasil menyimpan/memperbarui {count} lowongan.")
                            else:
                                print("  -> Tidak ada lowongan tersisa setelah filter perusahaan yang diblokir.")
                        else:
                            print("  -> Tidak ada hasil untuk kueri ini.")
                        
                        # Jeda yang lebih aman untuk menghindari blokir
                        time.sleep(random.uniform(10, 20))

                    except Exception as e:
                        print(f"Error pada kueri [{site_name.upper()}]: '{title}' di '{location}'. Error: {e}")
                        continue
    
    finally:
        print(f"\nProses scraping selesai. Total lowongan baru/diperbarui di semua situs: {total_processed_count}")
        db.close()