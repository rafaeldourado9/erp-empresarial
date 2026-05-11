from __future__ import annotations

from datetime import date, UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.commissions.infrastructure.orm_models import ComissaoORM
from app.identity.api.deps import UsuarioAtualDep
from app.infrastructure.database import get_db

router = APIRouter(prefix="/comissoes", tags=["comissoes"])


class ComissaoResponse(BaseModel):
    id: UUID
    empresa_id: UUID
    orcamento_id: UUID | None
    orcamento_numero: str | None
    vendedor_id: UUID
    vendedor_nome: str | None
    valor_venda: float
    percentual: float
    valor_comissao: float
    status: str
    criado_em: datetime


class ResumoComissoesResponse(BaseModel):
    total_pendente: float
    total_pago: float
    vendedores_ativos: int


def _empresa_id(usuario: UsuarioAtualDep) -> UUID:
    from fastapi import HTTPException
    if usuario.empresa_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Selecione uma empresa")
    return usuario.empresa_id


def _to_response(c: ComissaoORM) -> ComissaoResponse:
    return ComissaoResponse(
        id=UUID(c.id),
        empresa_id=UUID(c.empresa_id),
        orcamento_id=UUID(c.orcamento_id) if c.orcamento_id else None,
        orcamento_numero=c.orcamento_numero,
        vendedor_id=UUID(c.vendedor_id),
        vendedor_nome=c.vendedor_nome,
        valor_venda=float(c.valor_venda),
        percentual=float(c.percentual),
        valor_comissao=float(c.valor_comissao),
        status=c.status,
        criado_em=c.criado_em,
    )


@router.get("", response_model=list[ComissaoResponse])
async def listar_comissoes(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    inicio: date | None = Query(None),
    fim: date | None = Query(None),
    status_filtro: str | None = Query(None, alias="status"),
) -> list[ComissaoResponse]:
    eid = str(_empresa_id(usuario))
    q = select(ComissaoORM).where(ComissaoORM.empresa_id == eid)
    if inicio:
        q = q.where(ComissaoORM.criado_em >= datetime(inicio.year, inicio.month, inicio.day, tzinfo=UTC))
    if fim:
        q = q.where(ComissaoORM.criado_em <= datetime(fim.year, fim.month, fim.day, 23, 59, 59, tzinfo=UTC))
    if status_filtro:
        q = q.where(ComissaoORM.status == status_filtro)
    result = await db.execute(q.order_by(ComissaoORM.criado_em.desc()))
    return [_to_response(c) for c in result.scalars()]


@router.get("/resumo", response_model=ResumoComissoesResponse)
async def resumo_comissoes(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    inicio: date | None = Query(None),
    fim: date | None = Query(None),
) -> ResumoComissoesResponse:
    eid = str(_empresa_id(usuario))
    q = select(ComissaoORM).where(ComissaoORM.empresa_id == eid)
    if inicio:
        q = q.where(ComissaoORM.criado_em >= datetime(inicio.year, inicio.month, inicio.day, tzinfo=UTC))
    if fim:
        q = q.where(ComissaoORM.criado_em <= datetime(fim.year, fim.month, fim.day, 23, 59, 59, tzinfo=UTC))
    result = await db.execute(q)
    comissoes = list(result.scalars())

    pendentes = [c for c in comissoes if c.status == "pendente"]
    pagos = [c for c in comissoes if c.status == "pago"]
    vendedores = {c.vendedor_id for c in comissoes if c.status != "cancelado"}

    return ResumoComissoesResponse(
        total_pendente=sum(float(c.valor_comissao) for c in pendentes),
        total_pago=sum(float(c.valor_comissao) for c in pagos),
        vendedores_ativos=len(vendedores),
    )


@router.patch("/{comissao_id}/pagar", status_code=status.HTTP_200_OK)
async def pagar_comissao(
    comissao_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ComissaoResponse:
    eid = str(_empresa_id(usuario))
    result = await db.execute(
        select(ComissaoORM).where(ComissaoORM.id == str(comissao_id), ComissaoORM.empresa_id == eid)
    )
    c = result.scalar_one_or_none()
    if c is None:
        from fastapi import HTTPException
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    c.status = "pago"
    return _to_response(c)
