from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class MovimentoCaixaORM(Base):
    __tablename__ = "movimentos_caixa"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    empresa_id: Mapped[str] = mapped_column(String(36), ForeignKey("empresas.id"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)  # entrada | saida
    categoria: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    valor: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    orcamento_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("orcamentos.id"), nullable=True)
    criado_por: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    conciliado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
