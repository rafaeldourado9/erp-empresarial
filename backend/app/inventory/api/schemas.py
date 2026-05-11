from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ItemEstoqueRequest(BaseModel):
    descricao: str
    marca: str | None = None
    modelo: str | None = None
    quantidade: float = 0
    estoque_minimo: float | None = None
    valor_unitario: float | None = None
    valor_atribuido: float | None = None
    unidade: str = "un"


class ItemEstoqueResponse(BaseModel):
    id: UUID
    empresa_id: UUID
    descricao: str
    marca: str | None
    modelo: str | None
    quantidade: float
    estoque_minimo: float | None
    valor_unitario: float | None
    valor_atribuido: float | None
    unidade: str
    ativo: bool
    alerta_estoque_baixo: bool


class BaixaEstoqueRequest(BaseModel):
    quantidade: float
    observacao: str | None = None


class EntradaEstoqueRequest(BaseModel):
    quantidade: float
    observacao: str | None = None


class AjusteEstoqueRequest(BaseModel):
    quantidade: float  # nova quantidade absoluta
    observacao: str | None = None


class MovimentoEstoqueResponse(BaseModel):
    id: UUID
    item_id: UUID
    tipo: str
    quantidade: float
    quantidade_anterior: float
    quantidade_posterior: float
    observacao: str | None
    criado_por: UUID
    criado_em: datetime


class AlertaEstoqueResponse(BaseModel):
    id: UUID
    descricao: str
    marca: str | None
    modelo: str | None
    quantidade: float
    estoque_minimo: float
    unidade: str
    deficit: float
