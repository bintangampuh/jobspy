# create_tables.py

# Impor engine dan Base dari file database.py
from database import engine, Base

# PENTING: Impor semua model Anda di sini.
# Tindakan ini akan "mendaftarkan" semua kelas tabel Anda (ScrapedJob, dll.)
# ke dalam objek Base yang kita impor dari database.py.
import models

print("Mencoba membuat semua tabel database...")

# Sekarang kita panggil create_all. Karena model sudah diimpor di atas,
# Base.metadata dijamin sudah berisi skema tabel Anda.
Base.metadata.create_all(bind=engine)

print("Tabel berhasil dibuat (jika belum ada). Silakan periksa dashboard Supabase Anda.")