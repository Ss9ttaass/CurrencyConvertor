import httpx
from datetime import date
from sqlalchemy.orm import Session
from app.models import ExchangeRate

NBRB_API_URL = "https://api.nbrb.by/exrates/rates?periodicity=0"

async def load_rates(db: Session):
    async with httpx.AsyncClient() as client:
        resp = await client.get(NBRB_API_URL)
        data = resp.json()

    today = date.today()
    for item in data:
        currency = item["Cur_Abbreviation"]
        rate = item["Cur_OfficialRate"] / item["Cur_Scale"]
        existing = db.query(ExchangeRate).filter(
            ExchangeRate.on_date == today,
            ExchangeRate.currency == currency
        ).first()
        if not existing:
            db.add(ExchangeRate(on_date=today, currency=currency, rate_byn=rate))
    db.commit()
