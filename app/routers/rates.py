from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.rates import load_rates

router = APIRouter(tags=["rates"])

@router.post("/load-rates")
async def load_rates_endpoint(db: Session = Depends(get_db)):
    await load_rates(db)
    return {"status": "ok"}
