from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select

from app.database import SessionLocal
from app.models import MarketCalendar, RefreshRun, Stock, ThemeSnapshot

SAMPLE_STOCKS = [
    {'ticker': 'NVDA', 'name': 'NVIDIA Corporation', 'market': 'NASDAQ', 'sector': 'Semiconductors'},
    {'ticker': 'MSFT', 'name': 'Microsoft Corporation', 'market': 'NASDAQ', 'sector': 'Software'},
    {'ticker': 'AAPL', 'name': 'Apple Inc.', 'market': 'NASDAQ', 'sector': 'Consumer Electronics'},
    {'ticker': 'TSLA', 'name': 'Tesla, Inc.', 'market': 'NASDAQ', 'sector': 'EV'},
    {'ticker': 'GOOGL', 'name': 'Alphabet Inc.', 'market': 'NASDAQ', 'sector': 'Internet Services'},
    {'ticker': 'AMZN', 'name': 'Amazon.com, Inc.', 'market': 'NASDAQ', 'sector': 'E-Commerce'},
    {'ticker': 'META', 'name': 'Meta Platforms, Inc.', 'market': 'NASDAQ', 'sector': 'Internet Services'},
    {'ticker': 'AMD', 'name': 'Advanced Micro Devices, Inc.', 'market': 'NASDAQ', 'sector': 'Semiconductors'},
    {'ticker': 'AVGO', 'name': 'Broadcom Inc.', 'market': 'NASDAQ', 'sector': 'Semiconductors'},
    {'ticker': 'JPM', 'name': 'JPMorgan Chase & Co.', 'market': 'NYSE', 'sector': 'Financials'},
    {'ticker': 'JNJ', 'name': 'Johnson & Johnson', 'market': 'NYSE', 'sector': 'Healthcare'},
    {'ticker': 'KO', 'name': 'The Coca-Cola Company', 'market': 'NYSE', 'sector': 'Consumer Staples'},
    {'ticker': 'PG', 'name': 'Procter & Gamble Co.', 'market': 'NYSE', 'sector': 'Consumer Staples'},
    {'ticker': '005930', 'name': 'Samsung Electronics', 'market': 'KRX', 'sector': 'Semiconductors'},
    {'ticker': '000660', 'name': 'SK hynix Inc.', 'market': 'KRX', 'sector': 'Semiconductors'},
]

THEME_STOCKS = {
    'undervalued_growth': [
        ('005930', 95, 1, 'PEG와 밸류에이션 부담이 낮고 반도체 회복 수혜가 기대됩니다.'),
        ('MSFT', 91, 2, '클라우드와 AI 매출 성장률 대비 밸류에이션 안정성이 좋습니다.'),
        ('NVDA', 87, 3, '고성장 프리미엄이 있으나 AI 인프라 수요가 강합니다.'),
        ('GOOGL', 84, 4, '광고와 클라우드 현금흐름 대비 상대 저평가 매력이 있습니다.'),
        ('AMD', 81, 5, 'AI 가속기 성장 기대와 낮아진 기대치가 공존합니다.'),
    ],
    'growth_momentum': [
        ('NVDA', 98, 1, 'AI 데이터센터 모멘텀이 가장 강합니다.'),
        ('AVGO', 93, 2, '반도체와 인프라 소프트웨어 모멘텀이 견조합니다.'),
        ('MSFT', 90, 3, 'AI 플랫폼 전환과 클라우드 성장세가 이어지고 있습니다.'),
        ('META', 86, 4, '광고 효율 개선과 AI 투자 레버리지가 기대됩니다.'),
        ('AMZN', 83, 5, 'AWS와 커머스 수익성 개선 모멘텀이 있습니다.'),
    ],
    'safe_growth': [
        ('MSFT', 96, 1, '높은 현금흐름과 성장성을 동시에 보유합니다.'),
        ('AAPL', 90, 2, '생태계 락인과 서비스 매출 안정성이 강점입니다.'),
        ('JNJ', 85, 3, '방어적 헬스케어 포트폴리오가 변동성을 낮춥니다.'),
        ('PG', 82, 4, '필수소비재 기반의 안정적 실적이 강점입니다.'),
        ('KO', 79, 5, '브랜드 파워와 배당 안정성이 높습니다.'),
    ],
    'deep_value': [
        ('005930', 92, 1, '메모리 사이클 저점 이후 회복 구간에 있습니다.'),
        ('JPM', 86, 2, '대형 금융주 중 수익성과 자본력이 우수합니다.'),
        ('GOOGL', 83, 3, '광고 현금흐름 대비 멀티플 부담이 제한적입니다.'),
        ('AMZN', 79, 4, '커머스 마진 개선 여지가 큽니다.'),
        ('000660', 76, 5, 'HBM 기대감과 메모리 업황 회복을 반영합니다.'),
    ],
    'high_roe': [
        ('NVDA', 97, 1, '고마진 AI 칩 수요로 높은 ROE가 유지됩니다.'),
        ('MSFT', 94, 2, '소프트웨어 구독 모델의 자본 효율이 높습니다.'),
        ('AAPL', 91, 3, '자사주 매입과 서비스 매출이 ROE를 지지합니다.'),
        ('META', 86, 4, '광고 플랫폼의 영업 레버리지가 높습니다.'),
        ('AVGO', 84, 5, '고마진 반도체 포트폴리오를 보유합니다.'),
    ],
    'breakout': [
        ('NVDA', 96, 1, '주요 이동평균 상향 돌파 흐름입니다.'),
        ('AMD', 89, 2, 'AI 가속기 기대감으로 기술적 반등이 강합니다.'),
        ('000660', 85, 3, 'HBM 관련 수급 모멘텀이 있습니다.'),
        ('TSLA', 78, 4, '변동성은 크지만 단기 추세 반등 구간입니다.'),
        ('AMZN', 76, 5, '박스권 상단 돌파 가능성이 있습니다.'),
    ],
    'bugatti': [
        ('NVDA', 99, 1, '성장성, 수익성, 모멘텀 점수가 모두 상위권입니다.'),
        ('MSFT', 94, 2, '안정성과 성장성이 균형 잡힌 핵심 종목입니다.'),
        ('AVGO', 90, 3, 'AI 인프라와 현금흐름이 동시에 우수합니다.'),
        ('AAPL', 86, 4, '브랜드와 현금창출력이 강합니다.'),
        ('GOOGL', 84, 5, '검색, 광고, 클라우드 포트폴리오가 견조합니다.'),
    ],
    'dividend': [
        ('KO', 92, 1, '방어적 현금흐름과 배당 안정성이 높습니다.'),
        ('PG', 90, 2, '필수소비재 기반 배당 지속성이 우수합니다.'),
        ('JNJ', 87, 3, '헬스케어 방어성과 배당 매력이 있습니다.'),
        ('JPM', 80, 4, '대형 금융주 중 배당 여력이 양호합니다.'),
        ('005930', 74, 5, '주주환원 확대 가능성을 반영합니다.'),
    ],
    'dividend_aristocrat': [
        ('KO', 95, 1, '장기 배당 성장 이력이 강한 대표 배당주입니다.'),
        ('PG', 93, 2, '경기 방어성과 장기 배당 성장성이 높습니다.'),
        ('JNJ', 88, 3, '헬스케어 기반의 장기 배당 안정성이 있습니다.'),
        ('AAPL', 76, 4, '배당률은 낮지만 주주환원 규모가 큽니다.'),
        ('MSFT', 73, 5, '성장주이면서 꾸준한 배당 확대 여력이 있습니다.'),
    ],
}

THEME_NAMES = {
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

CALENDAR_DEFAULTS = [
    ('US', 1, True, 'NVDA 실적 발표'),
    ('US', 2, True, 'CPI 소비자물가 발표'),
    ('US', 3, True, 'AAPL, MSFT 실적'),
    ('US', 5, True, 'FOMC 의사록 공개'),
    ('US', 7, True, '비농업 고용지수 발표'),
    ('KRX', 8, True, '한국 수출입 동향 발표'),
    ('US', 9, True, 'TSLA 실적 발표'),
    ('US', 10, True, '소매판매 지표 발표'),
]


def upsert_stock(db, item: dict) -> None:
    existing = db.scalar(select(Stock).where(Stock.ticker == item['ticker']))
    if existing is None:
        db.add(Stock(**item))
    else:
        existing.name = item['name']
        existing.market = item['market']
        existing.sector = item['sector']


def seed_theme_snapshots(db) -> int:
    inserted = 0
    for theme_key, rows in THEME_STOCKS.items():
        has_theme = db.scalar(select(ThemeSnapshot.id).where(ThemeSnapshot.theme_key == theme_key).limit(1))
        if has_theme is not None:
            continue
        for ticker, score, rank, reason in rows:
            db.add(
                ThemeSnapshot(
                    theme_key=theme_key,
                    theme_name=THEME_NAMES[theme_key],
                    ticker=ticker,
                    score=float(score),
                    rank=rank,
                    reason=reason,
                    source='portfolio_seed',
                    payload={'signal': 'sample', 'seed_version': 'portfolio-v1'},
                )
            )
            inserted += 1
    return inserted


def seed_calendar(db) -> int:
    inserted = 0
    today = date.today()
    for market, day_offset, is_open, note in CALENDAR_DEFAULTS:
        event_date = today + timedelta(days=day_offset)
        existing = db.scalar(select(MarketCalendar).where(MarketCalendar.market == market, MarketCalendar.date == event_date))
        if existing is None:
            db.add(MarketCalendar(market=market, date=event_date, is_open=is_open, note=note))
            inserted += 1
        elif (existing.note or '').strip().lower() == 'sample row':
            existing.note = note
            existing.is_open = is_open
            inserted += 1
    return inserted


def seed_refresh_run(db) -> None:
    now = datetime.now(timezone.utc)
    db.add(
        RefreshRun(
            job_name='portfolio_seed',
            status='success',
            message='Inserted or refreshed portfolio sample data.',
            started_at=now,
            finished_at=now,
        )
    )


def main() -> None:
    db = SessionLocal()
    try:
        for item in SAMPLE_STOCKS:
            upsert_stock(db, item)
        db.flush()

        theme_count = seed_theme_snapshots(db)
        calendar_count = seed_calendar(db)
        seed_refresh_run(db)

        db.commit()
        print(f'Seed completed. stocks={len(SAMPLE_STOCKS)}, new_theme_snapshots={theme_count}, calendar_changes={calendar_count}')
    finally:
        db.close()


if __name__ == '__main__':
    main()
