from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.quotes.infrastructure.orm_models import (
    ItemOrcamentoORM, OrcamentoORM, PremissaOrcamentoORM, PremissaORM,
)


class PremissaRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def listar(self, empresa_id: UUID) -> list[PremissaORM]:
        result = await self._db.execute(
            select(PremissaORM)
            .where(PremissaORM.empresa_id == str(empresa_id), PremissaORM.ativo == True)
            .order_by(PremissaORM.ordem, PremissaORM.nome)
        )
        return list(result.scalars())

    async def buscar_por_id(self, premissa_id: UUID, empresa_id: UUID) -> PremissaORM | None:
        result = await self._db.execute(
            select(PremissaORM).where(
                PremissaORM.id == str(premissa_id),
                PremissaORM.empresa_id == str(empresa_id),
            )
        )
        return result.scalar_one_or_none()

    async def salvar(self, orm: PremissaORM) -> None:
        await self._db.merge(orm)
        await self._db.flush()

    async def criar(
        self, empresa_id: UUID, nome: str, tipo: str, valor: float,
        ordem: int = 0, descricao: str | None = None, obrigatoria: bool = False,
    ) -> PremissaORM:
        orm = PremissaORM(
            id=str(uuid4()), empresa_id=str(empresa_id), nome=nome,
            descricao=descricao, tipo=tipo, valor=valor, ordem=ordem,
            ativo=True, obrigatoria=obrigatoria, criado_em=datetime.now(UTC),
        )
        self._db.add(orm)
        await self._db.flush()
        return orm

    async def listar_obrigatorias(self, empresa_id: UUID) -> list[PremissaORM]:
        result = await self._db.execute(
            select(PremissaORM)
            .where(
                PremissaORM.empresa_id == str(empresa_id),
                PremissaORM.ativo == True,
                PremissaORM.obrigatoria == True,
            )
            .order_by(PremissaORM.ordem, PremissaORM.nome)
        )
        return list(result.scalars())


class OrcamentoRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _proximo_numero(self, empresa_id: UUID) -> str:
        result = await self._db.execute(
            select(func.count()).where(OrcamentoORM.empresa_id == str(empresa_id))
        )
        count = result.scalar() or 0
        return f"ORC-{count + 1:05d}"

    async def criar(
        self, empresa_id: UUID, criado_por: UUID, titulo: str,
        custo_base: float, subtotal: float, valor_venda: float,
        cliente_id: UUID | None = None, vendedor_id: UUID | None = None,
        observacoes: str | None = None, validade_dias: int = 30,
        endereco: str | None = None, email: str | None = None,
        telefone: str | None = None, cpf: str | None = None,
    ) -> OrcamentoORM:
        agora = datetime.now(UTC)
        orm = OrcamentoORM(
            id=str(uuid4()), empresa_id=str(empresa_id), criado_por=str(criado_por),
            numero=await self._proximo_numero(empresa_id),
            titulo=titulo, custo_base=custo_base, subtotal=subtotal,
            valor_venda=valor_venda, status="rascunho",
            cliente_id=str(cliente_id) if cliente_id else None,
            vendedor_id=str(vendedor_id) if vendedor_id else None,
            observacoes=observacoes, validade_dias=validade_dias,
            endereco=endereco, email=email, telefone=telefone, cpf=cpf,
            criado_em=agora, atualizado_em=agora,
        )
        self._db.add(orm)
        await self._db.flush()
        return orm

    async def buscar_por_id(self, orc_id: UUID, empresa_id: UUID) -> OrcamentoORM | None:
        result = await self._db.execute(
            select(OrcamentoORM).where(
                OrcamentoORM.id == str(orc_id),
                OrcamentoORM.empresa_id == str(empresa_id),
            )
        )
        return result.scalar_one_or_none()

    async def listar(self, empresa_id: UUID, status_filtro: str | None = None) -> list[OrcamentoORM]:
        query = select(OrcamentoORM).where(OrcamentoORM.empresa_id == str(empresa_id))
        if status_filtro:
            query = query.where(OrcamentoORM.status == status_filtro)
        result = await self._db.execute(query.order_by(OrcamentoORM.criado_em.desc()))
        return list(result.scalars())

    async def salvar(self, orm: OrcamentoORM) -> None:
        orm.atualizado_em = datetime.now(UTC)
        await self._db.merge(orm)
        await self._db.flush()

    async def deletar(self, orc_id: UUID) -> None:
        await self._db.execute(
            delete(PremissaOrcamentoORM).where(PremissaOrcamentoORM.orcamento_id == str(orc_id))
        )
        await self._db.execute(
            delete(ItemOrcamentoORM).where(ItemOrcamentoORM.orcamento_id == str(orc_id))
        )
        await self._db.execute(delete(OrcamentoORM).where(OrcamentoORM.id == str(orc_id)))
        await self._db.flush()

    # ── Premissas do orçamento ────────────────────────────────────────────────

    async def listar_premissas(self, orcamento_id: UUID) -> list[PremissaOrcamentoORM]:
        result = await self._db.execute(
            select(PremissaOrcamentoORM)
            .where(PremissaOrcamentoORM.orcamento_id == str(orcamento_id))
            .order_by(PremissaOrcamentoORM.ordem)
        )
        return list(result.scalars())

    async def criar_premissa(
        self, orcamento_id: UUID, premissa_id: UUID | None,
        nome: str, descricao: str | None, tipo: str, valor: float,
        valor_calculado: float, ordem: int, obrigatoria: bool = False,
    ) -> PremissaOrcamentoORM:
        orm = PremissaOrcamentoORM(
            id=str(uuid4()), orcamento_id=str(orcamento_id),
            premissa_id=str(premissa_id) if premissa_id else None,
            nome=nome, descricao=descricao, tipo=tipo, valor=valor,
            valor_calculado=valor_calculado, ordem=ordem,
            obrigatoria=obrigatoria,
        )
        self._db.add(orm)
        await self._db.flush()
        return orm

    async def deletar_premissas(self, orcamento_id: UUID) -> None:
        await self._db.execute(
            delete(PremissaOrcamentoORM).where(PremissaOrcamentoORM.orcamento_id == str(orcamento_id))
        )
        await self._db.flush()

    async def deletar_premissa(self, premissa_orc_id: UUID) -> None:
        await self._db.execute(
            delete(PremissaOrcamentoORM).where(PremissaOrcamentoORM.id == str(premissa_orc_id))
        )
        await self._db.flush()

    # ── Itens do orçamento ────────────────────────────────────────────────────

    async def listar_itens(self, orcamento_id: UUID) -> list[ItemOrcamentoORM]:
        result = await self._db.execute(
            select(ItemOrcamentoORM)
            .where(ItemOrcamentoORM.orcamento_id == str(orcamento_id))
            .order_by(ItemOrcamentoORM.ordem)
        )
        return list(result.scalars())

    async def criar_item(
        self, orcamento_id: UUID, tipo: str, descricao: str,
        item_estoque_id: UUID | None, quantidade: float | None,
        valor_unitario: float | None, valor_calculado: float, ordem: int,
    ) -> ItemOrcamentoORM:
        orm = ItemOrcamentoORM(
            id=str(uuid4()), orcamento_id=str(orcamento_id), tipo=tipo,
            descricao=descricao,
            item_estoque_id=str(item_estoque_id) if item_estoque_id else None,
            quantidade=quantidade, valor_unitario=valor_unitario,
            valor_calculado=valor_calculado, ordem=ordem,
        )
        self._db.add(orm)
        await self._db.flush()
        return orm

    async def deletar_itens(self, orcamento_id: UUID) -> None:
        await self._db.execute(
            delete(ItemOrcamentoORM).where(ItemOrcamentoORM.orcamento_id == str(orcamento_id))
        )
        await self._db.flush()

    async def buscar_item(self, item_id: UUID, empresa_id: UUID) -> ItemOrcamentoORM | None:
        result = await self._db.execute(
            select(ItemOrcamentoORM)
            .join(OrcamentoORM, OrcamentoORM.id == ItemOrcamentoORM.orcamento_id)
            .where(ItemOrcamentoORM.id == str(item_id), OrcamentoORM.empresa_id == str(empresa_id))
        )
        return result.scalar_one_or_none()

    async def deletar_item(self, item_id: UUID) -> None:
        await self._db.execute(
            delete(ItemOrcamentoORM).where(ItemOrcamentoORM.id == str(item_id))
        )
        await self._db.flush()
