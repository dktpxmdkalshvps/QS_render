from datetime import date
from sqlalchemy import select
from app.database import SessionLocal
from app.models import MarketCalendar, Stock, ThemeSnapshot

SAMPLE_STOCKS = [
    {'ticker': 'NVDA', 'name': 'NVIDIA Corporation', 'market': 'NASDAQ', 'sector': 'Semiconductors'},
    {'ticker': 'MSFT', 'name': 'Microsoft Corporation', 'market': 'NASDAQ', 'sector': 'Software'},
    {'ticker': 'TSLA', 'name': 'Tesla, Inc.', 'market': 'NASDAQ', 'sector': 'EV'},
    {'ticker': '005930', 'name': 'Samsung Electronics', 'market': 'KRX', 'sector': 'Semiconductors'},
]

SAMPLE_THEMES = [
    {
        'theme_key': 'ai_infra',
        'theme_name': 'AI Infrastructure',
        'ticker': 'NVDA',
        'score': 96.0,
        'rank': 1,
        'reason': 'GPU demand and data center exposure.',
        'source': 'seed',
        'payload': {'signal': 'sample'},
    },
    {
        'theme_key': 'ai_infra',
        'theme_name': 'AI Infrastructure',
        'ticker': 'MSFT',
        'score': 88.0,
        'rank': 2,
        'reason': 'Cloud and AI platform exposure.',
        'source': 'seed',
        'payload': {'signal': 'sample'},
    },
    {
        'theme_key': 'semiconductor',
        'theme_name': 'Semiconductor',
        'ticker': '005930',
        'score': 82.0,
        'rank': 1,
        'reason': 'Memory and foundry exposure.',
        'source': 'seed',
        'payload': {'signal': 'sample'},
    },
]


def main() -> None:
    db = SessionLocal()
    try:
        for item in SAMPLE_STOCKS:
            existing = db.scalar(select(Stock).where(Stock.ticker == item['ticker']))
            if existing is None:
                db.add(Stock(**item))
            else:
                existing.name = item['name']
                existing.market = item['market']
                existing.sector = item['sector']
        db.flush()

        has_snapshots = db.scalar(select(ThemeSnapshot.id).limit(1))
        if has_snapshots is None:
            for item in SAMPLE_THEMES:
                db.add(ThemeSnapshot(**item))

        today = date.today()
        existing_calendar = db.scalar(
            select(MarketCalendar).where(MarketCalendar.market == 'KRX', MarketCalendar.date == today)
        )
        if existing_calendar is None:
            db.add(MarketCalendar(market='KRX', date=today, is_open=True, note='sample row'))

        db.commit()
        print('Seed completed.')
    finally:
        db.close()


if __name__ == '__main__':
    main()
