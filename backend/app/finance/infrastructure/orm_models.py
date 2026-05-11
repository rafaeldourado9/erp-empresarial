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


class CategoriaFinanceiroORM(Base):
    __tablename__ = "categorias_financeiro"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    empresa_id: Mapped[str] = mapped_column(String(36), ForeignKey("empresas.id"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # receita | custo | despesa
    cor: Mapped[str] = mapped_column(String(20), nullable=False, default="#6b7280")
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ContaORM(Base):
    __tablename__ = "contas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    empresa_id: Mapped[str] = mapped_column(String(36), ForeignKey("empresas.id"), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)  # pagar | receber
    descricao: Mapped[str] = mapped_column(String(300), nullable=False)
    parceiro: Mapped[str | None] = mapped_column(String(200), nullable=True)  # fornecedor / cliente
    valor: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    data_pagamento: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pendente")  # pendente | pago | cancelado
    orcamento_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("orcamentos.id"), nullable=True)
    cliente_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("clientes.id"), nullable=True)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_por: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
