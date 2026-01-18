"""add_rank_tracking

Revision ID: c812d6eb6b0c
Revises: fdfb0ddf8b32
Create Date: 2026-01-18 01:58:31.684850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c812d6eb6b0c'
down_revision: Union[str, None] = 'fdfb0ddf8b32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to riot_accounts
    op.add_column('riot_accounts', sa.Column('summoner_id', sa.String(), nullable=True))
    op.add_column('riot_accounts', sa.Column('wins', sa.Integer(), nullable=True))
    op.add_column('riot_accounts', sa.Column('losses', sa.Integer(), nullable=True))
    op.add_column('riot_accounts', sa.Column('peak_tier', sa.String(), nullable=True))
    op.add_column('riot_accounts', sa.Column('peak_division', sa.String(), nullable=True))
    op.add_column('riot_accounts', sa.Column('peak_lp', sa.Integer(), nullable=True))

    # Create rank_history table
    op.create_table(
        'rank_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('riot_account_id', sa.Integer(), nullable=False),
        sa.Column('tier', sa.String(), nullable=False),
        sa.Column('division', sa.String(), nullable=False),
        sa.Column('lp', sa.Integer(), nullable=False),
        sa.Column('wins', sa.Integer(), nullable=False),
        sa.Column('losses', sa.Integer(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['riot_account_id'], ['riot_accounts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rank_history_id'), 'rank_history', ['id'], unique=False)


def downgrade() -> None:
    # Drop rank_history table
    op.drop_index(op.f('ix_rank_history_id'), table_name='rank_history')
    op.drop_table('rank_history')

    # Remove columns from riot_accounts
    op.drop_column('riot_accounts', 'peak_lp')
    op.drop_column('riot_accounts', 'peak_division')
    op.drop_column('riot_accounts', 'peak_tier')
    op.drop_column('riot_accounts', 'losses')
    op.drop_column('riot_accounts', 'wins')
    op.drop_column('riot_accounts', 'summoner_id')
