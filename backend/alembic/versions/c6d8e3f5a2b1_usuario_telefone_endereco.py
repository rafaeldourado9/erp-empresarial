"""usuario_telefone_endereco

Revision ID: c6d8e3f5a2b1
Revises: b5c9d2e3f4a1
Create Date: 2026-05-13 11:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c6d8e3f5a2b1'
down_revision: Union[str, None] = 'b5c9d2e3f4a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('usuarios', sa.Column('telefone', sa.String(30), nullable=True))
    op.add_column('usuarios', sa.Column('endereco', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('usuarios', 'endereco')
    op.drop_column('usuarios', 'telefone')
