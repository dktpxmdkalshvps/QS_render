from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import RefreshRun
from app.schemas import RefreshRunCreate, RefreshRunOut

router = APIRouter(prefix='/api/refresh-runs', tags=['refresh-runs'])


@router.get('', response_model=list[RefreshRunOut])
def list_refresh_runs(
    job_name: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=300),
    db: Session = Depends(get_db),
) -> list[RefreshRun]:
    stmt = select(RefreshRun)
    if job_name:
        stmt = stmt.where(RefreshRun.job_name == job_name)
    stmt = stmt.order_by(RefreshRun.created_at.desc()).limit(limit)
    return list(db.scalars(stmt).all())


@router.post('', response_model=RefreshRunOut, status_code=201)
def create_refresh_run(payload: RefreshRunCreate, db: Session = Depends(get_db)) -> RefreshRun:
    row = RefreshRun(
        job_name=payload.job_name,
        status=payload.status,
        message=payload.message,
        started_at=payload.started_at,
        finished_at=payload.finished_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
