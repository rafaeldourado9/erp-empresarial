from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegistroGrupoRequest(BaseModel):
    nome_grupo: str
    nome_empresa: str
    nome_admin: str
    email: EmailStr
    senha: str


class RegistroResponse(BaseModel):
    access_token: str
    refresh_token: str
    grupo_id: str
    empresa_id: str
    mensagem: str


class UsuarioResponse(BaseModel):
    id: UUID
    nome: str
    email: str
    perfil: str
    empresa_id: UUID | None
    grupo_id: UUID
    ativo: bool
    permissoes: list[str]


class CriarUsuarioRequest(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    perfil: str
    empresa_id: UUID | None = None
    permissoes: list[str] = []


class EmpresaResponse(BaseModel):
    id: UUID
    nome: str
    cnpj: str | None
    logo_url: str | None
    cor_primaria: str
    ativa: bool


class CriarEmpresaRequest(BaseModel):
    nome: str
    cnpj: str | None = None
    cor_primaria: str = "#2563eb"
