"""templates_proposta — múltiplos templates DOCX por empresa

Revision ID: i3j4k5l6m7n8
Revises: h2i3j4k5l6m7
Create Date: 2026-05-15 14:00:00.000000
"""
from __future__ import annotations
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'i3j4k5l6m7n8'
down_revision: Union[str, None] = 'h2i3j4k5l6m7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'templates_proposta',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('empresa_id', sa.String(36), sa.ForeignKey('empresas.id'), nullable=False, index=True),
        sa.Column('nome', sa.String(200), nullable=False),
        sa.Column('descricao', sa.Text, nullable=True),
        sa.Column('arquivo_path', sa.String(500), nullable=False),
        sa.Column('padrao', sa.Boolean, nullable=False, default=False),
        sa.Column('ativo', sa.Boolean, nullable=False, default=True),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('templates_proposta')
