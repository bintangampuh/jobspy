# test.py (Versi Scraping Google Search)

import os
import requests
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Muat environment variables dari file .env
load_dotenv()

print("--- Memulai Uji Coba Scraping LinkedIn via Google Search ---")

# 1. Ambil API key dari environment
api_key = os.getenv("SCRAPERAPI_API_KEY")

if not api_key:
    print("❌ GAGAL: SCRAPERAPI_API_KEY tidak ditemukan di file .env!")
else:
    print(f"✅ API Key ditemukan.")
    
    # 2. Buat query pencarian Google yang spesifik
    # Ini adalah perintah untuk mencari "Software Engineer" di "Netherlands" khusus di situs linkedin.com/jobs
    google_search_query = 'site:linkedin.com/jobs "Software Engineer" "Netherlands"'
    
    # 3. Ubah query menjadi format URL yang aman
    encoded_query = quote_plus(google_search_query)
    
    # 4. Tentukan URL target, yaitu Google Search
    target_url = f"https://www.google.com/search?q={encoded_query}"
    
    # 5. Buat URL request ke endpoint API ScraperAPI
    scraperapi_url = f"http://api.scraperapi.com?api_key={api_key}&url={target_url}"
    
    print(f"🚀 Mencoba melakukan request ke Google via ScraperAPI...")
    print(f"   URL Target: {target_url}")
    
    try:
        # 6. Lakukan request GET
        response = requests.get(scraperapi_url, timeout=60)
        
        # 7. Periksa hasilnya
        print(f"\n➡️  Status Code Diterima: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ BERHASIL! Koneksi sukses dan mendapatkan halaman hasil pencarian Google.")
            # Menyimpan hasil ke file HTML agar mudah dianalisis
            with open("google_result.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("✅ Hasil pencarian Google telah disimpan ke file 'google_result.html'.")
            
        else:
            print("❌ GAGAL! ScraperAPI mengembalikan error.")
            print("\n--- Respons dari Server ScraperAPI ---")
            print(response.text)
            print("----------------------------------------")
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ GAGAL TOTAL! Terjadi error saat mencoba koneksi.")
        print(f"   Detail Error: {e}")