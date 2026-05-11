from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class PremissaORM(Base):
    __tablename__ = "premissas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    empresa_id: Mapped[str] = mapped_column(String(36), ForeignKey("empresas.id"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # percentual | fixo
    valor: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OrcamentoORM(Base):
    __tablename__ = "orcamentos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    empresa_id: Mapped[str] = mapped_column(String(36), ForeignKey("empresas.id"), nullable=False, index=True)
    cliente_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("clientes.id"), nullable=True)
    criado_por: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=False)
    numero: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    titulo: Mapped[str] = mapped_column(String(300), nullable=False)
    custo_base: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    valor_venda: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="rascunho")
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    validade_dias: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    endereco: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    cpf: Mapped[str | None] = mapped_column(String(20), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    aprovado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fechado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class PremissaOrcamentoORM(Base):
    """Premissa congelada no momento em que foi aplicada ao orçamento."""
    __tablename__ = "premissas_orcamento"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    orcamento_id: Mapped[str] = mapped_column(String(36), ForeignKey("orcamentos.id", ondelete="CASCADE"), nullable=False, index=True)
    premissa_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("premissas.id"), nullable=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # percentual | fixo
    valor: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    valor_calculado: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class ItemOrcamentoORM(Base):
    __tablename__ = "itens_orcamento"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    orcamento_id: Mapped[str] = mapped_column(String(36), ForeignKey("orcamentos.id", ondelete="CASCADE"), nullable=False, index=True)
    item_estoque_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("itens_estoque.id"), nullable=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # manual | produto
    descricao: Mapped[str] = mapped_column(String(300), nullable=False)
    quantidade: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    valor_unitario: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    valor_calculado: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
