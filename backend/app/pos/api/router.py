from __future__ import annotations

from datetime import UTC, date, datetime, time
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.api.deps import UsuarioAtualDep
from app.infrastructure.database import get_db
from app.pos.application.pdf_service import gerar_pdf_os, gerar_pdf_relatorio_os
from app.pos.infrastructure.orm_models import (
    ItemOSORM, OrdemServicoORM, ProdutoCaixaORM, SessaoCaixaORM,
)

router = APIRouter(prefix="/caixa", tags=["caixa"])


def _empresa_id(usuario: UsuarioAtualDep) -> UUID:
    if usuario.empresa_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Selecione uma empresa")
    return usuario.empresa_id


# ── Schemas ───────────────────────────────────────────────────────────────────

class AbrirSessaoRequest(BaseModel):
    saldo_inicial: float = 0.0


class SessaoResponse(BaseModel):
    id: UUID
    empresa_id: UUID
    operador_id: UUID
    saldo_inicial: float
    saldo_final: float | None
    aberta: bool
    aberto_em: datetime
    fechado_em: datetime | None


class ProdutoCaixaRequest(BaseModel):
    nome: str
    descricao: str | None = None
    valor: float
    unidade: str = "un"


class ProdutoCaixaResponse(BaseModel):
    id: UUID
    nome: str
    descricao: str | None
    valor: float
    unidade: str
    ativo: bool


class ItemOSRequest(BaseModel):
    produto_id: UUID | None = None   # se informado, puxa nome e valor do produto
    descricao: str | None = None     # obrigatório se produto_id for None
    quantidade: float = 1
    valor_unitario: float | None = None  # obrigatório se produto_id for None


class ItemOSResponse(BaseModel):
    id: UUID
    produto_id: UUID | None
    descricao: str
    quantidade: float
    valor_unitario: float
    valor_total: float


class CriarOSRequest(BaseModel):
    nome_cliente: str
    tipo_servico: str
    descricao_servico: str
    valor_servico: float = 0.0
    forma_pagamento: str
    desconto: float = 0.0
    observacoes: str | None = None
    itens: list[ItemOSRequest] = []


class OSResponse(BaseModel):
    id: UUID
    sessao_id: UUID
    empresa_id: UUID
    numero: str
    nome_cliente: str
    tipo_servico: str
    descricao_servico: str
    valor_servico: float
    valor_produtos: float
    desconto: float
    total: float
    forma_pagamento: str
    status: str
    observacoes: str | None
    criado_em: datetime
    concluido_em: datetime | None
    itens: list[ItemOSResponse] = []


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sessao_response(s: SessaoCaixaORM) -> SessaoResponse:
    return SessaoResponse(
        id=UUID(s.id), empresa_id=UUID(s.empresa_id), operador_id=UUID(s.operador_id),
        saldo_inicial=float(s.saldo_inicial),
        saldo_final=float(s.saldo_final) if s.saldo_final is not None else None,
        aberta=s.aberta, aberto_em=s.aberto_em, fechado_em=s.fechado_em,
    )


async def _os_to_response(os: OrdemServicoORM, db: AsyncSession) -> OSResponse:
    result = await db.execute(
        select(ItemOSORM).where(ItemOSORM.os_id == os.id).order_by(ItemOSORM.descricao)
    )
    itens = [
        ItemOSResponse(
            id=UUID(i.id),
            produto_id=UUID(i.produto_id) if i.produto_id else None,
            descricao=i.descricao,
            quantidade=float(i.quantidade),
            valor_unitario=float(i.valor_unitario),
            valor_total=float(i.valor_total),
        )
        for i in result.scalars()
    ]
    return OSResponse(
        id=UUID(os.id), sessao_id=UUID(os.sessao_id), empresa_id=UUID(os.empresa_id),
        numero=os.numero, nome_cliente=os.nome_cliente,
        tipo_servico=os.tipo_servico, descricao_servico=os.descricao_servico,
        valor_servico=float(os.valor_servico), valor_produtos=float(os.valor_produtos),
        desconto=float(os.desconto), total=float(os.total),
        forma_pagamento=os.forma_pagamento, status=os.status,
        observacoes=os.observacoes, criado_em=os.criado_em,
        concluido_em=os.concluido_em, itens=itens,
    )


async def _sessao_aberta(db: AsyncSession, empresa_id: UUID) -> SessaoCaixaORM:
    result = await db.execute(
        select(SessaoCaixaORM).where(
            SessaoCaixaORM.empresa_id == str(empresa_id),
            SessaoCaixaORM.aberta == True,
        ).limit(1)
    )
    sessao = result.scalar_one_or_none()
    if sessao is None:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Nenhum caixa aberto")
    return sessao


async def _proximo_numero_os(db: AsyncSession, empresa_id: UUID) -> str:
    result = await db.execute(
        select(func.count()).where(OrdemServicoORM.empresa_id == str(empresa_id))
    )
    count = result.scalar() or 0
    return f"OS-{count + 1:05d}"


# ── Sessão ────────────────────────────────────────────────────────────────────

@router.get("/sessao", response_model=SessaoResponse | None)
async def status_sessao(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SessaoResponse | None:
    result = await db.execute(
        select(SessaoCaixaORM).where(
            SessaoCaixaORM.empresa_id == str(_empresa_id(usuario)),
            SessaoCaixaORM.aberta == True,
        ).limit(1)
    )
    s = result.scalar_one_or_none()
    return _sessao_response(s) if s else None


@router.post("/sessao/abrir", response_model=SessaoResponse, status_code=status.HTTP_201_CREATED)
async def abrir_sessao(
    body: AbrirSessaoRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SessaoResponse:
    eid = str(_empresa_id(usuario))
    existing = await db.execute(
        select(SessaoCaixaORM).where(SessaoCaixaORM.empresa_id == eid, SessaoCaixaORM.aberta == True)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Já existe um caixa aberto")
    sessao = SessaoCaixaORM(
        id=str(uuid4()), empresa_id=eid, operador_id=str(usuario.id),
        saldo_inicial=body.saldo_inicial, aberta=True, aberto_em=datetime.now(UTC),
    )
    db.add(sessao)
    await db.flush()
    return _sessao_response(sessao)


@router.post("/sessao/fechar", response_model=SessaoResponse)
async def fechar_sessao(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SessaoResponse:
    sessao = await _sessao_aberta(db, _empresa_id(usuario))
    result = await db.execute(
        select(OrdemServicoORM).where(
            OrdemServicoORM.sessao_id == sessao.id,
            OrdemServicoORM.status == "concluida",
        )
    )
    total_os = sum(float(os.total) for os in result.scalars())
    sessao.aberta = False
    sessao.fechado_em = datetime.now(UTC)
    sessao.saldo_final = float(sessao.saldo_inicial) + total_os
    await db.flush()
    return _sessao_response(sessao)


# ── Produtos do Caixa ─────────────────────────────────────────────────────────

@router.get("/produtos", response_model=list[ProdutoCaixaResponse])
async def listar_produtos(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[ProdutoCaixaResponse]:
    result = await db.execute(
        select(ProdutoCaixaORM).where(
            ProdutoCaixaORM.empresa_id == str(_empresa_id(usuario)),
            ProdutoCaixaORM.ativo == True,
        ).order_by(ProdutoCaixaORM.nome)
    )
    return [
        ProdutoCaixaResponse(
            id=UUID(p.id), nome=p.nome, descricao=p.descricao,
            valor=float(p.valor), unidade=p.unidade, ativo=p.ativo,
        )
        for p in result.scalars()
    ]


@router.post("/produtos", response_model=ProdutoCaixaResponse, status_code=status.HTTP_201_CREATED)
async def criar_produto(
    body: ProdutoCaixaRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProdutoCaixaResponse:
    p = ProdutoCaixaORM(
        id=str(uuid4()), empresa_id=str(_empresa_id(usuario)),
        nome=body.nome, descricao=body.descricao,
        valor=body.valor, unidade=body.unidade, ativo=True,
    )
    db.add(p)
    await db.flush()
    return ProdutoCaixaResponse(id=UUID(p.id), nome=p.nome, descricao=p.descricao,
                                valor=float(p.valor), unidade=p.unidade, ativo=p.ativo)


@router.put("/produtos/{produto_id}", response_model=ProdutoCaixaResponse)
async def atualizar_produto(
    produto_id: UUID,
    body: ProdutoCaixaRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProdutoCaixaResponse:
    result = await db.execute(
        select(ProdutoCaixaORM).where(
            ProdutoCaixaORM.id == str(produto_id),
            ProdutoCaixaORM.empresa_id == str(_empresa_id(usuario)),
        )
    )
    p = result.scalar_one_or_none()
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    p.nome = body.nome
    p.descricao = body.descricao
    p.valor = body.valor
    p.unidade = body.unidade
    await db.flush()
    return ProdutoCaixaResponse(id=UUID(p.id), nome=p.nome, descricao=p.descricao,
                                valor=float(p.valor), unidade=p.unidade, ativo=p.ativo)


@router.delete("/produtos/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_produto(
    produto_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    result = await db.execute(
        select(ProdutoCaixaORM).where(
            ProdutoCaixaORM.id == str(produto_id),
            ProdutoCaixaORM.empresa_id == str(_empresa_id(usuario)),
        )
    )
    p = result.scalar_one_or_none()
    if p is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    p.ativo = False
    await db.flush()


# ── Ordens de Serviço ─────────────────────────────────────────────────────────

@router.get("/os", response_model=list[OSResponse])
async def listar_os(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    sessao_id: UUID | None = Query(None),
    status_filtro: str | None = Query(None, alias="status"),
) -> list[OSResponse]:
    eid = str(_empresa_id(usuario))
    q = select(OrdemServicoORM).where(OrdemServicoORM.empresa_id == eid)
    if sessao_id:
        q = q.where(OrdemServicoORM.sessao_id == str(sessao_id))
    if status_filtro:
        q = q.where(OrdemServicoORM.status == status_filtro)
    result = await db.execute(q.order_by(OrdemServicoORM.criado_em.desc()))
    return [await _os_to_response(os, db) for os in result.scalars()]


@router.post("/os", response_model=OSResponse, status_code=status.HTTP_201_CREATED)
async def criar_os(
    body: CriarOSRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OSResponse:
    empresa_id = _empresa_id(usuario)
    sessao = await _sessao_aberta(db, empresa_id)

    # Resolve itens
    itens_orm: list[tuple[str | None, str, float, float, float]] = []
    valor_produtos = 0.0
    for item_req in body.itens:
        if item_req.produto_id:
            result = await db.execute(
                select(ProdutoCaixaORM).where(
                    ProdutoCaixaORM.id == str(item_req.produto_id),
                    ProdutoCaixaORM.empresa_id == str(empresa_id),
                    ProdutoCaixaORM.ativo == True,
                )
            )
            produto = result.scalar_one_or_none()
            if produto is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Produto {item_req.produto_id} não encontrado")
            descricao = produto.nome
            valor_unit = float(produto.valor)
        else:
            if not item_req.descricao or item_req.valor_unitario is None:
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail="Informe produto_id ou (descricao, valor_unitario)")
            descricao = item_req.descricao
            valor_unit = item_req.valor_unitario

        valor_total = round(item_req.quantidade * valor_unit, 2)
        valor_produtos += valor_total
        itens_orm.append((
            str(item_req.produto_id) if item_req.produto_id else None,
            descricao, item_req.quantidade, valor_unit, valor_total,
        ))

    total = round(body.valor_servico + valor_produtos - body.desconto, 2)

    os = OrdemServicoORM(
        id=str(uuid4()), sessao_id=sessao.id, empresa_id=str(empresa_id),
        numero=await _proximo_numero_os(db, empresa_id),
        nome_cliente=body.nome_cliente,
        tipo_servico=body.tipo_servico,
        descricao_servico=body.descricao_servico,
        valor_servico=body.valor_servico,
        valor_produtos=valor_produtos,
        desconto=body.desconto,
        total=total,
        forma_pagamento=body.forma_pagamento,
        status="aberta",
        observacoes=body.observacoes,
        criado_em=datetime.now(UTC),
    )
    db.add(os)
    await db.flush()

    for pid, desc, qtd, valor_unit, valor_total in itens_orm:
        db.add(ItemOSORM(
            id=str(uuid4()), os_id=os.id, produto_id=pid,
            descricao=desc, quantidade=qtd,
            valor_unitario=valor_unit, valor_total=valor_total,
        ))
    await db.flush()

    return await _os_to_response(os, db)


@router.get("/os/{os_id}", response_model=OSResponse)
async def obter_os(
    os_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OSResponse:
    result = await db.execute(
        select(OrdemServicoORM).where(
            OrdemServicoORM.id == str(os_id),
            OrdemServicoORM.empresa_id == str(_empresa_id(usuario)),
        )
    )
    os = result.scalar_one_or_none()
    if os is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="OS não encontrada")
    return await _os_to_response(os, db)


@router.patch("/os/{os_id}/concluir", response_model=OSResponse)
async def concluir_os(
    os_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OSResponse:
    result = await db.execute(
        select(OrdemServicoORM).where(
            OrdemServicoORM.id == str(os_id),
            OrdemServicoORM.empresa_id == str(_empresa_id(usuario)),
        )
    )
    os = result.scalar_one_or_none()
    if os is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="OS não encontrada")
    if os.status == "concluida":
        return await _os_to_response(os, db)
    os.status = "concluida"
    os.concluido_em = datetime.now(UTC)
    await db.flush()

    # Auto-criar movimento de caixa com origem=caixa (Fase 4.A)
    from app.finance.infrastructure.orm_models import MovimentoCaixaORM
    from datetime import date as _date
    mov = MovimentoCaixaORM(
        id=str(uuid4()), empresa_id=os.empresa_id, tipo="entrada",
        categoria="Serviço",
        descricao=f"OS {os.numero} — {os.nome_cliente} ({os.forma_pagamento})",
        valor=float(os.total),
        data=_date.today(),
        orcamento_id=None,
        criado_por=str(usuario.id), criado_em=datetime.now(UTC),
        conciliado=False,
        origem="caixa",
    )
    db.add(mov)
    await db.flush()

    return await _os_to_response(os, db)


@router.patch("/os/{os_id}/cancelar", response_model=OSResponse)
async def cancelar_os(
    os_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OSResponse:
    result = await db.execute(
        select(OrdemServicoORM).where(
            OrdemServicoORM.id == str(os_id),
            OrdemServicoORM.empresa_id == str(_empresa_id(usuario)),
        )
    )
    os = result.scalar_one_or_none()
    if os is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="OS não encontrada")
    os.status = "cancelada"
    await db.flush()
    return await _os_to_response(os, db)


# ── PDFs ──────────────────────────────────────────────────────────────────────

async def _empresa_nome(db: AsyncSession, empresa_id: UUID) -> str:
    from app.identity.infrastructure.orm_models import EmpresaORM
    result = await db.execute(select(EmpresaORM).where(EmpresaORM.id == str(empresa_id)))
    emp = result.scalar_one_or_none()
    return emp.nome if emp else ""


@router.get("/os/relatorio/pdf")
async def relatorio_os_pdf(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    inicio: date | None = Query(None),
    fim: date | None = Query(None),
    status_filtro: str | None = Query(None, alias="status"),
) -> Response:
    """PDF resumo das OS no período. inicio/fim opcionais (sem filtro = todas)."""
    empresa_id = _empresa_id(usuario)
    q = select(OrdemServicoORM).where(OrdemServicoORM.empresa_id == str(empresa_id))
    if inicio:
        q = q.where(OrdemServicoORM.criado_em >= datetime.combine(inicio, time.min, tzinfo=UTC))
    if fim:
        q = q.where(OrdemServicoORM.criado_em <= datetime.combine(fim, time.max, tzinfo=UTC))
    if status_filtro:
        q = q.where(OrdemServicoORM.status == status_filtro)
    result = await db.execute(q.order_by(OrdemServicoORM.criado_em.asc()))
    ordens = list(result.scalars())

    pdf = gerar_pdf_relatorio_os(
        ordens=ordens, inicio=inicio, fim=fim, status_filtro=status_filtro,
        empresa_nome=await _empresa_nome(db, empresa_id),
    )
    sufixo = ""
    if inicio:
        sufixo += f"-{inicio.isoformat()}"
    if fim:
        sufixo += f"_{fim.isoformat()}"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="relatorio-os{sufixo}.pdf"'},
    )


@router.get("/os/{os_id}/pdf")
async def baixar_pdf_os(
    os_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    empresa_id = _empresa_id(usuario)
    result = await db.execute(
        select(OrdemServicoORM).where(
            OrdemServicoORM.id == str(os_id),
            OrdemServicoORM.empresa_id == str(empresa_id),
        )
    )
    os = result.scalar_one_or_none()
    if os is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="OS não encontrada")

    itens_result = await db.execute(
        select(ItemOSORM).where(ItemOSORM.os_id == os.id).order_by(ItemOSORM.descricao)
    )
    itens = list(itens_result.scalars())

    pdf = gerar_pdf_os(os, itens, empresa_nome=await _empresa_nome(db, empresa_id))
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="os-{os.numero}.pdf"'},
    )
