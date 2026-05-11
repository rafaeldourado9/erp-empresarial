from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class ClienteRequest(BaseModel):
    nome: str
    email: str | None = None
    telefone: str | None = None
    cpf_cnpj: str | None = None
    observacoes: str | None = None


class ClienteResponse(BaseModel):
    id: UUID
    empresa_id: UUID
    nome: str
    email: str | None
    telefone: str | None
    cpf_cnpj: str | None
    observacoes: str | None
    ativo: bool
