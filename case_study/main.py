# main.py
from fastapi import FastAPI
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
from src.scraper import scrape_and_store
from src.db.session import get_session
from src.db.models import CampgroundORM
from src.schemas import CampgroundOut  # Pydantic model
import logging

from src.db.init_db import init_db


app = FastAPI()
scheduler = BackgroundScheduler()
scheduler_started = False

@app.on_event("startup")
def start_scheduler():
    global scheduler_started
    init_db()  # 🔥 ORM tablolarını oluşturur
    if not scheduler_started:
        scheduler.add_job(scrape_and_store, 'interval', hours=2, max_instances=1)
        scheduler.start()
        logging.basicConfig(level=logging.INFO)
        logging.info("🔄 Scheduler başlatıldı: 2 saatte bir scraper çalışacak.")
        scheduler_started = True


@app.get("/ping")
def ping():
    return {"message": "API ayakta"}

@app.post("/trigger")
def trigger_scrape():
    Thread(target=scrape_and_store).start()
    return {"message": "Scraper tetiklendi 🚀"}

@app.get("/campgrounds", response_model=list[CampgroundOut])
def get_campgrounds():
    try:
        session = get_session()
        campgrounds = session.query(CampgroundORM).all()
        session.close()
        return campgrounds
    except Exception as e:
        return {"error": str(e)}
