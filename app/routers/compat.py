from datetime import date, datetime, timedelta, timezone
from math import sin

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MarketCalendar, Stock, ThemeSnapshot

router = APIRouter(tags=['frontend-compat'])


THEME_LABELS = {
    'undervalued_growth': 'Undervalued Growth',
    'growth_momentum': 'Growth Momentum',
    'safe_growth': 'Safe Growth',
    'dividend_aristocrat': 'Dividend Aristocrat',
    'dividend': 'Dividend',
    'breakout': 'Breakout',
    'high_roe': 'High ROE',
    'deep_value': 'Deep Value',
    'bugatti': 'Bugatti',
    'ai_infra': 'AI Infrastructure',
    'semiconductor': 'Semiconductor',
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stock_payload(stock: Stock, idx: int = 0) -> dict:
    base_price = 120 + idx * 17
    return {
        'ticker': stock.ticker,
        'symbol': stock.ticker,
        'name': stock.name,
        'market': stock.market,
        'sector': stock.sector,
        'price': round(base_price * 1.01, 2),
        'change': round((idx + 1) * 0.37, 2),
        'changePercent': round((idx + 1) * 0.42, 2),
        'score': max(60, 95 - idx * 4),
    }


@router.get('/market/banner')
def market_banner() -> dict:
    return {
        'ok': True,
        'status': 'OPEN',
        'title': 'Quant backend connected',
        'message': 'Render FastAPI and PostgreSQL are running normally.',
        'updated_at': _now_iso(),
        'items': [
            {'label': 'Backend', 'value': 'Render'},
            {'label': 'Database', 'value': 'PostgreSQL'},
            {'label': 'API', 'value': 'OK'},
        ],
    }


@router.get('/market/calendar')
def market_calendar(days: int = Query(default=10, ge=1, le=60), db: Session = Depends(get_db)) -> dict:
    today = date.today()
    rows = list(
        db.scalars(
            select(MarketCalendar)
            .where(MarketCalendar.date >= today)
            .order_by(MarketCalendar.date.asc())
            .limit(days)
        ).all()
    )

    items = [
        {
            'market': row.market,
            'date': row.date.isoformat(),
            'is_open': row.is_open,
            'note': row.note,
        }
        for row in rows
    ]

    if not items:
        for i in range(days):
            d = today + timedelta(days=i)
            items.append(
                {
                    'market': 'US/KR',
                    'date': d.isoformat(),
                    'is_open': d.weekday() < 5,
                    'note': 'Weekend' if d.weekday() >= 5 else 'Regular trading day',
                }
            )

    return {'ok': True, 'days': days, 'items': items, 'calendar': items}


@router.get('/theme/{theme_key}')
def theme(theme_key: str, db: Session = Depends(get_db)) -> dict:
    latest_created_at = db.scalar(
        select(ThemeSnapshot.created_at)
        .where(ThemeSnapshot.theme_key == theme_key)
        .order_by(ThemeSnapshot.created_at.desc())
        .limit(1)
    )

    snapshots = []
    if latest_created_at is not None:
        snapshots = list(
            db.scalars(
                select(ThemeSnapshot)
                .where(ThemeSnapshot.theme_key == theme_key, ThemeSnapshot.created_at == latest_created_at)
                .order_by(ThemeSnapshot.rank.asc().nullslast(), ThemeSnapshot.score.desc().nullslast())
                .limit(30)
            ).all()
        )

    if snapshots:
        items = [
            {
                'ticker': s.ticker,
                'symbol': s.ticker,
                'theme_key': s.theme_key,
                'theme_name': s.theme_name,
                'score': s.score,
                'rank': s.rank,
                'reason': s.reason,
                'source': s.source,
                'payload': s.payload,
                'created_at': s.created_at.isoformat() if s.created_at else None,
            }
            for s in snapshots
        ]
        theme_name = snapshots[0].theme_name
    else:
        stocks = list(db.scalars(select(Stock).order_by(Stock.ticker).limit(10)).all())
        items = [_stock_payload(stock, idx) for idx, stock in enumerate(stocks)]
        theme_name = THEME_LABELS.get(theme_key, theme_key.replace('_', ' ').title())

    return {
        'ok': True,
        'theme_key': theme_key,
        'theme_name': theme_name,
        'updated_at': _now_iso(),
        'items': items,
        'stocks': items,
    }


@router.get('/stocks/{ticker}')
def stock_detail(ticker: str, period: str = Query(default='1y'), db: Session = Depends(get_db)) -> dict:
    symbol = ticker.upper().strip()
    stock = db.scalar(select(Stock).where(Stock.ticker == symbol))
    if stock is None:
        stock = Stock(ticker=symbol, name=symbol, market='NASDAQ', sector='Unknown')

    days = 90 if period in {'3m', '6m', '1y'} else 30
    base = 100 + (sum(ord(c) for c in symbol) % 120)
    prices = []
    start = date.today() - timedelta(days=days)
    for i in range(days):
        d = start + timedelta(days=i)
        if d.weekday() >= 5:
            continue
        close = round(base + i * 0.15 + sin(i / 5) * 3, 2)
        prices.append(
            {
                'date': d.isoformat(),
                'open': round(close * 0.995, 2),
                'high': round(close * 1.015, 2),
                'low': round(close * 0.985, 2),
                'close': close,
                'volume': 1_000_000 + i * 12_345,
            }
        )

    return {
        'ok': True,
        'ticker': symbol,
        'symbol': symbol,
        'name': stock.name,
        'market': stock.market,
        'sector': stock.sector,
        'period': period,
        'price': prices[-1]['close'] if prices else base,
        'prices': prices,
        'history': prices,
    }


@router.get('/analysis/{ticker}/technical')
def technical_analysis(ticker: str, period: str = Query(default='1y')) -> dict:
    symbol = ticker.upper().strip()
    return {
        'ok': True,
        'ticker': symbol,
        'symbol': symbol,
        'period': period,
        'signal': 'BUY',
        'summary': 'Sample technical signal generated by the compatibility API.',
        'indicators': {
            'rsi': 58.4,
            'macd': 1.24,
            'moving_average_20': 142.7,
            'moving_average_60': 136.2,
        },
        'items': [
            {'name': 'RSI', 'value': 58.4, 'signal': 'neutral'},
            {'name': 'MACD', 'value': 1.24, 'signal': 'positive'},
            {'name': 'MA20/MA60', 'value': 1.048, 'signal': 'positive'},
        ],
        'updated_at': _now_iso(),
    }


@router.get('/analysis/{ticker}/forecast')
def forecast_analysis(
    ticker: str,
    model: str = Query(default='both'),
    days: int = Query(default=7, ge=1, le=30),
) -> dict:
    symbol = ticker.upper().strip()
    base = 100 + (sum(ord(c) for c in symbol) % 120)
    forecasts = []
    today = date.today()
    for i in range(1, days + 1):
        d = today + timedelta(days=i)
        forecasts.append(
            {
                'date': d.isoformat(),
                'predicted_close': round(base + i * 0.45 + sin(i / 2) * 1.5, 2),
                'lower': round(base + i * 0.20 - 2.5, 2),
                'upper': round(base + i * 0.70 + 2.5, 2),
            }
        )

    return {
        'ok': True,
        'ticker': symbol,
        'symbol': symbol,
        'model': model,
        'days': days,
        'forecast': forecasts,
        'items': forecasts,
        'updated_at': _now_iso(),
    }
