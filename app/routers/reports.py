from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models import Deal, DealStatus

router = APIRouter(tags=["reports"])

@router.get("/reports/deals")
def report_deals(
    date_from: date = Query(...),
    date_to: date = Query(...),
    currency: str | None = Query(None),
    db: Session = Depends(get_db),
):

    dt_from = datetime.combine(date_from, datetime.min.time())
    dt_to = datetime.combine(date_to + timedelta(days=1), datetime.min.time())

    deals = (
        db.query(Deal)
        .filter(
            Deal.status == DealStatus.CONFIRMED,
            Deal.created_at >= dt_from,
            Deal.created_at < dt_to,
        )
        .all()
    )

    agg = {}
    def touch(cur):
        if cur not in agg:
            agg[cur] = {"cash_in": 0.0, "cash_out": 0.0, "deal_count": 0}

    for d in deals:
        touch(d.base_currency)
        agg[d.base_currency]["cash_in"] += float(d.base_amount)
        agg[d.base_currency]["deal_count"] += 1

        touch(d.target_currency)
        agg[d.target_currency]["cash_out"] += float(d.target_amount)
        agg[d.target_currency]["deal_count"] += 1

    items = [
        {
            "currency": cur,
            "cash_in": round(v["cash_in"], 2),
            "cash_out": round(v["cash_out"], 2),
            "deal_count": v["deal_count"],
        }
        for cur, v in agg.items()
    ]

    if currency:
        items = [x for x in items if x["currency"] == currency]

    items.sort(key=lambda x: x["currency"])
    return items
