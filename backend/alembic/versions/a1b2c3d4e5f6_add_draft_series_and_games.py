"""add draft series and games tables

Revision ID: a1b2c3d4e5f6
Revises: 9f7baf8744a8
Create Date: 2026-01-18 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '9f7baf8744a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create draft_series table
    op.create_table(
        'draft_series',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('opponent_name', sa.String(), nullable=False),
        sa.Column('format', sa.String(), nullable=False, server_default='bo1'),
        sa.Column('our_score', sa.Integer(), server_default='0'),
        sa.Column('opponent_score', sa.Integer(), server_default='0'),
        sa.Column('result', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_draft_series_id'), 'draft_series', ['id'], unique=False)

    # Create draft_games table
    op.create_table(
        'draft_games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('series_id', sa.Integer(), nullable=False),
        sa.Column('game_number', sa.Integer(), nullable=False),
        sa.Column('blue_side', sa.Boolean(), nullable=False),
        sa.Column('our_bans', sa.JSON(), nullable=False),
        sa.Column('opponent_bans', sa.JSON(), nullable=False),
        sa.Column('our_picks', sa.JSON(), nullable=False),
        sa.Column('opponent_picks', sa.JSON(), nullable=False),
        sa.Column('pick_order', sa.JSON(), nullable=True),
        sa.Column('result', sa.String(), nullable=True),
        sa.Column('import_source', sa.String(), nullable=True),
        sa.Column('import_url', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['series_id'], ['draft_series.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_draft_games_id'), 'draft_games', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_draft_games_id'), table_name='draft_games')
    op.drop_table('draft_games')
    op.drop_index(op.f('ix_draft_series_id'), table_name='draft_series')
    op.drop_table('draft_series')
