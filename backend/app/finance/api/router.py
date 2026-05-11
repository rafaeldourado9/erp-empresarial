from __future__ import annotations

from datetime import date
from typing import Annotated
from uuid import UUID, uuid4
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.infrastructure.orm_models import MovimentoCaixaORM
from app.identity.api.deps import UsuarioAtualDep
from app.infrastructure.database import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/financeiro", tags=["financeiro"])


class MovimentoRequest(BaseModel):
    tipo: str  # entrada | saida
    categoria: str
    descricao: str
    valor: float
    data: date
    orcamento_id: UUID | None = None


class MovimentoResponse(BaseModel):
    id: UUID
    empresa_id: UUID
    tipo: str
    categoria: str
    descricao: str
    valor: float
    data: date
    orcamento_id: UUID | None
    criado_por: UUID
    criado_em: datetime
    conciliado: bool


class ResumoFinanceiroResponse(BaseModel):
    total_entradas: float
    total_saidas: float
    saldo: float
    periodo_inicio: date
    periodo_fim: date


class DREResponse(BaseModel):
    receita_bruta: float
    deducoes: float
    receita_liquida: float
    custos: float
    lucro_bruto: float
    despesas_operacionais: float
    lucro_operacional: float
    periodo_inicio: date
    periodo_fim: date


def _empresa_id(usuario: UsuarioAtualDep) -> UUID:
    from fastapi import HTTPException
    if usuario.empresa_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Selecione uma empresa")
    return usuario.empresa_id


def _to_response(m: MovimentoCaixaORM) -> MovimentoResponse:
    return MovimentoResponse(
        id=UUID(m.id), empresa_id=UUID(m.empresa_id), tipo=m.tipo,
        categoria=m.categoria, descricao=m.descricao, valor=float(m.valor),
        data=m.data, orcamento_id=UUID(m.orcamento_id) if m.orcamento_id else None,
        criado_por=UUID(m.criado_por), criado_em=m.criado_em, conciliado=m.conciliado,
    )


@router.get("/movimentos", response_model=list[MovimentoResponse])
async def listar_movimentos(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    inicio: date | None = Query(None),
    fim: date | None = Query(None),
    tipo: str | None = Query(None),
    empresa_filtro: UUID | None = Query(None, alias="empresa_id"),
) -> list[MovimentoResponse]:
    # Admin grupo pode ver todas as empresas
    if usuario.perfil == "admin_grupo" and empresa_filtro:
        eid = str(empresa_filtro)
    else:
        eid = str(_empresa_id(usuario))

    query = select(MovimentoCaixaORM).where(MovimentoCaixaORM.empresa_id == eid)
    if inicio:
        query = query.where(MovimentoCaixaORM.data >= inicio)
    if fim:
        query = query.where(MovimentoCaixaORM.data <= fim)
    if tipo:
        query = query.where(MovimentoCaixaORM.tipo == tipo)
    result = await db.execute(query.order_by(MovimentoCaixaORM.data.desc()))
    return [_to_response(m) for m in result.scalars()]


@router.post("/movimentos", response_model=MovimentoResponse, status_code=status.HTTP_201_CREATED)
async def criar_movimento(
    body: MovimentoRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> MovimentoResponse:
    empresa_id = _empresa_id(usuario)
    orm = MovimentoCaixaORM(
        id=str(uuid4()), empresa_id=str(empresa_id), tipo=body.tipo,
        categoria=body.categoria, descricao=body.descricao, valor=body.valor,
        data=body.data,
        orcamento_id=str(body.orcamento_id) if body.orcamento_id else None,
        criado_por=str(usuario.id), criado_em=datetime.now(UTC), conciliado=False,
    )
    db.add(orm)
    await db.flush()
    return _to_response(orm)


@router.get("/resumo", response_model=ResumoFinanceiroResponse)
async def resumo(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    inicio: date = Query(...),
    fim: date = Query(...),
) -> ResumoFinanceiroResponse:
    eid = str(_empresa_id(usuario))
    q = select(MovimentoCaixaORM).where(
        MovimentoCaixaORM.empresa_id == eid,
        MovimentoCaixaORM.data >= inicio,
        MovimentoCaixaORM.data <= fim,
    )
    result = await db.execute(q)
    movimentos = list(result.scalars())
    entradas = sum(float(m.valor) for m in movimentos if m.tipo == "entrada")
    saidas = sum(float(m.valor) for m in movimentos if m.tipo == "saida")
    return ResumoFinanceiroResponse(
        total_entradas=entradas, total_saidas=saidas,
        saldo=entradas - saidas, periodo_inicio=inicio, periodo_fim=fim,
    )


@router.get("/dre", response_model=DREResponse)
async def dre(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    inicio: date = Query(...),
    fim: date = Query(...),
) -> DREResponse:
    eid = str(_empresa_id(usuario))
    result = await db.execute(
        select(MovimentoCaixaORM).where(
            MovimentoCaixaORM.empresa_id == eid,
            MovimentoCaixaORM.data >= inicio,
            MovimentoCaixaORM.data <= fim,
        )
    )
    movimentos = list(result.scalars())
    receita = sum(float(m.valor) for m in movimentos if m.tipo == "entrada")
    custos = sum(float(m.valor) for m in movimentos if m.tipo == "saida" and m.categoria in ("custo", "produto", "material"))
    despesas = sum(float(m.valor) for m in movimentos if m.tipo == "saida" and m.categoria not in ("custo", "produto", "material"))
    lucro_bruto = receita - custos
    lucro_operacional = lucro_bruto - despesas
    return DREResponse(
        receita_bruta=receita, deducoes=0, receita_liquida=receita,
        custos=custos, lucro_bruto=lucro_bruto,
        despesas_operacionais=despesas, lucro_operacional=lucro_operacional,
        periodo_inicio=inicio, periodo_fim=fim,
    )
