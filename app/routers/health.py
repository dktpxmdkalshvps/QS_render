from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.schemas import HealthOut

router = APIRouter(tags=['health'])


@router.get('/health', response_model=HealthOut)
def health_check(db: Session = Depends(get_db)) -> HealthOut:
    settings = get_settings()
    db.execute(text('SELECT 1'))
    return HealthOut(ok=True, service='quant-backend', database='ok', app_env=settings.app_env)
