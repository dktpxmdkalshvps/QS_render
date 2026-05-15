from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Stock(Base):
    __tablename__ = 'stocks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    ticker: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    market: Mapped[str | None] = mapped_column(String(32), index=True)
    sector: Mapped[str | None] = mapped_column(String(128), index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    snapshots: Mapped[list['ThemeSnapshot']] = relationship(back_populates='stock')


class ThemeSnapshot(Base):
    __tablename__ = 'theme_snapshots'
    __table_args__ = (
        Index('ix_theme_snapshots_theme_created', 'theme_key', 'created_at'),
        Index('ix_theme_snapshots_ticker_created', 'ticker', 'created_at'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    theme_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    theme_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ticker: Mapped[str] = mapped_column(String(32), ForeignKey('stocks.ticker'), index=True, nullable=False)
    score: Mapped[float | None] = mapped_column(Float)
    rank: Mapped[int | None] = mapped_column(Integer)
    reason: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(128))
    payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)

    stock: Mapped[Stock] = relationship(back_populates='snapshots')


class MarketCalendar(Base):
    __tablename__ = 'market_calendar'
    __table_args__ = (
        UniqueConstraint('market', 'date', name='uq_market_calendar_market_date'),
        Index('ix_market_calendar_market_date', 'market', 'date'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    market: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    date: Mapped[Date] = mapped_column(Date, index=True, nullable=False)
    is_open: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    note: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RefreshRun(Base):
    __tablename__ = 'refresh_runs'
    __table_args__ = (Index('ix_refresh_runs_job_created', 'job_name', 'created_at'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)
