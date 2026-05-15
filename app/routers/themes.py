from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Stock, ThemeSnapshot
from app.schemas import ThemeSnapshotCreate, ThemeSnapshotOut

router = APIRouter(prefix='/api/themes', tags=['themes'])


@router.get('/{theme_key}/snapshots', response_model=list[ThemeSnapshotOut])
def list_theme_snapshots(
    theme_key: str,
    limit: int = Query(default=50, ge=1, le=300),
    db: Session = Depends(get_db),
) -> list[ThemeSnapshot]:
    stmt = (
        select(ThemeSnapshot)
        .where(ThemeSnapshot.theme_key == theme_key)
        .order_by(ThemeSnapshot.created_at.desc(), ThemeSnapshot.rank.asc().nullslast())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


@router.get('/{theme_key}/snapshots/latest', response_model=list[ThemeSnapshotOut])
def latest_theme_snapshot(
    theme_key: str,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ThemeSnapshot]:
    latest_created_at = db.scalar(
        select(ThemeSnapshot.created_at)
        .where(ThemeSnapshot.theme_key == theme_key)
        .order_by(ThemeSnapshot.created_at.desc())
        .limit(1)
    )
    if latest_created_at is None:
        return []
    stmt = (
        select(ThemeSnapshot)
        .where(ThemeSnapshot.theme_key == theme_key, ThemeSnapshot.created_at == latest_created_at)
        .order_by(ThemeSnapshot.rank.asc().nullslast(), ThemeSnapshot.score.desc().nullslast())
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


@router.post('/{theme_key}/snapshots', response_model=ThemeSnapshotOut, status_code=201)
def create_theme_snapshot(theme_key: str, payload: ThemeSnapshotCreate, db: Session = Depends(get_db)) -> ThemeSnapshot:
    if payload.theme_key != theme_key:
        raise HTTPException(status_code=400, detail='Path theme_key and body theme_key must match.')

    ticker = payload.ticker.upper().strip()
    stock = db.scalar(select(Stock).where(Stock.ticker == ticker))
    if stock is None:
        stock = Stock(ticker=ticker, name=ticker, market=None, sector=None)
        db.add(stock)
        db.flush()

    snapshot = ThemeSnapshot(
        theme_key=payload.theme_key,
        theme_name=payload.theme_name,
        ticker=ticker,
        score=payload.score,
        rank=payload.rank,
        reason=payload.reason,
        source=payload.source,
        payload=payload.payload,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)
    return snapshot
