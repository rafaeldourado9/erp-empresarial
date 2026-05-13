"""variaveis_orcamento

Revision ID: b5c9d2e3f4a1
Revises: a4f8c1d2e3b7
Create Date: 2026-05-13 10:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b5c9d2e3f4a1'
down_revision: Union[str, None] = 'a4f8c1d2e3b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'variaveis_orcamento',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('empresa_id', sa.String(36), sa.ForeignKey('empresas.id'), nullable=False, index=True),
        sa.Column('chave', sa.String(100), nullable=False),
        sa.Column('label', sa.String(200), nullable=False),
        sa.Column('grupo', sa.String(100), nullable=False, server_default='Personalizado'),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('empresa_id', 'chave', name='uq_variaveis_empresa_chave'),
    )


def downgrade() -> None:
    op.drop_table('variaveis_orcamento')
