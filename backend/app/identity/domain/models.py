from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

import bcrypt

from app.identity.domain.constants import Permissao, PerfilUsuario


@dataclass
class Grupo:
    """Aggregate root: grupo empresarial (holding)."""

    id: UUID
    nome: str
    logo_url: str | None
    ativo: bool
    criado_em: datetime

    @classmethod
    def criar(cls, nome: str, logo_url: str | None = None) -> "Grupo":
        return cls(
            id=uuid4(),
            nome=nome,
            logo_url=logo_url,
            ativo=True,
            criado_em=datetime.now(UTC),
        )


@dataclass
class Empresa:
    """Uma empresa dentro do grupo."""

    id: UUID
    grupo_id: UUID
    nome: str
    cnpj: str | None
    logo_url: str | None
    cor_primaria: str
    ativa: bool
    criado_em: datetime
    nome_fantasia: str | None = None
    razao_social: str | None = None
    telefone: str | None = None
    email: str | None = None
    endereco: str | None = None

    @classmethod
    def criar(
        cls,
        grupo_id: UUID,
        nome: str,
        cnpj: str | None = None,
        logo_url: str | None = None,
        cor_primaria: str = "#2563eb",
    ) -> "Empresa":
        return cls(
            id=uuid4(),
            grupo_id=grupo_id,
            nome=nome,
            cnpj=cnpj,
            logo_url=logo_url,
            cor_primaria=cor_primaria,
            ativa=True,
            criado_em=datetime.now(UTC),
        )


@dataclass
class Usuario:
    """Operador/usuário do sistema."""

    id: UUID
    grupo_id: UUID
    empresa_id: UUID | None
    nome: str
    email: str
    senha_hash: str
    perfil: PerfilUsuario
    permissoes: list[Permissao]
    ativo: bool
    criado_em: datetime

    @classmethod
    def criar(
        cls,
        grupo_id: UUID,
        nome: str,
        email: str,
        senha_plaintext: str,
        perfil: PerfilUsuario = PerfilUsuario.OPERADOR,
        permissoes: list[Permissao] | None = None,
        empresa_id: UUID | None = None,
    ) -> "Usuario":
        senha_hash = bcrypt.hashpw(
            senha_plaintext.encode(), bcrypt.gensalt(rounds=12)
        ).decode()
        return cls(
            id=uuid4(),
            grupo_id=grupo_id,
            empresa_id=empresa_id,
            nome=nome,
            email=email.lower().strip(),
            senha_hash=senha_hash,
            perfil=perfil,
            permissoes=permissoes or [],
            ativo=True,
            criado_em=datetime.now(UTC),
        )

    def verificar_senha(self, senha: str) -> bool:
        return bcrypt.checkpw(senha.encode(), self.senha_hash.encode())

    def tem_permissao(self, permissao: Permissao) -> bool:
        if self.perfil in (PerfilUsuario.ADMIN_GRUPO, PerfilUsuario.ADMIN_EMPRESA):
            return True
        return permissao in self.permissoes

    def pode_acessar_empresa(self, empresa_id: UUID) -> bool:
        if self.perfil == PerfilUsuario.ADMIN_GRUPO:
            return True
        return self.empresa_id == empresa_id
