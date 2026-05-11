from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.api.schemas import ClienteRequest, ClienteResponse
from app.clients.infrastructure.repository import ClienteRepository
from app.identity.api.deps import UsuarioAtualDep
from app.infrastructure.database import get_db

router = APIRouter(prefix="/clientes", tags=["clientes"])


def _empresa_id(usuario: UsuarioAtualDep) -> UUID:
    if usuario.empresa_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Selecione uma empresa")
    return usuario.empresa_id


@router.get("", response_model=list[ClienteResponse])
async def listar(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    busca: str | None = Query(None),
) -> list[ClienteResponse]:
    empresa_id = _empresa_id(usuario)
    clientes = await ClienteRepository(db).listar(empresa_id, busca)
    return [ClienteResponse(
        id=UUID(c.id), empresa_id=UUID(c.empresa_id), nome=c.nome,
        email=c.email, telefone=c.telefone, cpf_cnpj=c.cpf_cnpj,
        observacoes=c.observacoes, ativo=c.ativo,
    ) for c in clientes]


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def criar(
    body: ClienteRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ClienteResponse:
    empresa_id = _empresa_id(usuario)
    c = await ClienteRepository(db).criar(
        empresa_id=empresa_id, nome=body.nome, email=body.email,
        telefone=body.telefone, cpf_cnpj=body.cpf_cnpj, observacoes=body.observacoes,
    )
    return ClienteResponse(id=UUID(c.id), empresa_id=UUID(c.empresa_id), nome=c.nome, email=c.email, telefone=c.telefone, cpf_cnpj=c.cpf_cnpj, observacoes=c.observacoes, ativo=c.ativo)


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def atualizar(
    cliente_id: UUID,
    body: ClienteRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ClienteResponse:
    empresa_id = _empresa_id(usuario)
    repo = ClienteRepository(db)
    c = await repo.buscar_por_id(cliente_id, empresa_id)
    if c is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    c.nome = body.nome
    c.email = body.email
    c.telefone = body.telefone
    c.cpf_cnpj = body.cpf_cnpj
    c.observacoes = body.observacoes
    await repo.salvar(c)
    return ClienteResponse(id=UUID(c.id), empresa_id=UUID(c.empresa_id), nome=c.nome, email=c.email, telefone=c.telefone, cpf_cnpj=c.cpf_cnpj, observacoes=c.observacoes, ativo=c.ativo)


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar(
    cliente_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    empresa_id = _empresa_id(usuario)
    repo = ClienteRepository(db)
    c = await repo.buscar_por_id(cliente_id, empresa_id)
    if c is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    c.ativo = False
    await repo.salvar(c)
