from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.infrastructure.orm_models import ClienteORM


class ClienteRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def criar(self, empresa_id: UUID, nome: str, email: str | None = None,
                    telefone: str | None = None, cpf_cnpj: str | None = None,
                    observacoes: str | None = None) -> ClienteORM:
        orm = ClienteORM(
            id=str(uuid4()), empresa_id=str(empresa_id), nome=nome,
            email=email, telefone=telefone, cpf_cnpj=cpf_cnpj,
            observacoes=observacoes, ativo=True, criado_em=datetime.now(UTC),
        )
        self._db.add(orm)
        await self._db.flush()
        return orm

    async def buscar_por_id(self, cliente_id: UUID, empresa_id: UUID) -> ClienteORM | None:
        result = await self._db.execute(
            select(ClienteORM).where(
                ClienteORM.id == str(cliente_id),
                ClienteORM.empresa_id == str(empresa_id),
            )
        )
        return result.scalar_one_or_none()

    async def listar(self, empresa_id: UUID, busca: str | None = None) -> list[ClienteORM]:
        query = select(ClienteORM).where(
            ClienteORM.empresa_id == str(empresa_id),
            ClienteORM.ativo == True,
        )
        if busca:
            query = query.where(ClienteORM.nome.ilike(f"%{busca}%"))
        result = await self._db.execute(query.order_by(ClienteORM.nome))
        return list(result.scalars())

    async def salvar(self, orm: ClienteORM) -> None:
        await self._db.merge(orm)
        await self._db.flush()
