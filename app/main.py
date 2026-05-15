from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import calendar, compat, health, refresh_runs, stocks, themes

settings = get_settings()

app = FastAPI(
    title='Quant Backend API',
    description='Render-ready FastAPI backend for the quant portfolio project.',
    version='0.1.0',
)

allow_credentials = settings.cors_origin_list != ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=allow_credentials,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(health.router)
app.include_router(stocks.router)
app.include_router(themes.router)
app.include_router(calendar.router)
app.include_router(refresh_runs.router)
app.include_router(compat.router)


@app.get('/')
def root() -> dict[str, str]:
    return {
        'service': 'quant-backend',
        'status': 'ok',
        'docs': '/docs',
        'health': '/health',
    }
