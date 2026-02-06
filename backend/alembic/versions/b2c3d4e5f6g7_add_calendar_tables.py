"""add calendar events and player availabilities tables

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create player_availabilities table
    op.create_table(
        'player_availabilities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('slot', sa.String(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('note', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_player_availabilities_id'), 'player_availabilities', ['id'], unique=False)
    op.create_index('ix_player_availabilities_date', 'player_availabilities', ['date'], unique=False)
    op.create_index(
        'ix_player_availabilities_player_date',
        'player_availabilities',
        ['player_id', 'date'],
        unique=False
    )

    # Create calendar_events table
    op.create_table(
        'calendar_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('slot', sa.String(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=True),
        sa.Column('end_time', sa.Time(), nullable=True),
        sa.Column('draft_series_id', sa.Integer(), nullable=True),
        sa.Column('opponent_name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['draft_series_id'], ['draft_series.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_calendar_events_id'), 'calendar_events', ['id'], unique=False)
    op.create_index('ix_calendar_events_date', 'calendar_events', ['date'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_calendar_events_date', table_name='calendar_events')
    op.drop_index(op.f('ix_calendar_events_id'), table_name='calendar_events')
    op.drop_table('calendar_events')

    op.drop_index('ix_player_availabilities_player_date', table_name='player_availabilities')
    op.drop_index('ix_player_availabilities_date', table_name='player_availabilities')
    op.drop_index(op.f('ix_player_availabilities_id'), table_name='player_availabilities')
    op.drop_table('player_availabilities')
