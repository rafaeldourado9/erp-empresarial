"""campos_extras orcamentos e endereco completo clientes

Revision ID: f3a1d9e7b2c5
Revises: c289bdf9a8c6
Create Date: 2026-05-11 18:00:00.000000

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f3a1d9e7b2c5"
down_revision: Union[str, None] = "c289bdf9a8c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Orçamentos: campos extras (JSON) para variáveis de proposta
    op.add_column("orcamentos", sa.Column("campos_extras", sa.JSON(), nullable=True))

    # Clientes: endereço detalhado
    # Converte coluna endereco de JSON para TEXT (dados podem já estar como string)
    op.alter_column("clientes", "endereco",
                    existing_type=sa.JSON(),
                    type_=sa.Text(),
                    existing_nullable=True,
                    postgresql_using="endereco::text")
    op.add_column("clientes", sa.Column("bairro", sa.String(100), nullable=True))
    op.add_column("clientes", sa.Column("cidade", sa.String(100), nullable=True))
    op.add_column("clientes", sa.Column("estado", sa.String(2), nullable=True))


def downgrade() -> None:
    op.drop_column("clientes", "estado")
    op.drop_column("clientes", "cidade")
    op.drop_column("clientes", "bairro")
    op.alter_column("clientes", "endereco",
                    existing_type=sa.Text(),
                    type_=sa.JSON(),
                    existing_nullable=True)
    op.drop_column("orcamentos", "campos_extras")
