"""finance_pagamentos_origem

Adiciona tabela `pagamentos_parciais` com histórico de abatimentos por conta,
coluna `origem` em `contas` e `movimentos_caixa` para integração com módulos,
e migra dados de `valor_abatimento` legado para a nova tabela.

Revision ID: g1h2i3j4k5l6
Revises: f9a0b1c2d3e4
Create Date: 2026-05-14 21:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'g1h2i3j4k5l6'
down_revision: Union[str, None] = 'f9a0b1c2d3e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Tabela pagamentos_parciais
    op.create_table(
        'pagamentos_parciais',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('conta_id', sa.String(36), sa.ForeignKey('contas.id', ondelete='CASCADE'),
                  nullable=False, index=True),
        sa.Column('valor', sa.Numeric(15, 2), nullable=False),
        sa.Column('data', sa.Date(), nullable=False, index=True),
        sa.Column('observacao', sa.Text(), nullable=True),
        sa.Column('operador_id', sa.String(36), sa.ForeignKey('usuarios.id'), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
    )

    # 2) origem em contas e movimentos
    op.add_column('contas',
        sa.Column('origem', sa.String(20), nullable=False, server_default='manual'),
    )
    op.add_column('movimentos_caixa',
        sa.Column('origem', sa.String(20), nullable=False, server_default='manual'),
    )

    # Backfill — orçamento_id != NULL implica origem='orcamento'
    op.execute("UPDATE contas SET origem = 'orcamento' WHERE orcamento_id IS NOT NULL")
    op.execute("UPDATE movimentos_caixa SET origem = 'orcamento' WHERE orcamento_id IS NOT NULL")

    # 3) Backfill: cada conta com valor_abatimento > 0 vira 1 pagamento parcial.
    #    Usa data_pagamento como data; criado_por como operador; motivo_abatimento como observacao.
    op.execute("""
        INSERT INTO pagamentos_parciais (id, conta_id, valor, data, observacao, operador_id, criado_em)
        SELECT
            gen_random_uuid()::text,
            id,
            valor_abatimento,
            COALESCE(data_pagamento, CURRENT_DATE),
            motivo_abatimento,
            criado_por,
            COALESCE(criado_em, NOW())
        FROM contas
        WHERE valor_abatimento IS NOT NULL AND valor_abatimento > 0
    """)


def downgrade() -> None:
    op.drop_column('movimentos_caixa', 'origem')
    op.drop_column('contas', 'origem')
    op.drop_table('pagamentos_parciais')
