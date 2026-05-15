"""initial schema

Revision ID: 202605150001
Revises:
Create Date: 2026-05-15 00:01:00
"""
from alembic import op
import sqlalchemy as sa

revision = '202605150001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'stocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=32), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('market', sa.String(length=32), nullable=True),
        sa.Column('sector', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticker'),
    )
    op.create_index(op.f('ix_stocks_id'), 'stocks', ['id'], unique=False)
    op.create_index(op.f('ix_stocks_ticker'), 'stocks', ['ticker'], unique=False)
    op.create_index(op.f('ix_stocks_market'), 'stocks', ['market'], unique=False)
    op.create_index(op.f('ix_stocks_sector'), 'stocks', ['sector'], unique=False)

    op.create_table(
        'theme_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('theme_key', sa.String(length=128), nullable=False),
        sa.Column('theme_name', sa.String(length=255), nullable=False),
        sa.Column('ticker', sa.String(length=32), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=128), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['ticker'], ['stocks.ticker']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_theme_snapshots_id'), 'theme_snapshots', ['id'], unique=False)
    op.create_index(op.f('ix_theme_snapshots_theme_key'), 'theme_snapshots', ['theme_key'], unique=False)
    op.create_index(op.f('ix_theme_snapshots_ticker'), 'theme_snapshots', ['ticker'], unique=False)
    op.create_index(op.f('ix_theme_snapshots_created_at'), 'theme_snapshots', ['created_at'], unique=False)
    op.create_index('ix_theme_snapshots_theme_created', 'theme_snapshots', ['theme_key', 'created_at'], unique=False)
    op.create_index('ix_theme_snapshots_ticker_created', 'theme_snapshots', ['ticker', 'created_at'], unique=False)

    op.create_table(
        'market_calendar',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('market', sa.String(length=32), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('is_open', sa.Boolean(), nullable=False),
        sa.Column('note', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('market', 'date', name='uq_market_calendar_market_date'),
    )
    op.create_index(op.f('ix_market_calendar_id'), 'market_calendar', ['id'], unique=False)
    op.create_index(op.f('ix_market_calendar_market'), 'market_calendar', ['market'], unique=False)
    op.create_index(op.f('ix_market_calendar_date'), 'market_calendar', ['date'], unique=False)
    op.create_index('ix_market_calendar_market_date', 'market_calendar', ['market', 'date'], unique=False)

    op.create_table(
        'refresh_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_name', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_refresh_runs_id'), 'refresh_runs', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_runs_job_name'), 'refresh_runs', ['job_name'], unique=False)
    op.create_index(op.f('ix_refresh_runs_status'), 'refresh_runs', ['status'], unique=False)
    op.create_index(op.f('ix_refresh_runs_created_at'), 'refresh_runs', ['created_at'], unique=False)
    op.create_index('ix_refresh_runs_job_created', 'refresh_runs', ['job_name', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_refresh_runs_job_created', table_name='refresh_runs')
    op.drop_index(op.f('ix_refresh_runs_created_at'), table_name='refresh_runs')
    op.drop_index(op.f('ix_refresh_runs_status'), table_name='refresh_runs')
    op.drop_index(op.f('ix_refresh_runs_job_name'), table_name='refresh_runs')
    op.drop_index(op.f('ix_refresh_runs_id'), table_name='refresh_runs')
    op.drop_table('refresh_runs')

    op.drop_index('ix_market_calendar_market_date', table_name='market_calendar')
    op.drop_index(op.f('ix_market_calendar_date'), table_name='market_calendar')
    op.drop_index(op.f('ix_market_calendar_market'), table_name='market_calendar')
    op.drop_index(op.f('ix_market_calendar_id'), table_name='market_calendar')
    op.drop_table('market_calendar')

    op.drop_index('ix_theme_snapshots_ticker_created', table_name='theme_snapshots')
    op.drop_index('ix_theme_snapshots_theme_created', table_name='theme_snapshots')
    op.drop_index(op.f('ix_theme_snapshots_created_at'), table_name='theme_snapshots')
    op.drop_index(op.f('ix_theme_snapshots_ticker'), table_name='theme_snapshots')
    op.drop_index(op.f('ix_theme_snapshots_theme_key'), table_name='theme_snapshots')
    op.drop_index(op.f('ix_theme_snapshots_id'), table_name='theme_snapshots')
    op.drop_table('theme_snapshots')

    op.drop_index(op.f('ix_stocks_sector'), table_name='stocks')
    op.drop_index(op.f('ix_stocks_market'), table_name='stocks')
    op.drop_index(op.f('ix_stocks_ticker'), table_name='stocks')
    op.drop_index(op.f('ix_stocks_id'), table_name='stocks')
    op.drop_table('stocks')
