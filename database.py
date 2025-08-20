# database.py (REVISED)

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base # <== Perbaikan warning

load_dotenv()

DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base() # Base ini akan diimpor oleh models.py dan create_tables.py

def get_db():
    """Fungsi helper untuk dependency injection session database."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Blok if __name__ == "__main__" dan fungsi create_all_tables() dihapus dari sini.