import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ortam değişkeninden host bilgisi alınır, yoksa localhost kullanılır
host = os.getenv("DB_HOST", "localhost")
DATABASE_URL = f"postgresql://user:password@{host}:5432/case_study"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()
