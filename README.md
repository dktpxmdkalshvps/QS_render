# QuantScreen Backend

FastAPI + PostgreSQL 기반의 포트폴리오용 퀀트 스크리닝 백엔드입니다. Vercel에 배포된 Next.js 프론트와 연결되도록 Render Web Service + Render PostgreSQL 환경에 맞춰 구성했습니다.

## 배포 URL

| 구분 | URL |
|---|---|
| Frontend | `https://qsscreen.vercel.app` |
| Vercel preview/origin | `https://qs-front-psi.vercel.app` |
| Backend | `https://quant-backend-e82y.onrender.com` |
| Health Check | `https://quant-backend-e82y.onrender.com/health` |
| Swagger UI | `https://quant-backend-e82y.onrender.com/docs` |

> Render Free Web Service는 유휴 상태 이후 첫 요청이 느릴 수 있습니다.

## 기술 스택

| 영역 | 기술 |
|---|---|
| API | FastAPI |
| ORM | SQLAlchemy 2.x |
| Migration | Alembic |
| DB | PostgreSQL on Render |
| Server | Gunicorn + Uvicorn Worker |
| 배포 | Render Blueprint |
| Frontend 연동 | Next.js on Vercel |

## 아키텍처

```text
User Browser
  ↓
Vercel Next.js Frontend
  ↓ HTTPS / CORS
Render FastAPI Backend
  ↓ SQLAlchemy
Render PostgreSQL
```

## 주요 기능

- 테마별 종목 스크리닝 API
- 종목 상세 / 차트 / 재무 샘플 API
- 기술적 분석 샘플 API
- 예측 모델 샘플 API
- 증시 캘린더 API
- 지수/환율 배너 API
- PostgreSQL health check
- Alembic 기반 스키마 관리
- Render Blueprint 배포 설정

## 프로젝트 구조

```text
.
├── app/
│   ├── main.py                 # FastAPI 앱 엔트리포인트
│   ├── config.py               # 환경변수 설정
│   ├── database.py             # SQLAlchemy 엔진/세션
│   ├── models.py               # DB 모델
│   ├── schemas.py              # Pydantic 스키마
│   └── routers/
│       ├── health.py           # /health
│       ├── stocks.py           # /api/stocks
│       ├── themes.py           # /api/themes/...
│       ├── calendar.py         # /api/market-calendar
│       ├── refresh_runs.py     # /api/refresh-runs
│       └── compat.py           # 프론트 호환 API
├── alembic/
│   └── versions/               # 마이그레이션 파일
├── scripts/
│   └── seed.py                 # 포트폴리오 샘플 데이터 적재
├── render.yaml                 # Render Blueprint
├── build.sh                    # Render build command
├── start.sh                    # Alembic 적용 후 서버 시작
├── requirements.txt
├── runtime.txt
└── .python-version
```

## 환경변수

| Key | 예시 | 설명 |
|---|---|---|
| `APP_ENV` | `production` | 실행 환경 |
| `DATABASE_URL` | `postgresql://...` | PostgreSQL 연결 URL |
| `CORS_ORIGINS` | `https://qs-front-psi.vercel.app,https://qsscreen.vercel.app` | 허용할 프론트 origin 목록 |
| `WEB_CONCURRENCY` | `2` | Gunicorn worker 수 |
| `PYTHON_VERSION` | `3.12.7` | Render Python 버전 고정 |

## 로컬 실행

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. alembic upgrade head
PYTHONPATH=. python scripts/seed.py
uvicorn app.main:app --reload
```

확인 URL:

```text
http://localhost:8000/health
http://localhost:8000/docs
http://localhost:8000/theme/undervalued_growth
http://localhost:8000/market/calendar?days=10
```

## Render 배포

### Blueprint 배포

1. 이 폴더의 파일들을 GitHub repo 루트에 배치합니다.
2. Render에서 **New > Blueprint**를 선택합니다.
3. GitHub repo를 연결합니다.
4. Blueprint path는 `render.yaml`로 둡니다.
5. 배포 후 `/health`로 DB 연결 상태를 확인합니다.

### 중요한 Render 설정

- Build Command: `bash build.sh`
- Start Command: `bash start.sh`
- Python: `3.12.7`
- `DATABASE_URL`: Blueprint에서 PostgreSQL connection string 자동 연결
- `CORS_ORIGINS`: 실제 Vercel URL을 반드시 포함

## 샘플 데이터 적재

Render Free Web Service는 Shell Access가 없으므로, Codespaces나 로컬에서 Render PostgreSQL의 **External Database URL**로 실행합니다.

```bash
export DATABASE_URL='postgresql://USER:PASSWORD@HOST:PORT/DATABASE'
export APP_ENV=local
PYTHONPATH=. alembic upgrade head
PYTHONPATH=. python scripts/seed.py
```

`seed.py`는 다음 데이터를 넣습니다.

- 주요 미국/한국 종목 15개
- 프론트 테마 9개에 대한 테마 스냅샷
- 증시 캘린더 기본 이벤트
- refresh run 성공 로그

## 프론트 호환 API

프론트 `lib/api.ts`는 공통 응답 래퍼를 기대합니다.

```json
{
  "data": {},
  "status": "ok",
  "cached": false,
  "timestamp": "2026-05-15T00:00:00+00:00"
}
```

프론트에서 사용하는 주요 API는 아래와 같습니다.

| Method | Path | 설명 |
|---|---|---|
| GET | `/health` | 서비스/DB 상태 확인 |
| GET | `/api/stocks` | DB 종목 목록 |
| GET | `/market/banner` | 상단 지수/환율 배너 |
| GET | `/market/calendar?days=10` | 증시 캘린더 |
| GET | `/theme/{theme_key}` | 테마별 종목 리스트 |
| GET | `/stocks/{ticker}?period=1y` | 종목 상세/차트/재무 샘플 |
| GET | `/analysis/{ticker}/technical?period=1y` | 기술적 분석 샘플 |
| GET | `/analysis/{ticker}/forecast?model=both&days=7` | 예측 샘플 |
| GET | `/api/refresh-runs` | 데이터 갱신 실행 로그 |

자세한 응답 계약은 [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md)를 참고하세요.

## DB 설계 요약

| 테이블 | 역할 |
|---|---|
| `stocks` | 종목 마스터 |
| `theme_snapshots` | 테마별 종목 점수/랭킹 스냅샷 |
| `market_calendar` | 증시 일정/휴장/경제 이벤트 |
| `refresh_runs` | 데이터 갱신 작업 로그 |

## 트러블슈팅 기록

| 이슈 | 원인 | 해결 |
|---|---|---|
| Free DB 생성 실패 | Render Free PostgreSQL은 active free DB 제한이 있음 | 기존 DB 삭제 후 Blueprint 재배포 또는 기존 DB 수동 연결 |
| `psycopg-binary==3.2.3` 설치 실패 | Render 빌드 환경에서 해당 버전 wheel 미지원 | `psycopg[binary]==3.3.4`로 변경 |
| SQLAlchemy 타입 힌트 오류 | Render가 Python 3.14로 빌드 | `.python-version`, `runtime.txt`, `PYTHON_VERSION=3.12.7` 고정 |
| `Permission denied` 가능성 | shell script 실행 권한 누락 | `bash build.sh`, `bash start.sh` 사용 |
| API 404 | 프론트가 `/theme/...`, `/market/...` 경로를 호출 | `app/routers/compat.py`에 호환 API 추가 |
| 화면 데이터 오류 | 프론트가 `{ data, status, cached, timestamp }` 응답 래퍼 기대 | 모든 호환 API 응답 포맷 통일 |
| CORS 차단 | 실제 Vercel origin 누락 | `CORS_ORIGINS`에 `qs-front-psi.vercel.app`, `qsscreen.vercel.app` 추가 |

## 운영/QA 체크리스트

배포 후 아래 주소를 확인합니다.

```text
/health
/api/stocks
/market/banner
/market/calendar?days=10
/theme/undervalued_growth
/stocks/NVDA?period=1y
/analysis/NVDA/technical?period=1y
/analysis/NVDA/forecast?model=both&days=7
```

상세 체크리스트는 [`docs/QA_CHECKLIST.md`](docs/QA_CHECKLIST.md)를 참고하세요.

## 향후 개선 방향

- 실제 시장 데이터 수집 배치 추가
- `theme_snapshots` 자동 갱신 파이프라인 구축
- yfinance 또는 외부 API 기반 가격 데이터 저장
- Refresh job을 Render Cron Job 또는 GitHub Actions로 분리
- API 테스트 자동화
- 예측 모델 결과 저장 테이블 추가
- 종목 상세/차트 데이터의 DB 영속화
