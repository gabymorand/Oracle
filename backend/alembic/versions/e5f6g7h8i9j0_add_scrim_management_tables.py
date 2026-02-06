"""Add scrim management tables

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2026-02-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6g7h8i9j0'
down_revision: Union[str, None] = 'd4e5f6g7h8i9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create opponent_teams table
    op.create_table(
        'opponent_teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('contact_name', sa.String(), nullable=True),
        sa.Column('contact_discord', sa.String(), nullable=True),
        sa.Column('contact_email', sa.String(), nullable=True),
        sa.Column('contact_twitter', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_opponent_teams_id'), 'opponent_teams', ['id'], unique=False)
    op.create_index(op.f('ix_opponent_teams_name'), 'opponent_teams', ['name'], unique=True)

    # Create scrim_reviews table
    op.create_table(
        'scrim_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('calendar_event_id', sa.Integer(), nullable=False),
        sa.Column('opponent_team_id', sa.Integer(), nullable=True),
        sa.Column('quality', sa.String(), nullable=False),
        sa.Column('punctuality', sa.Integer(), nullable=True),
        sa.Column('communication', sa.Integer(), nullable=True),
        sa.Column('competitiveness', sa.Integer(), nullable=True),
        sa.Column('would_scrim_again', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['calendar_event_id'], ['calendar_events.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['opponent_team_id'], ['opponent_teams.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('calendar_event_id')
    )
    op.create_index(op.f('ix_scrim_reviews_id'), 'scrim_reviews', ['id'], unique=False)

    # Create scouted_players table
    op.create_table(
        'scouted_players',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('summoner_name', sa.String(), nullable=False),
        sa.Column('tag_line', sa.String(), nullable=True),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('mechanical_skill', sa.Integer(), nullable=True),
        sa.Column('game_sense', sa.Integer(), nullable=True),
        sa.Column('communication', sa.Integer(), nullable=True),
        sa.Column('attitude', sa.Integer(), nullable=True),
        sa.Column('potential', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_prospect', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['team_id'], ['opponent_teams.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scouted_players_id'), 'scouted_players', ['id'], unique=False)
    op.create_index(op.f('ix_scouted_players_summoner_name'), 'scouted_players', ['summoner_name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_scouted_players_summoner_name'), table_name='scouted_players')
    op.drop_index(op.f('ix_scouted_players_id'), table_name='scouted_players')
    op.drop_table('scouted_players')
    op.drop_index(op.f('ix_scrim_reviews_id'), table_name='scrim_reviews')
    op.drop_table('scrim_reviews')
    op.drop_index(op.f('ix_opponent_teams_name'), table_name='opponent_teams')
    op.drop_index(op.f('ix_opponent_teams_id'), table_name='opponent_teams')
    op.drop_table('opponent_teams')
