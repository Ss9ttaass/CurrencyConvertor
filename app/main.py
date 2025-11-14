from fastapi import FastAPI
from app.database import engine, Base, SessionLocal
from app.routers import rates, deals, reports
from app.services.rates import load_rates
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Currency Exchange Service")

app.include_router(rates.router, prefix="/api/v1")
app.include_router(deals.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")

def load_rates_daily():
    db = SessionLocal()
    asyncio.run(load_rates(db))
    db.close()

@app.on_event("startup")
async def startup_event():

    db = SessionLocal()
    await load_rates(db)
    db.close()


    scheduler = BackgroundScheduler()
    scheduler.add_job(load_rates_daily, "cron", hour=9, minute=0)
    scheduler.start()
