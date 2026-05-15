from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class StockBase(BaseModel):
    ticker: str = Field(..., examples=['AAPL'])
    name: str = Field(..., examples=['Apple Inc.'])
    market: str | None = Field(default=None, examples=['NASDAQ'])
    sector: str | None = Field(default=None, examples=['Technology'])


class StockCreate(StockBase):
    pass


class StockOut(StockBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ThemeSnapshotBase(BaseModel):
    theme_key: str = Field(..., examples=['ai_infra'])
    theme_name: str = Field(..., examples=['AI Infrastructure'])
    ticker: str = Field(..., examples=['NVDA'])
    score: float | None = Field(default=None, ge=0, le=100)
    rank: int | None = Field(default=None, ge=1)
    reason: str | None = None
    source: str | None = None
    payload: dict[str, Any] | None = None


class ThemeSnapshotCreate(ThemeSnapshotBase):
    pass


class ThemeSnapshotOut(ThemeSnapshotBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class MarketCalendarBase(BaseModel):
    market: str = Field(..., examples=['KRX'])
    date: date
    is_open: bool = True
    note: str | None = None


class MarketCalendarCreate(MarketCalendarBase):
    pass


class MarketCalendarOut(MarketCalendarBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class RefreshRunBase(BaseModel):
    job_name: str = Field(..., examples=['theme-refresh'])
    status: str = Field(..., examples=['success'])
    message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class RefreshRunCreate(RefreshRunBase):
    pass


class RefreshRunOut(RefreshRunBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class HealthOut(BaseModel):
    ok: bool
    service: str
    database: str
    app_env: str
