from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class ItemEstoqueORM(Base):
    __tablename__ = "itens_estoque"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    empresa_id: Mapped[str] = mapped_column(String(36), ForeignKey("empresas.id"), nullable=False, index=True)
    marca: Mapped[str | None] = mapped_column(String(100), nullable=True)
    modelo: Mapped[str | None] = mapped_column(String(100), nullable=True)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    quantidade: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False, default=0)
    estoque_minimo: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    valor_unitario: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    valor_atribuido: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    unidade: Mapped[str] = mapped_column(String(20), nullable=False, default="un")
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class MovimentoEstoqueORM(Base):
    __tablename__ = "movimentos_estoque"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    empresa_id: Mapped[str] = mapped_column(String(36), ForeignKey("empresas.id"), nullable=False, index=True)
    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("itens_estoque.id"), nullable=False, index=True)
    criado_por: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # baixa | entrada | ajuste
    quantidade: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    quantidade_anterior: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    quantidade_posterior: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
