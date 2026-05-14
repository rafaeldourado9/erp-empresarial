"""solar_data_orcamento

Revision ID: e8f1a2b3c4d5
Revises: d7e1f4a5b3c2
Create Date: 2026-05-14 10:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e8f1a2b3c4d5'
down_revision: Union[str, None] = 'd7e1f4a5b3c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('orcamentos', sa.Column('solar_data', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('orcamentos', 'solar_data')
