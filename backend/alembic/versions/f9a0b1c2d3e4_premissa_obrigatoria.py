"""premissa_obrigatoria

Revision ID: f9a0b1c2d3e4
Revises: e8f1a2b3c4d5
Create Date: 2026-05-14 19:50:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f9a0b1c2d3e4'
down_revision: Union[str, None] = 'e8f1a2b3c4d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'premissas',
        sa.Column('obrigatoria', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        'premissas_orcamento',
        sa.Column('obrigatoria', sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column('premissas_orcamento', 'obrigatoria')
    op.drop_column('premissas', 'obrigatoria')
