from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


# ── Premissas (templates) ─────────────────────────────────────────────────────

class PremissaRequest(BaseModel):
    nome: str
    descricao: str | None = None
    tipo: str  # percentual | fixo
    valor: float
    ordem: int = 0


class PremissaResponse(BaseModel):
    id: UUID
    nome: str
    descricao: str | None
    tipo: str
    valor: float
    ordem: int
    ativo: bool


# ── Premissas aplicadas ao orçamento ─────────────────────────────────────────

class PremissaOrcamentoRequest(BaseModel):
    premissa_id: UUID | None = None   # se informado, carrega nome/tipo/valor do template
    nome: str | None = None           # obrigatório se premissa_id for None
    descricao: str | None = None
    tipo: str | None = None           # obrigatório se premissa_id for None
    valor: float | None = None        # obrigatório se premissa_id for None
    ordem: int = 0


class PremissaOrcamentoResponse(BaseModel):
    id: UUID
    premissa_id: UUID | None
    nome: str
    descricao: str | None
    tipo: str
    valor: float
    valor_calculado: float
    ordem: int


# ── Itens do orçamento (manual / produto) ─────────────────────────────────────

class ItemOrcamentoRequest(BaseModel):
    tipo: str = "manual"  # manual | produto
    descricao: str
    item_estoque_id: UUID | None = None
    quantidade: float | None = None
    valor_unitario: float | None = None
    ordem: int = 0


class ItemOrcamentoResponse(BaseModel):
    id: UUID
    tipo: str
    descricao: str
    item_estoque_id: UUID | None
    quantidade: float | None
    valor_unitario: float | None
    valor_calculado: float
    ordem: int


# ── Orçamento ─────────────────────────────────────────────────────────────────

class OrcamentoRequest(BaseModel):
    titulo: str
    custo_base: float
    valor_venda: float | None = None
    cliente_id: UUID | None = None
    vendedor_id: UUID | None = None
    observacoes: str | None = None
    validade_dias: int = 30
    endereco: str | None = None
    email: str | None = None
    telefone: str | None = None
    cpf: str | None = None
    campos_extras: dict = {}
    premissas: list[PremissaOrcamentoRequest] = []
    itens: list[ItemOrcamentoRequest] = []


class FecharOrcamentoRequest(BaseModel):
    endereco: str
    email: str
    telefone: str
    cpf: str


class OrcamentoResponse(BaseModel):
    id: UUID
    empresa_id: UUID
    numero: str
    titulo: str
    custo_base: float
    subtotal: float
    valor_venda: float
    status: str
    cliente_id: UUID | None
    vendedor_id: UUID | None
    criado_por: UUID
    criado_em: datetime
    atualizado_em: datetime
    aprovado_em: datetime | None
    enviado_em: datetime | None
    fechado_em: datetime | None
    observacoes: str | None
    validade_dias: int
    endereco: str | None
    email: str | None
    telefone: str | None
    cpf: str | None
    campos_extras: dict = {}
    premissas: list[PremissaOrcamentoResponse] = []
    itens: list[ItemOrcamentoResponse] = []


# ── Cálculo em tempo real ─────────────────────────────────────────────────────

class CalcularOrcamentoRequest(BaseModel):
    custo_base: float
    valor_venda: float | None = None
    premissas: list[PremissaOrcamentoRequest] = []
    itens: list[ItemOrcamentoRequest] = []


class CalcularOrcamentoResponse(BaseModel):
    custo_base: float
    subtotal_premissas: float
    subtotal_itens: float
    subtotal: float
    valor_venda: float
    premissas: list[dict]
    itens: list[dict]
