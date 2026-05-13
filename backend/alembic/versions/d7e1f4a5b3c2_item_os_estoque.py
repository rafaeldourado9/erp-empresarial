"""item_os_estoque

Revision ID: d7e1f4a5b3c2
Revises: c6d8e3f5a2b1
Create Date: 2026-05-13 12:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd7e1f4a5b3c2'
down_revision: Union[str, None] = 'c6d8e3f5a2b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('itens_os', sa.Column(
        'item_estoque_id', sa.String(36),
        sa.ForeignKey('itens_estoque.id'), nullable=True,
    ))


def downgrade() -> None:
    op.drop_column('itens_os', 'item_estoque_id')
