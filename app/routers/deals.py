from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Deal, ExchangeRate, DealStatus
from datetime import date

router = APIRouter(tags=["deals"])

@router.post("/quote")
def quote(amount: float, base_currency: str, target_currency: str, db: Session = Depends(get_db)):
    today = date.today()
    base_rate = db.query(ExchangeRate).filter_by(on_date=today, currency=base_currency).first()
    target_rate = db.query(ExchangeRate).filter_by(on_date=today, currency=target_currency).first()
    if not base_rate or not target_rate:
        raise HTTPException(404, "Rates not found for given currencies")

    rate = float(base_rate.rate_byn) / float(target_rate.rate_byn)
    target_amount = amount * rate

    deal = Deal(
        base_currency=base_currency,
        target_currency=target_currency,
        base_amount=amount,
        target_amount=target_amount,
        rate_base_to_target=rate,
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)

    return {
        "deal_id": deal.id,
        "rate": rate,
        "target_amount": target_amount,
        "status": deal.status
    }

@router.post("/deals/{deal_id}/confirm")
def confirm_deal(deal_id: str, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter_by(id=deal_id).first()
    if not deal:
        raise HTTPException(404, "Deal not found")
    deal.status = DealStatus.CONFIRMED
    db.commit()
    return {"status": deal.status}

@router.post("/deals/{deal_id}/reject")
def reject_deal(deal_id: str, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter_by(id=deal_id).first()
    if not deal:
        raise HTTPException(404, "Deal not found")
    deal.status = DealStatus.REJECTED
    db.commit()
    return {"status": deal.status}

@router.get("/deals/pending")
def pending_deals(db: Session = Depends(get_db)):
    deals = db.query(Deal).filter_by(status=DealStatus.PENDING).all()
    return [
        {
            "deal_id": d.id,
            "base_currency": d.base_currency,
            "target_currency": d.target_currency,
            "base_amount": float(d.base_amount),
            "rate": float(d.rate_base_to_target),
        } for d in deals
    ]
