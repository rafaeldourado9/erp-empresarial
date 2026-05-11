from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class ComissaoORM(Base):
    __tablename__ = "comissoes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    empresa_id: Mapped[str] = mapped_column(String(36), ForeignKey("empresas.id"), nullable=False, index=True)
    orcamento_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("orcamentos.id"), nullable=True)
    orcamento_numero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    vendedor_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=False, index=True)
    vendedor_nome: Mapped[str | None] = mapped_column(String(200), nullable=True)
    valor_venda: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    percentual: Mapped[float] = mapped_column(Numeric(8, 4), nullable=False)
    valor_comissao: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pendente")  # pendente | pago | cancelado
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
