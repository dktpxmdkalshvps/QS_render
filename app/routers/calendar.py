from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MarketCalendar
from app.schemas import MarketCalendarCreate, MarketCalendarOut

router = APIRouter(prefix='/api/market-calendar', tags=['market-calendar'])


@router.get('', response_model=list[MarketCalendarOut])
def list_market_calendar(
    market: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[MarketCalendar]:
    stmt = select(MarketCalendar)
    if market:
        stmt = stmt.where(MarketCalendar.market == market.upper())
    if start_date:
        stmt = stmt.where(MarketCalendar.date >= start_date)
    if end_date:
        stmt = stmt.where(MarketCalendar.date <= end_date)
    stmt = stmt.order_by(MarketCalendar.date.desc()).limit(limit)
    return list(db.scalars(stmt).all())


@router.post('', response_model=MarketCalendarOut, status_code=201)
def upsert_market_calendar(payload: MarketCalendarCreate, db: Session = Depends(get_db)) -> MarketCalendar:
    market = payload.market.upper().strip()
    row = db.scalar(select(MarketCalendar).where(MarketCalendar.market == market, MarketCalendar.date == payload.date))
    if row is None:
        row = MarketCalendar(market=market, date=payload.date, is_open=payload.is_open, note=payload.note)
        db.add(row)
    else:
        row.is_open = payload.is_open
        row.note = payload.note
    db.commit()
    db.refresh(row)
    return row
