from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class ClienteRequest(BaseModel):
    nome: str
    email: str | None = None
    telefone: str | None = None
    cpf_cnpj: str | None = None
    endereco: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    estado: str | None = None
    observacoes: str | None = None
    vendedor_id: UUID | None = None


class ClienteResponse(BaseModel):
    id: UUID
    empresa_id: UUID
    nome: str
    email: str | None
    telefone: str | None
    cpf_cnpj: str | None
    endereco: str | None
    bairro: str | None
    cidade: str | None
    estado: str | None
    observacoes: str | None
    vendedor_id: UUID | None
    ativo: bool
