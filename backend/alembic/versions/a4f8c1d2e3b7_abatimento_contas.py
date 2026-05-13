"""abatimento_contas

Revision ID: a4f8c1d2e3b7
Revises: c289bdf9a8c6
Create Date: 2026-05-12 20:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a4f8c1d2e3b7'
down_revision: Union[str, None] = 'f3a1d9e7b2c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('contas', sa.Column('valor_abatimento', sa.Numeric(15, 2), nullable=False, server_default='0'))
    op.add_column('contas', sa.Column('motivo_abatimento', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('contas', 'motivo_abatimento')
    op.drop_column('contas', 'valor_abatimento')
