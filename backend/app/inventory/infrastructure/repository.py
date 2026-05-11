from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.infrastructure.orm_models import ItemEstoqueORM, MovimentoEstoqueORM


class ItemEstoqueRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def criar(self, empresa_id: UUID, descricao: str, marca: str | None = None,
                    modelo: str | None = None, quantidade: float = 0,
                    estoque_minimo: float | None = None,
                    valor_unitario: float | None = None, valor_atribuido: float | None = None,
                    unidade: str = "un") -> ItemEstoqueORM:
        agora = datetime.now(UTC)
        orm = ItemEstoqueORM(
            id=str(uuid4()), empresa_id=str(empresa_id), descricao=descricao,
            marca=marca, modelo=modelo, quantidade=quantidade,
            estoque_minimo=estoque_minimo,
            valor_unitario=valor_unitario, valor_atribuido=valor_atribuido,
            unidade=unidade, ativo=True, criado_em=agora, atualizado_em=agora,
        )
        self._db.add(orm)
        await self._db.flush()
        return orm

    async def buscar_por_id(self, item_id: UUID, empresa_id: UUID) -> ItemEstoqueORM | None:
        result = await self._db.execute(
            select(ItemEstoqueORM).where(
                ItemEstoqueORM.id == str(item_id),
                ItemEstoqueORM.empresa_id == str(empresa_id),
            )
        )
        return result.scalar_one_or_none()

    async def listar(self, empresa_id: UUID, busca: str | None = None) -> list[ItemEstoqueORM]:
        query = select(ItemEstoqueORM).where(
            ItemEstoqueORM.empresa_id == str(empresa_id),
            ItemEstoqueORM.ativo == True,
        )
        if busca:
            query = query.where(
                ItemEstoqueORM.descricao.ilike(f"%{busca}%") |
                ItemEstoqueORM.marca.ilike(f"%{busca}%") |
                ItemEstoqueORM.modelo.ilike(f"%{busca}%")
            )
        result = await self._db.execute(query.order_by(ItemEstoqueORM.descricao))
        return list(result.scalars())

    async def listar_alertas(self, empresa_id: UUID) -> list[ItemEstoqueORM]:
        result = await self._db.execute(
            select(ItemEstoqueORM).where(
                ItemEstoqueORM.empresa_id == str(empresa_id),
                ItemEstoqueORM.ativo == True,
                ItemEstoqueORM.estoque_minimo.is_not(None),
                ItemEstoqueORM.quantidade < ItemEstoqueORM.estoque_minimo,
            ).order_by(ItemEstoqueORM.descricao)
        )
        return list(result.scalars())

    async def salvar(self, orm: ItemEstoqueORM) -> None:
        orm.atualizado_em = datetime.now(UTC)
        await self._db.merge(orm)
        await self._db.flush()


class MovimentoEstoqueRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def registrar(
        self,
        empresa_id: UUID,
        item_id: UUID,
        criado_por: UUID,
        tipo: str,
        quantidade: float,
        quantidade_anterior: float,
        quantidade_posterior: float,
        observacao: str | None = None,
    ) -> MovimentoEstoqueORM:
        orm = MovimentoEstoqueORM(
            id=str(uuid4()),
            empresa_id=str(empresa_id),
            item_id=str(item_id),
            criado_por=str(criado_por),
            tipo=tipo,
            quantidade=quantidade,
            quantidade_anterior=quantidade_anterior,
            quantidade_posterior=quantidade_posterior,
            observacao=observacao,
            criado_em=datetime.now(UTC),
        )
        self._db.add(orm)
        await self._db.flush()
        return orm

    async def listar_por_item(self, item_id: UUID, empresa_id: UUID) -> list[MovimentoEstoqueORM]:
        result = await self._db.execute(
            select(MovimentoEstoqueORM).where(
                MovimentoEstoqueORM.item_id == str(item_id),
                MovimentoEstoqueORM.empresa_id == str(empresa_id),
            ).order_by(MovimentoEstoqueORM.criado_em.desc())
        )
        return list(result.scalars())
