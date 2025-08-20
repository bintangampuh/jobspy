# main.py

from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
import crud
import schemas
import scraper  # Pastikan nama file adalah scraper.py
from database import get_db

app = FastAPI(
    title="JobSpy Scraper API",
    description="API untuk mengelola data lowongan hasil scraping."
)

@app.get("/", summary="Endpoint Status Cek")
def read_root():
    """Endpoint untuk halaman utama sebagai penanda server berjalan."""
    return {"message": "Selamat datang di JobSpy Scraping Service!"}

@app.post("/scrape/start", summary="Mulai Proses Scraping Skala Penuh")
def start_full_scrape(background_tasks: BackgroundTasks):
    """
    Memulai proses scraping lengkap (Indeed dan LinkedIn) di background.
    Ini adalah proses yang berjalan lama.
    """
    background_tasks.add_task(scraper.run_full_scrape_process)
    return {"message": "Proses scraping telah dimulai di background. Cek log server untuk melihat progres."}

@app.post("/companies/block", summary="Blokir Perusahaan", status_code=201)
def block_a_company(request: schemas.BlockCompanyRequest, db: Session = Depends(get_db)):
    """
    Menambahkan satu perusahaan ke dalam daftar blokir agar tidak di-scrape lagi di masa depan.
    Akan mengembalikan error 409 jika perusahaan sudah ada.
    """
    result = crud.block_company(db=db, request=request)
    if result:
        return result
    else:
        raise HTTPException(
            status_code=409,  # 409 Conflict
            detail=f"Perusahaan '{request.entity_name}' sudah ada dalam daftar blokir."
        )

@app.post("/matches/create", summary="Buat Pencocokan Kandidat", status_code=201)
def create_a_match(request: schemas.JobMatchRequest, db: Session = Depends(get_db)):
    """
    Menyimpan data pencocokan antara kandidat (dari ATS) dan lowongan hasil scraping.
    Akan mengembalikan error 404 jika ID lowongan tidak ditemukan di database.
    """
    result = crud.create_job_match(db=db, request=request)
    if result:
        return result
    else:
        raise HTTPException(
            status_code=404,  # 404 Not Found
            detail=f"Lowongan dengan ID '{request.scraped_job_id}' tidak ditemukan."
        )