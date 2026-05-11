from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.domain.models import Empresa, Grupo, Usuario
from app.identity.infrastructure.mappers import (
    empresa_to_domain, empresa_to_orm,
    grupo_to_domain, grupo_to_orm,
    usuario_to_domain, usuario_to_orm,
)
from app.identity.infrastructure.orm_models import EmpresaORM, GrupoORM, UsuarioORM


class GrupoRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def salvar(self, grupo: Grupo) -> None:
        orm = grupo_to_orm(grupo)
        await self._db.merge(orm)
        await self._db.flush()

    async def buscar_por_id(self, grupo_id: UUID) -> Grupo | None:
        result = await self._db.execute(
            select(GrupoORM).where(GrupoORM.id == str(grupo_id))
        )
        orm = result.scalar_one_or_none()
        return grupo_to_domain(orm) if orm else None

    async def listar(self) -> list[Grupo]:
        result = await self._db.execute(select(GrupoORM).where(GrupoORM.ativo == True))
        return [grupo_to_domain(o) for o in result.scalars()]


class EmpresaRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def salvar(self, empresa: Empresa) -> None:
        orm = empresa_to_orm(empresa)
        await self._db.merge(orm)
        await self._db.flush()

    async def buscar_por_id(self, empresa_id: UUID) -> Empresa | None:
        result = await self._db.execute(
            select(EmpresaORM).where(EmpresaORM.id == str(empresa_id))
        )
        orm = result.scalar_one_or_none()
        return empresa_to_domain(orm) if orm else None

    async def listar_por_grupo(self, grupo_id: UUID) -> list[Empresa]:
        result = await self._db.execute(
            select(EmpresaORM)
            .where(EmpresaORM.grupo_id == str(grupo_id), EmpresaORM.ativa == True)
        )
        return [empresa_to_domain(o) for o in result.scalars()]


class UsuarioRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def salvar(self, usuario: Usuario) -> None:
        orm = usuario_to_orm(usuario)
        await self._db.merge(orm)
        await self._db.flush()

    async def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        result = await self._db.execute(
            select(UsuarioORM).where(UsuarioORM.id == str(usuario_id))
        )
        orm = result.scalar_one_or_none()
        return usuario_to_domain(orm) if orm else None

    async def buscar_por_email(self, email: str) -> Usuario | None:
        result = await self._db.execute(
            select(UsuarioORM).where(UsuarioORM.email == email.lower().strip())
        )
        orm = result.scalar_one_or_none()
        return usuario_to_domain(orm) if orm else None

    async def listar_por_empresa(self, empresa_id: UUID) -> list[Usuario]:
        result = await self._db.execute(
            select(UsuarioORM).where(UsuarioORM.empresa_id == str(empresa_id))
        )
        return [usuario_to_domain(o) for o in result.scalars()]

    async def listar_por_grupo(self, grupo_id: UUID) -> list[Usuario]:
        result = await self._db.execute(
            select(UsuarioORM).where(UsuarioORM.grupo_id == str(grupo_id))
        )
        return [usuario_to_domain(o) for o in result.scalars()]
