"""orcamento_numero_por_empresa

Corrige constraint de unicidade do número do orçamento:
era global (numero único entre TODAS as empresas),
passa a ser por empresa (empresa_id, numero) — cada empresa tem sua própria sequência.

Revision ID: h2i3j4k5l6m7
Revises: g1h2i3j4k5l6
Create Date: 2026-05-15 12:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = 'h2i3j4k5l6m7'
down_revision: Union[str, None] = 'g1h2i3j4k5l6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove constraint global
    op.drop_index('ix_orcamentos_numero', table_name='orcamentos')
    # Cria constraint composta por empresa
    op.create_index(
        'ix_orcamentos_empresa_numero',
        'orcamentos',
        ['empresa_id', 'numero'],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index('ix_orcamentos_empresa_numero', table_name='orcamentos')
    op.create_index('ix_orcamentos_numero', 'orcamentos', ['numero'], unique=True)
