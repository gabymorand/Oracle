"""make rank_history division nullable

Revision ID: 9f7baf8744a8
Revises: c812d6eb6b0c
Create Date: 2026-01-18 06:08:43.193268

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f7baf8744a8'
down_revision: Union[str, None] = 'c812d6eb6b0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make division column nullable for Master/Grandmaster/Challenger ranks
    op.alter_column('rank_history', 'division',
                    existing_type=sa.String(),
                    nullable=True)


def downgrade() -> None:
    # Revert division column to not nullable
    op.alter_column('rank_history', 'division',
                    existing_type=sa.String(),
                    nullable=False)
