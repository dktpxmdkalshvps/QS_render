# QuantScreen QA Checklist

## 1. Backend smoke test

배포 후 브라우저 또는 curl로 확인합니다.

```bash
curl https://quant-backend-e82y.onrender.com/health
curl https://quant-backend-e82y.onrender.com/api/stocks
curl https://quant-backend-e82y.onrender.com/market/banner
curl 'https://quant-backend-e82y.onrender.com/market/calendar?days=10'
curl https://quant-backend-e82y.onrender.com/theme/undervalued_growth
curl 'https://quant-backend-e82y.onrender.com/stocks/NVDA?period=1y'
curl 'https://quant-backend-e82y.onrender.com/analysis/NVDA/technical?period=1y'
curl 'https://quant-backend-e82y.onrender.com/analysis/NVDA/forecast?model=both&days=7'
```

기대 결과:

- `/health`의 `database`가 `ok`
- `/api/stocks`가 빈 배열이 아님
- `/theme/undervalued_growth`가 `{ data: { stocks: [...] } }` 형태
- `/market/calendar?days=10`의 `data` 배열이 5개 이상
- API 요청이 404가 아닌 200

## 2. CORS check

프론트 도메인에서 개발자도구 Console을 확인합니다.

허용해야 하는 origin:

```text
https://qs-front-psi.vercel.app
https://qsscreen.vercel.app
http://localhost:3000
http://localhost:5173
```

CORS 오류 예시:

```text
No 'Access-Control-Allow-Origin' header is present
net::ERR_FAILED 200 (OK)
```

위 오류가 보이면 Render 환경변수 `CORS_ORIGINS`를 수정하고 백엔드를 재배포합니다.

## 3. Frontend functional QA

- 메인 대시보드 접속 시 상단 지수/환율 배너 표시
- 테마 탭 클릭 시 종목 리스트 갱신
- `저평가 성장`, `모멘텀`, `안전 성장`, `딥 밸류`, `고 ROE`, `브레이크아웃`, `배당`, `배당귀족` 탭 확인
- 종목 테이블에 ticker, name, price, changePercent, marketCap, PER, PEG, ROE 표시
- 검색창에서 `NVDA`, `AAPL`, `005930` 검색 후 상세 모달 표시
- 상세 모달에서 가격 차트/기술 분석/예측 차트 표시
- 우측 증시 캘린더에 일정 5개 이상 표시
- 모바일 화면에서 헤더, 테마 탭, 테이블, 캘린더가 깨지지 않는지 확인

## 4. Deployment QA

- Render latest deploy가 success인지 확인
- Vercel latest deployment가 production으로 alias 되었는지 확인
- Vercel 환경변수 `NEXT_PUBLIC_API_BASE_URL`이 Render URL인지 확인
- Render 환경변수 `PYTHON_VERSION=3.12.7` 유지
- Render deploy log에서 `.venv/lib/python3.12` 사용 확인

## 5. Portfolio review checklist

- GitHub README에 프론트/백엔드 URL 포함
- API 명세 포함
- 아키텍처 다이어그램 또는 텍스트 구조 포함
- ERD 또는 DB 설계 요약 포함
- 트러블슈팅 기록 포함
- 스크린샷 2~3장 추가
- `.env` 미커밋 확인
- `.env.example` 최신화 확인
