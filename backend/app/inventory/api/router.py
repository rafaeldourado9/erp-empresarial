from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.api.deps import UsuarioAtualDep
from app.identity.infrastructure.repository import EmpresaRepository
from app.infrastructure.database import get_db
from app.inventory.api.schemas import (
    AjusteEstoqueRequest, AlertaEstoqueResponse, BaixaEstoqueRequest,
    EntradaEstoqueRequest, ItemEstoqueRequest, ItemEstoqueResponse,
    MovimentoEstoqueResponse,
)
from app.inventory.application.pdf_service import gerar_relatorio_estoque
from app.inventory.infrastructure.repository import ItemEstoqueRepository, MovimentoEstoqueRepository

router = APIRouter(prefix="/estoque", tags=["estoque"])


def _empresa_id(usuario: UsuarioAtualDep) -> UUID:
    if usuario.empresa_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Selecione uma empresa")
    return usuario.empresa_id


def _to_response(o: object) -> ItemEstoqueResponse:
    qtd = float(o.quantidade)
    minimo = float(o.estoque_minimo) if o.estoque_minimo is not None else None
    return ItemEstoqueResponse(
        id=UUID(o.id), empresa_id=UUID(o.empresa_id), descricao=o.descricao,
        marca=o.marca, modelo=o.modelo, quantidade=qtd,
        estoque_minimo=minimo,
        valor_unitario=float(o.valor_unitario) if o.valor_unitario else None,
        valor_atribuido=float(o.valor_atribuido) if o.valor_atribuido else None,
        unidade=o.unidade, ativo=o.ativo,
        alerta_estoque_baixo=minimo is not None and qtd < minimo,
    )


def _to_movimento_response(m: object) -> MovimentoEstoqueResponse:
    return MovimentoEstoqueResponse(
        id=UUID(m.id), item_id=UUID(m.item_id), tipo=m.tipo,
        quantidade=float(m.quantidade),
        quantidade_anterior=float(m.quantidade_anterior),
        quantidade_posterior=float(m.quantidade_posterior),
        observacao=m.observacao, criado_por=UUID(m.criado_por),
        criado_em=m.criado_em,
    )


# ── CRUD básico ───────────────────────────────────────────────────────────────

@router.get("", response_model=list[ItemEstoqueResponse])
async def listar(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    busca: str | None = Query(None),
) -> list[ItemEstoqueResponse]:
    items = await ItemEstoqueRepository(db).listar(_empresa_id(usuario), busca)
    return [_to_response(i) for i in items]


@router.post("", response_model=ItemEstoqueResponse, status_code=status.HTTP_201_CREATED)
async def criar(
    body: ItemEstoqueRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ItemEstoqueResponse:
    i = await ItemEstoqueRepository(db).criar(
        empresa_id=_empresa_id(usuario), descricao=body.descricao, marca=body.marca,
        modelo=body.modelo, quantidade=body.quantidade, estoque_minimo=body.estoque_minimo,
        valor_unitario=body.valor_unitario, valor_atribuido=body.valor_atribuido,
        unidade=body.unidade,
    )
    return _to_response(i)


@router.put("/{item_id}", response_model=ItemEstoqueResponse)
async def atualizar(
    item_id: UUID,
    body: ItemEstoqueRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ItemEstoqueResponse:
    repo = ItemEstoqueRepository(db)
    i = await repo.buscar_por_id(item_id, _empresa_id(usuario))
    if i is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    i.descricao = body.descricao
    i.marca = body.marca
    i.modelo = body.modelo
    i.quantidade = body.quantidade
    i.estoque_minimo = body.estoque_minimo
    i.valor_unitario = body.valor_unitario
    i.valor_atribuido = body.valor_atribuido
    i.unidade = body.unidade
    await repo.salvar(i)
    return _to_response(i)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar(
    item_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    repo = ItemEstoqueRepository(db)
    i = await repo.buscar_por_id(item_id, _empresa_id(usuario))
    if i is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    i.ativo = False
    await repo.salvar(i)


# ── Movimentos ────────────────────────────────────────────────────────────────

@router.post("/{item_id}/baixa", response_model=ItemEstoqueResponse)
async def baixa(
    item_id: UUID,
    body: BaixaEstoqueRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ItemEstoqueResponse:
    if body.quantidade <= 0:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Quantidade deve ser positiva")
    repo = ItemEstoqueRepository(db)
    i = await repo.buscar_por_id(item_id, _empresa_id(usuario))
    if i is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    qtd_anterior = float(i.quantidade)
    nova_qtd = qtd_anterior - body.quantidade
    if nova_qtd < 0:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Estoque insuficiente. Disponível: {qtd_anterior:g} {i.unidade}")
    i.quantidade = nova_qtd
    await repo.salvar(i)
    await MovimentoEstoqueRepository(db).registrar(
        empresa_id=_empresa_id(usuario), item_id=item_id, criado_por=usuario.id,
        tipo="baixa", quantidade=body.quantidade,
        quantidade_anterior=qtd_anterior, quantidade_posterior=nova_qtd,
        observacao=body.observacao,
    )
    return _to_response(i)


@router.post("/{item_id}/entrada", response_model=ItemEstoqueResponse)
async def entrada(
    item_id: UUID,
    body: EntradaEstoqueRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ItemEstoqueResponse:
    if body.quantidade <= 0:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Quantidade deve ser positiva")
    repo = ItemEstoqueRepository(db)
    i = await repo.buscar_por_id(item_id, _empresa_id(usuario))
    if i is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    qtd_anterior = float(i.quantidade)
    nova_qtd = qtd_anterior + body.quantidade
    i.quantidade = nova_qtd
    await repo.salvar(i)
    await MovimentoEstoqueRepository(db).registrar(
        empresa_id=_empresa_id(usuario), item_id=item_id, criado_por=usuario.id,
        tipo="entrada", quantidade=body.quantidade,
        quantidade_anterior=qtd_anterior, quantidade_posterior=nova_qtd,
        observacao=body.observacao,
    )
    return _to_response(i)


@router.post("/{item_id}/ajuste", response_model=ItemEstoqueResponse)
async def ajuste(
    item_id: UUID,
    body: AjusteEstoqueRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ItemEstoqueResponse:
    if body.quantidade < 0:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Quantidade não pode ser negativa")
    repo = ItemEstoqueRepository(db)
    i = await repo.buscar_por_id(item_id, _empresa_id(usuario))
    if i is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    qtd_anterior = float(i.quantidade)
    i.quantidade = body.quantidade
    await repo.salvar(i)
    await MovimentoEstoqueRepository(db).registrar(
        empresa_id=_empresa_id(usuario), item_id=item_id, criado_por=usuario.id,
        tipo="ajuste", quantidade=abs(body.quantidade - qtd_anterior),
        quantidade_anterior=qtd_anterior, quantidade_posterior=body.quantidade,
        observacao=body.observacao,
    )
    return _to_response(i)


@router.get("/{item_id}/movimentos", response_model=list[MovimentoEstoqueResponse])
async def listar_movimentos(
    item_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[MovimentoEstoqueResponse]:
    repo = ItemEstoqueRepository(db)
    i = await repo.buscar_por_id(item_id, _empresa_id(usuario))
    if i is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Item não encontrado")
    movimentos = await MovimentoEstoqueRepository(db).listar_por_item(item_id, _empresa_id(usuario))
    return [_to_movimento_response(m) for m in movimentos]


# ── Alertas ───────────────────────────────────────────────────────────────────

@router.get("/alertas", response_model=list[AlertaEstoqueResponse])
async def alertas(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[AlertaEstoqueResponse]:
    itens = await ItemEstoqueRepository(db).listar_alertas(_empresa_id(usuario))
    return [
        AlertaEstoqueResponse(
            id=UUID(i.id), descricao=i.descricao, marca=i.marca, modelo=i.modelo,
            quantidade=float(i.quantidade), estoque_minimo=float(i.estoque_minimo),
            unidade=i.unidade, deficit=float(i.estoque_minimo) - float(i.quantidade),
        )
        for i in itens
    ]


# ── Relatório PDF ─────────────────────────────────────────────────────────────

@router.get("/relatorio.pdf")
async def relatorio_pdf(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Response:
    empresa_id = _empresa_id(usuario)
    empresa = await EmpresaRepository(db).buscar_por_id(empresa_id)
    empresa_nome = empresa.nome if empresa else "Empresa"
    cor_primaria = empresa.cor_primaria if empresa else "#2563eb"

    itens_orm = await ItemEstoqueRepository(db).listar(empresa_id)
    itens = []
    for i in itens_orm:
        qtd = float(i.quantidade)
        minimo = float(i.estoque_minimo) if i.estoque_minimo is not None else None
        itens.append({
            "descricao": i.descricao,
            "marca": i.marca,
            "modelo": i.modelo,
            "quantidade": qtd,
            "estoque_minimo": minimo,
            "valor_unitario": float(i.valor_unitario) if i.valor_unitario else None,
            "unidade": i.unidade,
            "alerta": minimo is not None and qtd < minimo,
        })

    pdf_bytes = gerar_relatorio_estoque(
        empresa_nome=empresa_nome,
        cor_primaria=cor_primaria,
        itens=itens,
        gerado_em=datetime.now(UTC),
    )

    nome_arquivo = f"estoque_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'},
    )
