"""Add last_refreshed_at to riot_accounts

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-02-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h8i9j0k1l2m3'
down_revision: Union[str, None] = 'g7h8i9j0k1l2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('riot_accounts', sa.Column('last_refreshed_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('riot_accounts', 'last_refreshed_at')
