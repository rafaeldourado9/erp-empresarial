from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.finance.infrastructure.orm_models import (
    CategoriaFinanceiroORM, ContaORM, MovimentoCaixaORM,
)
from app.identity.api.deps import UsuarioAtualDep
from app.infrastructure.database import get_db

router = APIRouter(prefix="/financeiro", tags=["financeiro"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _empresa_id(usuario: UsuarioAtualDep) -> UUID:
    if usuario.empresa_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Selecione uma empresa")
    return usuario.empresa_id


# ── Schemas ───────────────────────────────────────────────────────────────────

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


class DRELinha(BaseModel):
    descricao: str
    valor: float
    negrito: bool = False


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
    linhas: list[DRELinha] = []


class CategoriaRequest(BaseModel):
    nome: str
    tipo: str  # receita | custo | despesa
    cor: str = "#6b7280"


class CategoriaResponse(BaseModel):
    id: UUID
    nome: str
    tipo: str
    cor: str
    ativo: bool


class ContaRequest(BaseModel):
    tipo: str  # pagar | receber
    descricao: str
    parceiro: str | None = None
    valor: float
    data_vencimento: date
    orcamento_id: UUID | None = None
    cliente_id: UUID | None = None
    observacoes: str | None = None


class ContaResponse(BaseModel):
    id: UUID
    empresa_id: UUID
    tipo: str
    descricao: str
    parceiro: str | None
    valor: float
    data_vencimento: date
    data_pagamento: date | None
    status: str
    orcamento_id: UUID | None
    cliente_id: UUID | None
    observacoes: str | None
    criado_por: UUID
    criado_em: datetime


# ── Conversores ───────────────────────────────────────────────────────────────

def _to_movimento(m: MovimentoCaixaORM) -> MovimentoResponse:
    return MovimentoResponse(
        id=UUID(m.id), empresa_id=UUID(m.empresa_id), tipo=m.tipo,
        categoria=m.categoria, descricao=m.descricao, valor=float(m.valor),
        data=m.data, orcamento_id=UUID(m.orcamento_id) if m.orcamento_id else None,
        criado_por=UUID(m.criado_por), criado_em=m.criado_em, conciliado=m.conciliado,
    )


def _to_conta(c: ContaORM) -> ContaResponse:
    return ContaResponse(
        id=UUID(c.id), empresa_id=UUID(c.empresa_id), tipo=c.tipo,
        descricao=c.descricao, parceiro=c.parceiro, valor=float(c.valor),
        data_vencimento=c.data_vencimento, data_pagamento=c.data_pagamento,
        status=c.status,
        orcamento_id=UUID(c.orcamento_id) if c.orcamento_id else None,
        cliente_id=UUID(c.cliente_id) if c.cliente_id else None,
        observacoes=c.observacoes,
        criado_por=UUID(c.criado_por), criado_em=c.criado_em,
    )


# ── Movimentos ────────────────────────────────────────────────────────────────

@router.get("/movimentos", response_model=list[MovimentoResponse])
async def listar_movimentos(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    inicio: date | None = Query(None),
    fim: date | None = Query(None),
    tipo: str | None = Query(None),
    empresa_filtro: UUID | None = Query(None, alias="empresa_id"),
) -> list[MovimentoResponse]:
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
    return [_to_movimento(m) for m in result.scalars()]


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
    return _to_movimento(orm)


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
    custos = sum(float(m.valor) for m in movimentos if m.tipo == "saida" and m.categoria.lower() in ("custo", "produto", "material"))
    despesas = sum(float(m.valor) for m in movimentos if m.tipo == "saida" and m.categoria.lower() not in ("custo", "produto", "material"))
    lucro_bruto = receita - custos
    lucro_operacional = lucro_bruto - despesas

    linhas = [
        DRELinha(descricao="Receita Bruta", valor=receita),
        DRELinha(descricao="Custos Diretos", valor=-custos),
        DRELinha(descricao="Lucro Bruto", valor=lucro_bruto, negrito=True),
        DRELinha(descricao="Despesas Operacionais", valor=-despesas),
        DRELinha(descricao="Lucro Operacional", valor=lucro_operacional, negrito=True),
    ]

    return DREResponse(
        receita_bruta=receita, deducoes=0, receita_liquida=receita,
        custos=custos, lucro_bruto=lucro_bruto,
        despesas_operacionais=despesas, lucro_operacional=lucro_operacional,
        periodo_inicio=inicio, periodo_fim=fim,
        linhas=linhas,
    )


# ── Categorias ────────────────────────────────────────────────────────────────

_CATEGORIAS_PADRAO = [
    ("Venda", "receita", "#22c55e"),
    ("Serviço", "receita", "#16a34a"),
    ("Comissão", "despesa", "#f59e0b"),
    ("Aluguel", "despesa", "#8b5cf6"),
    ("Salário", "despesa", "#ef4444"),
    ("Fornecedor", "custo", "#f97316"),
    ("Imposto", "despesa", "#dc2626"),
    ("Outros", "despesa", "#6b7280"),
]


async def _garantir_categorias_padrao(db: AsyncSession, empresa_id: str) -> None:
    result = await db.execute(
        select(CategoriaFinanceiroORM).where(CategoriaFinanceiroORM.empresa_id == empresa_id)
    )
    if result.scalars().first() is None:
        for nome, tipo, cor in _CATEGORIAS_PADRAO:
            db.add(CategoriaFinanceiroORM(
                id=str(uuid4()), empresa_id=empresa_id, nome=nome,
                tipo=tipo, cor=cor, ativo=True, criado_em=datetime.now(UTC),
            ))
        await db.flush()


@router.get("/categorias", response_model=list[CategoriaResponse])
async def listar_categorias(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[CategoriaResponse]:
    eid = str(_empresa_id(usuario))
    await _garantir_categorias_padrao(db, eid)
    result = await db.execute(
        select(CategoriaFinanceiroORM)
        .where(CategoriaFinanceiroORM.empresa_id == eid, CategoriaFinanceiroORM.ativo == True)
        .order_by(CategoriaFinanceiroORM.nome)
    )
    return [CategoriaResponse(id=UUID(c.id), nome=c.nome, tipo=c.tipo, cor=c.cor, ativo=c.ativo)
            for c in result.scalars()]


@router.post("/categorias", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
async def criar_categoria(
    body: CategoriaRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> CategoriaResponse:
    eid = str(_empresa_id(usuario))
    orm = CategoriaFinanceiroORM(
        id=str(uuid4()), empresa_id=eid, nome=body.nome, tipo=body.tipo,
        cor=body.cor, ativo=True, criado_em=datetime.now(UTC),
    )
    db.add(orm)
    await db.flush()
    return CategoriaResponse(id=UUID(orm.id), nome=orm.nome, tipo=orm.tipo, cor=orm.cor, ativo=orm.ativo)


@router.delete("/categorias/{cat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_categoria(
    cat_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    eid = str(_empresa_id(usuario))
    result = await db.execute(
        select(CategoriaFinanceiroORM).where(
            CategoriaFinanceiroORM.id == str(cat_id),
            CategoriaFinanceiroORM.empresa_id == eid,
        )
    )
    cat = result.scalar_one_or_none()
    if cat is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    cat.ativo = False
    await db.flush()


# ── Contas a Pagar / Receber ──────────────────────────────────────────────────

@router.get("/contas", response_model=list[ContaResponse])
async def listar_contas(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    tipo: str | None = Query(None),
    status_filtro: str | None = Query(None, alias="status"),
    inicio: date | None = Query(None),
    fim: date | None = Query(None),
    vencendo_dias: int | None = Query(None),
) -> list[ContaResponse]:
    eid = str(_empresa_id(usuario))
    q = select(ContaORM).where(ContaORM.empresa_id == eid)
    if tipo:
        q = q.where(ContaORM.tipo == tipo)
    if status_filtro:
        q = q.where(ContaORM.status == status_filtro)
    if inicio:
        q = q.where(ContaORM.data_vencimento >= inicio)
    if fim:
        q = q.where(ContaORM.data_vencimento <= fim)
    if vencendo_dias is not None:
        hoje = date.today()
        limite = date.fromordinal(hoje.toordinal() + vencendo_dias)
        q = q.where(ContaORM.data_vencimento <= limite, ContaORM.status == "pendente")
    result = await db.execute(q.order_by(ContaORM.data_vencimento))
    return [_to_conta(c) for c in result.scalars()]


@router.post("/contas", response_model=ContaResponse, status_code=status.HTTP_201_CREATED)
async def criar_conta(
    body: ContaRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ContaResponse:
    eid = str(_empresa_id(usuario))
    orm = ContaORM(
        id=str(uuid4()), empresa_id=eid, tipo=body.tipo,
        descricao=body.descricao, parceiro=body.parceiro,
        valor=body.valor, data_vencimento=body.data_vencimento,
        status="pendente",
        orcamento_id=str(body.orcamento_id) if body.orcamento_id else None,
        cliente_id=str(body.cliente_id) if body.cliente_id else None,
        observacoes=body.observacoes,
        criado_por=str(usuario.id), criado_em=datetime.now(UTC),
    )
    db.add(orm)
    await db.flush()
    return _to_conta(orm)


@router.patch("/contas/{conta_id}/pagar", response_model=ContaResponse)
async def pagar_conta(
    conta_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    data_pagamento: date | None = Query(None),
) -> ContaResponse:
    eid = str(_empresa_id(usuario))
    result = await db.execute(
        select(ContaORM).where(ContaORM.id == str(conta_id), ContaORM.empresa_id == eid)
    )
    conta = result.scalar_one_or_none()
    if conta is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    conta.status = "pago"
    conta.data_pagamento = data_pagamento or date.today()
    await db.flush()
    return _to_conta(conta)


@router.patch("/contas/{conta_id}/cancelar", response_model=ContaResponse)
async def cancelar_conta(
    conta_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ContaResponse:
    eid = str(_empresa_id(usuario))
    result = await db.execute(
        select(ContaORM).where(ContaORM.id == str(conta_id), ContaORM.empresa_id == eid)
    )
    conta = result.scalar_one_or_none()
    if conta is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    conta.status = "cancelado"
    await db.flush()
    return _to_conta(conta)
