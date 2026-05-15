from datetime import date, datetime, timedelta, timezone
from math import sin

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MarketCalendar, Stock, ThemeSnapshot

router = APIRouter(tags=['frontend-compat'])


THEME_LABELS = {
    'undervalued_growth': '저평가 성장주',
    'growth_momentum': '모멘텀',
    'safe_growth': '안전 성장',
    'deep_value': '딥 밸류',
    'high_roe': '고 ROE',
    'breakout': '브레이크아웃',
    'bugatti': '부가티',
    'dividend': '배당',
    'dividend_aristocrat': '배당귀족',
}

SECTOR_INDUSTRY = {
    'Semiconductors': 'Semiconductors',
    'Software': 'Application Software',
    'EV': 'Auto Manufacturers',
    'Unknown': 'General',
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _api_response(payload: dict | list) -> dict:
    return {
        'data': payload,
        'status': 'ok',
        'cached': False,
        'timestamp': _now_iso(),
    }


def _base_price(symbol: str, idx: int = 0) -> float:
    fixed = {
        'NVDA': 924.50,
        'MSFT': 421.25,
        'TSLA': 183.70,
        'AAPL': 189.40,
        '005930': 74500.00,
        '005930.KS': 74500.00,
    }
    return fixed.get(symbol.upper(), 80.0 + (sum(ord(c) for c in symbol) % 160) + idx * 3.7)


def _stock_info(stock: Stock | None, ticker: str | None = None, idx: int = 0, theme_score: float | None = None) -> dict:
    symbol = (ticker or (stock.ticker if stock else 'AAPL')).upper().strip()
    name = stock.name if stock is not None else symbol
    sector = stock.sector if stock is not None and stock.sector else 'Unknown'
    price = round(_base_price(symbol, idx), 2)
    change_percent = round(((idx % 5) - 1) * 0.64 + 1.15, 2)
    change = round(price * change_percent / 100, 2)
    market_cap = int(max(price, 1) * (1_000_000_000 + idx * 125_000_000))
    ma50 = round(price * 0.97, 2)
    ma200 = round(price * 0.91, 2)

    return {
        'ticker': symbol,
        'name': name,
        'sector': sector,
        'industry': SECTOR_INDUSTRY.get(sector, sector or 'General'),
        'price': price,
        'change': change,
        'changePercent': change_percent,
        'marketCap': market_cap,
        'volume': 1_200_000 + idx * 345_000,
        'per': round(18.5 + idx * 2.1, 2),
        'peg': round(max(0.42, 0.82 + idx * 0.11), 2),
        'pbr': round(3.1 + idx * 0.35, 2),
        'roe': round(14.0 + idx * 2.4, 1),
        'revenueGrowth': round(0.12 + idx * 0.015, 3),
        'operatingMargin': round(0.21 + idx * 0.012, 3),
        'debtToEquity': round(28.0 + idx * 3.1, 1),
        'dividendYield': round(0.004 + idx * 0.001, 4),
        'eps': round(price / (18.5 + idx * 2.1), 2),
        'ma200': ma200,
        'ma50': ma50,
        'isAboveMa200': price > ma200,
        'isPennyStock': price < 1,
        'isBankruptcyRisk': symbol.endswith('.Q') or symbol.endswith('.E'),
        'isSmallCap': market_cap < 50_000_000,
        'riskScore': max(12, min(88, 26 + idx * 7)),
        'themeScore': int(theme_score if theme_score is not None else max(60, 95 - idx * 4)),
    }


def _get_or_fake_stock(db: Session, ticker: str) -> Stock | None:
    return db.scalar(select(Stock).where(Stock.ticker == ticker.upper().strip()))


def _chart_points(symbol: str, days: int = 120) -> list[dict]:
    base = _base_price(symbol)
    start = date.today() - timedelta(days=days)
    points: list[dict] = []
    for i in range(days):
        d = start + timedelta(days=i)
        if d.weekday() >= 5:
            continue
        trend = i * 0.12
        wave = sin(i / 6) * max(base * 0.012, 1.2)
        close = round(base * 0.88 + trend + wave, 2)
        points.append(
            {
                'date': d.isoformat(),
                'open': round(close * 0.996, 2),
                'high': round(close * 1.018, 2),
                'low': round(close * 0.982, 2),
                'close': close,
                'volume': 1_000_000 + i * 14_200,
                'ma50': round(close * 0.972, 2),
                'ma200': round(close * 0.925, 2),
            }
        )
    return points


def _financials(base: float) -> dict:
    periods = ['2025 Q1', '2025 Q2', '2025 Q3', '2025 Q4']
    return {
        'revenue': [
            {'period': p, 'value': round(base * 1_000_000_000 * (1 + i * 0.08)), 'yoyChange': round(0.08 + i * 0.02, 3)}
            for i, p in enumerate(periods)
        ],
        'operatingIncome': [
            {'period': p, 'value': round(base * 220_000_000 * (1 + i * 0.07)), 'yoyChange': round(0.07 + i * 0.018, 3)}
            for i, p in enumerate(periods)
        ],
        'netIncome': [
            {'period': p, 'value': round(base * 170_000_000 * (1 + i * 0.06)), 'yoyChange': round(0.06 + i * 0.015, 3)}
            for i, p in enumerate(periods)
        ],
        'eps': [
            {'period': p, 'value': round(2.1 + i * 0.18, 2), 'yoyChange': round(0.05 + i * 0.011, 3)}
            for i, p in enumerate(periods)
        ],
    }


@router.get('/market/banner')
def market_banner() -> dict:
    payload = {
        'indices': [
            {'symbol': 'S&P 500', 'name': 'S&P 500', 'price': 5432.10, 'change': 12.30, 'changePercent': 0.23},
            {'symbol': 'NASDAQ', 'name': 'NASDAQ 100', 'price': 17123.45, 'change': -45.20, 'changePercent': -0.26},
            {'symbol': 'DOW', 'name': 'Dow Jones', 'price': 39234.56, 'change': 89.10, 'changePercent': 0.23},
            {'symbol': 'VIX', 'name': 'VIX', 'price': 14.32, 'change': -0.54, 'changePercent': -3.63},
        ],
        'exchangeRates': [
            {'pair': 'USD/KRW', 'rate': 1342.50, 'change': -2.30},
            {'pair': 'USD/JPY', 'rate': 149.23, 'change': 0.12},
        ],
        'lastUpdated': _now_iso(),
    }
    return _api_response(payload)


@router.get('/market/calendar')
def market_calendar(days: int = Query(default=10, ge=1, le=60), db: Session = Depends(get_db)) -> dict:
    today = date.today()

    # Frontend contract:
    # data must be a list of {date, type, title, tickers, importance}.
    # type must be one of: earnings, economic, holiday, fomc.
    events: list[dict] = []

    rows = list(
        db.scalars(
            select(MarketCalendar)
            .where(MarketCalendar.date >= today)
            .order_by(MarketCalendar.date.asc())
            .limit(days)
        ).all()
    )

    for row in rows:
        note = (row.note or '').strip()
        # Ignore placeholder seed rows so the deployed UI does not look empty.
        if note.lower() == 'sample row':
            continue

        events.append(
            {
                'date': row.date.isoformat(),
                'type': 'economic' if row.is_open else 'holiday',
                'title': note or (f'{row.market} 정규장' if row.is_open else f'{row.market} 휴장'),
                'tickers': None,
                'importance': 'medium' if row.is_open else 'high',
            }
        )

    defaults = [
        ('earnings', 'NVDA 실적 발표', ['NVDA'], 'high'),
        ('economic', 'CPI 소비자물가 발표', None, 'high'),
        ('earnings', 'AAPL, MSFT 실적', ['AAPL', 'MSFT'], 'high'),
        ('fomc', 'FOMC 의사록 공개', None, 'high'),
        ('economic', '비농업 고용지수 발표', None, 'medium'),
        ('earnings', 'TSLA 실적 발표', ['TSLA'], 'medium'),
        ('economic', '소매판매 지표 발표', None, 'medium'),
        ('holiday', '미국 증시 휴장 예정일 확인', None, 'low'),
    ]

    # Always pad with upcoming events so the sidebar calendar has enough rows.
    i = 0
    used_dates = {event['date'] for event in events}
    while len(events) < days:
        event_type, title, tickers, importance = defaults[i % len(defaults)]
        event_date = today + timedelta(days=i + 1)
        date_str = event_date.isoformat()
        # Avoid duplicate dates when real DB rows already exist.
        if date_str not in used_dates:
            events.append(
                {
                    'date': date_str,
                    'type': event_type,
                    'title': title,
                    'tickers': tickers,
                    'importance': importance,
                }
            )
            used_dates.add(date_str)
        i += 1

    events.sort(key=lambda event: event['date'])
    return _api_response(events[:days])

@router.get('/theme/{theme_key}')
def theme(theme_key: str, db: Session = Depends(get_db)) -> dict:
    latest_created_at = db.scalar(
        select(ThemeSnapshot.created_at)
        .where(ThemeSnapshot.theme_key == theme_key)
        .order_by(ThemeSnapshot.created_at.desc())
        .limit(1)
    )

    stocks_payload: list[dict] = []
    if latest_created_at is not None:
        snapshots = list(
            db.scalars(
                select(ThemeSnapshot)
                .where(ThemeSnapshot.theme_key == theme_key, ThemeSnapshot.created_at == latest_created_at)
                .order_by(ThemeSnapshot.rank.asc().nullslast(), ThemeSnapshot.score.desc().nullslast())
                .limit(50)
            ).all()
        )
        for idx, snap in enumerate(snapshots):
            stock = _get_or_fake_stock(db, snap.ticker)
            item = _stock_info(stock, snap.ticker, idx, snap.score)
            item.update(
                {
                    'rank': snap.rank,
                    'reason': snap.reason,
                    'source': snap.source,
                }
            )
            stocks_payload.append(item)

    if not stocks_payload:
        stocks = list(db.scalars(select(Stock).order_by(Stock.ticker).limit(30)).all())
        stocks_payload = [_stock_info(stock, stock.ticker, idx) for idx, stock in enumerate(stocks)]

    if not stocks_payload:
        fallback = ['NVDA', 'MSFT', 'TSLA', 'AAPL']
        stocks_payload = [_stock_info(None, ticker, idx) for idx, ticker in enumerate(fallback)]

    payload = {
        'theme': theme_key,
        'stocks': stocks_payload,
        'totalCount': len(stocks_payload),
        'filteredCount': len(stocks_payload),
        'lastUpdated': _now_iso(),
    }
    return _api_response(payload)


@router.get('/stocks/{ticker}')
def stock_detail(ticker: str, period: str = Query(default='1y'), db: Session = Depends(get_db)) -> dict:
    symbol = ticker.upper().strip()
    stock = _get_or_fake_stock(db, symbol)
    info = _stock_info(stock, symbol)
    chart = _chart_points(symbol, 250 if period in {'1y', '2y'} else 120)
    if chart:
        last = chart[-1]
        prev = chart[-2] if len(chart) > 1 else last
        info['price'] = last['close']
        info['change'] = round(last['close'] - prev['close'], 2)
        info['changePercent'] = round((last['close'] - prev['close']) / prev['close'] * 100, 2) if prev['close'] else 0
        info['ma50'] = last.get('ma50')
        info['ma200'] = last.get('ma200')
        info['isAboveMa200'] = last['close'] > (last.get('ma200') or 0)

    payload = {
        **info,
        'description': f'{info["name"]} 샘플 상세 데이터입니다. Render FastAPI 호환 API에서 생성했습니다.',
        'website': f'https://finance.yahoo.com/quote/{symbol}',
        'employees': 10000,
        'founded': '2000',
        'chartData': chart,
        'financials': _financials(max(info['price'], 1)),
    }
    return _api_response(payload)


@router.get('/analysis/{ticker}/technical')
def technical_analysis(ticker: str, period: str = Query(default='1y')) -> dict:
    symbol = ticker.upper().strip()
    chart = _chart_points(symbol, 160 if period in {'1y', '2y'} else 90)
    points: list[dict] = []
    for i, row in enumerate(chart):
        close = row['close']
        ma20 = round(close * (0.985 + sin(i / 12) * 0.003), 2)
        ma60 = round(close * 0.955, 2)
        points.append(
            {
                'date': row['date'],
                'close': close,
                'volume': row['volume'],
                'ma5': round(close * 0.994, 2),
                'ma20': ma20,
                'ma60': ma60,
                'bb_upper': round(ma20 * 1.04, 2),
                'bb_lower': round(ma20 * 0.96, 2),
                'bb_mid': ma20,
                'rsi': round(52 + sin(i / 8) * 14, 2),
                'macd': round(sin(i / 10) * 2.1, 3),
                'macd_signal': round(sin(i / 11) * 1.7, 3),
                'macd_hist': round(sin(i / 10) * 0.4, 3),
            }
        )

    payload = {
        'ticker': symbol,
        'period': period,
        'data': points,
        'signal': {
            'overall': 'buy',
            'buy_count': 3,
            'sell_count': 1,
            'details': [
                {'signal': 'buy', 'description': '가격이 주요 이동평균선 위에 있습니다.'},
                {'signal': 'hold', 'description': 'RSI는 과열권과 침체권 사이에 있습니다.'},
                {'signal': 'buy', 'description': 'MACD 흐름이 개선되고 있습니다.'},
            ],
        },
        'lastUpdated': _now_iso(),
    }
    return _api_response(payload)


@router.get('/analysis/{ticker}/forecast')
def forecast_analysis(
    ticker: str,
    model: str = Query(default='both'),
    days: int = Query(default=7, ge=1, le=30),
) -> dict:
    symbol = ticker.upper().strip()
    last_price = round(_base_price(symbol), 2)
    today = date.today()

    prophet = []
    arima = []
    for i in range(1, days + 1):
        d = today + timedelta(days=i)
        yhat = round(last_price + i * 0.65 + sin(i / 2) * 1.25, 2)
        prophet.append(
            {
                'date': d.isoformat(),
                'yhat': yhat,
                'yhat_lower': round(yhat * 0.97, 2),
                'yhat_upper': round(yhat * 1.03, 2),
            }
        )
        arima.append(
            {
                'date': d.isoformat(),
                'yhat': round(last_price + i * 0.42 + sin(i / 3) * 0.95, 2),
                'yhat_lower': None,
                'yhat_upper': None,
            }
        )

    payload = {
        'lastPrice': last_price,
        'lastDate': today.isoformat(),
        'prophet': {'ticker': symbol, 'model': 'prophet', 'forecast': prophet},
        'arima': {'ticker': symbol, 'model': 'arima', 'forecast': arima},
    }
    return _api_response(payload)
