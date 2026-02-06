"""Add multi-tenancy support with teams table

Revision ID: f6g7h8i9j0k1
Revises: e5f6g7h8i9j0
Create Date: 2026-02-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6g7h8i9j0k1'
down_revision: Union[str, None] = 'e5f6g7h8i9j0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('access_code', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)
    op.create_index(op.f('ix_teams_access_code'), 'teams', ['access_code'], unique=True)

    # 2. Insert default "Shortcut" team with the current access code
    op.execute("""
        INSERT INTO teams (id, name, access_code, created_at)
        VALUES (1, 'Shortcut', 'oracle2026', NOW())
    """)

    # 3. Add team_id to players table
    op.add_column('players', sa.Column('team_id', sa.Integer(), nullable=True))
    op.execute("UPDATE players SET team_id = 1")
    op.alter_column('players', 'team_id', nullable=False)
    op.create_index(op.f('ix_players_team_id'), 'players', ['team_id'], unique=False)
    op.create_foreign_key('fk_players_team_id', 'players', 'teams', ['team_id'], ['id'], ondelete='CASCADE')

    # Drop old unique index on summoner_name and create composite one
    op.drop_index('ix_players_summoner_name', 'players')
    op.create_unique_constraint('uq_player_team_summoner', 'players', ['team_id', 'summoner_name'])

    # 4. Add team_id to coaches table
    op.add_column('coaches', sa.Column('team_id', sa.Integer(), nullable=True))
    op.execute("UPDATE coaches SET team_id = 1")
    op.alter_column('coaches', 'team_id', nullable=False)
    op.create_index(op.f('ix_coaches_team_id'), 'coaches', ['team_id'], unique=False)
    op.create_foreign_key('fk_coaches_team_id', 'coaches', 'teams', ['team_id'], ['id'], ondelete='CASCADE')

    # Drop old unique index on name and create composite one
    op.drop_index('ix_coaches_name', 'coaches')
    op.create_unique_constraint('uq_coach_team_name', 'coaches', ['team_id', 'name'])

    # 5. Add team_id to draft_series table
    op.add_column('draft_series', sa.Column('team_id', sa.Integer(), nullable=True))
    op.execute("UPDATE draft_series SET team_id = 1")
    op.alter_column('draft_series', 'team_id', nullable=False)
    op.create_index(op.f('ix_draft_series_team_id'), 'draft_series', ['team_id'], unique=False)
    op.create_foreign_key('fk_draft_series_team_id', 'draft_series', 'teams', ['team_id'], ['id'], ondelete='CASCADE')

    # 6. Add team_id to calendar_events table
    op.add_column('calendar_events', sa.Column('team_id', sa.Integer(), nullable=True))
    op.execute("UPDATE calendar_events SET team_id = 1")
    op.alter_column('calendar_events', 'team_id', nullable=False)
    op.create_index(op.f('ix_calendar_events_team_id'), 'calendar_events', ['team_id'], unique=False)
    op.create_foreign_key('fk_calendar_events_team_id', 'calendar_events', 'teams', ['team_id'], ['id'], ondelete='CASCADE')

    # 7. Add team_id to opponent_teams table
    op.add_column('opponent_teams', sa.Column('team_id', sa.Integer(), nullable=True))
    op.execute("UPDATE opponent_teams SET team_id = 1")
    op.alter_column('opponent_teams', 'team_id', nullable=False)
    op.create_index(op.f('ix_opponent_teams_team_id'), 'opponent_teams', ['team_id'], unique=False)
    op.create_foreign_key('fk_opponent_teams_team_id', 'opponent_teams', 'teams', ['team_id'], ['id'], ondelete='CASCADE')

    # Drop old unique constraint on name (different teams can have same opponent names)
    op.drop_index('ix_opponent_teams_name', 'opponent_teams')

    # 8. Rename scouted_players.team_id to opponent_team_id
    op.alter_column('scouted_players', 'team_id', new_column_name='opponent_team_id')


def downgrade() -> None:
    # Reverse the migration

    # 8. Rename back
    op.alter_column('scouted_players', 'opponent_team_id', new_column_name='team_id')

    # 7. Remove team_id from opponent_teams
    op.create_index('ix_opponent_teams_name', 'opponent_teams', ['name'], unique=True)
    op.drop_constraint('fk_opponent_teams_team_id', 'opponent_teams', type_='foreignkey')
    op.drop_index(op.f('ix_opponent_teams_team_id'), 'opponent_teams')
    op.drop_column('opponent_teams', 'team_id')

    # 6. Remove team_id from calendar_events
    op.drop_constraint('fk_calendar_events_team_id', 'calendar_events', type_='foreignkey')
    op.drop_index(op.f('ix_calendar_events_team_id'), 'calendar_events')
    op.drop_column('calendar_events', 'team_id')

    # 5. Remove team_id from draft_series
    op.drop_constraint('fk_draft_series_team_id', 'draft_series', type_='foreignkey')
    op.drop_index(op.f('ix_draft_series_team_id'), 'draft_series')
    op.drop_column('draft_series', 'team_id')

    # 4. Remove team_id from coaches
    op.drop_constraint('uq_coach_team_name', 'coaches', type_='unique')
    op.create_index('ix_coaches_name', 'coaches', ['name'], unique=True)
    op.drop_constraint('fk_coaches_team_id', 'coaches', type_='foreignkey')
    op.drop_index(op.f('ix_coaches_team_id'), 'coaches')
    op.drop_column('coaches', 'team_id')

    # 3. Remove team_id from players
    op.drop_constraint('uq_player_team_summoner', 'players', type_='unique')
    op.create_index('ix_players_summoner_name', 'players', ['summoner_name'], unique=True)
    op.drop_constraint('fk_players_team_id', 'players', type_='foreignkey')
    op.drop_index(op.f('ix_players_team_id'), 'players')
    op.drop_column('players', 'team_id')

    # 2. Delete default team (data would be orphaned anyway)
    op.execute("DELETE FROM teams WHERE id = 1")

    # 1. Drop teams table
    op.drop_index(op.f('ix_teams_access_code'), 'teams')
    op.drop_index(op.f('ix_teams_id'), 'teams')
    op.drop_table('teams')
