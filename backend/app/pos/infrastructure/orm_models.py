from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database import Base


class SessaoCaixaORM(Base):
    __tablename__ = "sessoes_caixa"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    empresa_id: Mapped[str] = mapped_column(String(36), ForeignKey("empresas.id"), nullable=False, index=True)
    operador_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios.id"), nullable=False)
    saldo_inicial: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    saldo_final: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    aberta: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    aberto_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fechado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ProdutoCaixaORM(Base):
    """Tabela de produtos do caixa — estoque próprio, independente do estoque principal."""
    __tablename__ = "produtos_caixa"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    empresa_id: Mapped[str] = mapped_column(String(36), ForeignKey("empresas.id"), nullable=False, index=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    valor: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    unidade: Mapped[str] = mapped_column(String(20), nullable=False, default="un")
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class OrdemServicoORM(Base):
    __tablename__ = "ordens_servico"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    sessao_id: Mapped[str] = mapped_column(String(36), ForeignKey("sessoes_caixa.id"), nullable=False, index=True)
    empresa_id: Mapped[str] = mapped_column(String(36), ForeignKey("empresas.id"), nullable=False, index=True)
    numero: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    nome_cliente: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo_servico: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao_servico: Mapped[str] = mapped_column(Text, nullable=False)
    valor_servico: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    valor_produtos: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    desconto: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False, default=0)
    total: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    forma_pagamento: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="aberta")
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    concluido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ItemOSORM(Base):
    """Produto usado numa OS, com valor atribuído no momento da criação."""
    __tablename__ = "itens_os"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    os_id: Mapped[str] = mapped_column(String(36), ForeignKey("ordens_servico.id", ondelete="CASCADE"), nullable=False, index=True)
    produto_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("produtos_caixa.id"), nullable=True)
    descricao: Mapped[str] = mapped_column(String(300), nullable=False)
    quantidade: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False, default=1)
    valor_unitario: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    valor_total: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
