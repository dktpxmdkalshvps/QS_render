# QuantScreen API Contract

프론트엔드(`QS_front`)가 기대하는 백엔드 API 계약입니다. 모든 프론트 호환 API는 동일한 응답 래퍼를 사용합니다.

## 공통 응답 래퍼

```ts
interface ApiResponse<T> {
  data: T;
  status: "ok" | "error";
  message?: string;
  cached: boolean;
  timestamp: string;
}
```

예시:

```json
{
  "data": [],
  "status": "ok",
  "cached": false,
  "timestamp": "2026-05-15T16:13:32.561556+00:00"
}
```

## GET /health

서비스와 DB 연결 상태 확인용입니다.

```json
{
  "ok": true,
  "service": "quant-backend",
  "database": "ok",
  "app_env": "production"
}
```

## GET /market/banner

상단 지수/환율 배너 데이터입니다.

```ts
interface MarketBannerData {
  indices: {
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
  }[];
  exchangeRates: {
    pair: string;
    rate: number;
    change: number;
  }[];
  lastUpdated: string;
}
```

## GET /market/calendar?days=10

우측 증시 캘린더 데이터입니다.

```ts
interface MarketCalendarEvent {
  date: string;
  type: "earnings" | "economic" | "holiday" | "fomc";
  title: string;
  tickers?: string[] | null;
  importance: "high" | "medium" | "low";
}
```

주의:

- `type`은 반드시 `earnings`, `economic`, `holiday`, `fomc` 중 하나여야 합니다.
- `importance`는 반드시 `high`, `medium`, `low` 중 하나여야 합니다.
- 프론트 UI가 충분히 채워지도록 `days` 값만큼 이벤트를 반환하는 것을 권장합니다.

## GET /theme/{theme_key}

테마별 종목 리스트입니다.

지원 theme key:

```text
undervalued_growth
growth_momentum
safe_growth
deep_value
high_roe
breakout
bugatti
dividend
dividend_aristocrat
```

```ts
interface ThemeResponse {
  theme: ThemeKey;
  stocks: StockInfo[];
  totalCount: number;
  filteredCount: number;
  lastUpdated: string;
}
```

```ts
interface StockInfo {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  price: number;
  change: number;
  changePercent: number;
  marketCap: number;
  volume: number;
  per?: number | null;
  peg?: number | null;
  pbr?: number | null;
  roe?: number | null;
  revenueGrowth?: number | null;
  operatingMargin?: number | null;
  debtToEquity?: number | null;
  dividendYield?: number | null;
  eps?: number | null;
  ma200?: number | null;
  ma50?: number | null;
  isAboveMa200?: boolean;
  isPennyStock?: boolean;
  isBankruptcyRisk?: boolean;
  isSmallCap?: boolean;
  riskScore: number;
  themeScore: number;
}
```

## GET /stocks/{ticker}?period=1y

종목 상세 모달용 데이터입니다.

추가 필드:

```ts
interface StockDetail extends StockInfo {
  description?: string;
  website?: string;
  employees?: number;
  founded?: string;
  chartData: ChartPoint[];
  financials: Financials;
}
```

## GET /analysis/{ticker}/technical?period=1y

기술적 분석 차트용 데이터입니다.

```ts
interface TechnicalAnalysis {
  ticker: string;
  period: string;
  data: IndicatorPoint[];
  signal: {
    overall: "buy" | "sell" | "hold";
    buy_count: number;
    sell_count: number;
    details: { signal: "buy" | "sell" | "hold"; description: string }[];
  };
  lastUpdated: string;
}
```

## GET /analysis/{ticker}/forecast?model=both&days=7

예측 차트용 데이터입니다.

```ts
interface ForecastData {
  lastPrice: number;
  lastDate: string;
  prophet?: ForecastModel;
  arima?: ForecastModel;
}
```

## Backend-only CRUD API

아래 API는 프론트 직접 호출보다는 관리/검증용입니다.

| Method | Path | 설명 |
|---|---|---|
| GET | `/api/stocks` | 종목 목록 |
| POST | `/api/stocks` | 종목 추가 |
| GET | `/api/themes/{theme_key}/snapshots` | 테마 스냅샷 목록 |
| GET | `/api/themes/{theme_key}/snapshots/latest` | 최신 스냅샷 |
| POST | `/api/themes/{theme_key}/snapshots` | 스냅샷 추가 |
| GET | `/api/market-calendar` | DB 캘린더 목록 |
| POST | `/api/market-calendar` | 캘린더 추가 |
| GET | `/api/refresh-runs` | 갱신 로그 목록 |
| POST | `/api/refresh-runs` | 갱신 로그 추가 |
