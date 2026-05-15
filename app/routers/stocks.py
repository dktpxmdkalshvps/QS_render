from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Stock
from app.schemas import StockCreate, StockOut

router = APIRouter(prefix='/api/stocks', tags=['stocks'])


@router.get('', response_model=list[StockOut])
def list_stocks(
    ticker: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Stock]:
    stmt = select(Stock).order_by(Stock.ticker).limit(limit).offset(offset)
    if ticker:
        stmt = select(Stock).where(Stock.ticker.ilike(f'%{ticker}%')).order_by(Stock.ticker).limit(limit).offset(offset)
    return list(db.scalars(stmt).all())


@router.post('', response_model=StockOut, status_code=201)
def upsert_stock(payload: StockCreate, db: Session = Depends(get_db)) -> Stock:
    ticker = payload.ticker.upper().strip()
    stock = db.scalar(select(Stock).where(Stock.ticker == ticker))
    if stock is None:
        stock = Stock(ticker=ticker, name=payload.name, market=payload.market, sector=payload.sector)
        db.add(stock)
    else:
        stock.name = payload.name
        stock.market = payload.market
        stock.sector = payload.sector
    db.commit()
    db.refresh(stock)
    return stock
