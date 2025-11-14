from sqlalchemy import Column, String, Date, DECIMAL, DateTime, Enum
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.sql import func
import enum
import uuid
from .database import Base


class DealStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    on_date = Column(Date, index=True)
    currency = Column(String, index=True)
    rate_byn = Column(DECIMAL(12, 6))


class Deal(Base):
    __tablename__ = "deals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    base_currency = Column(String)
    target_currency = Column(String)
    base_amount = Column(DECIMAL(12, 2))
    target_amount = Column(DECIMAL(12, 2))
    rate_base_to_target = Column(DECIMAL(12, 6))
    status = Column(Enum(DealStatus), default=DealStatus.PENDING)
