from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.prospecting.infrastructure.orm_models import LeadORM
from app.identity.api.deps import UsuarioAtualDep
from app.infrastructure.database import get_db

router = APIRouter(prefix="/prospeccao", tags=["prospeccao"])

ETAPAS = ["Prospecção", "Qualificação", "Proposta", "Negociação", "Fechado", "Perdido"]


class LeadRequest(BaseModel):
    nome: str
    empresa: str | None = None
    contato: str | None = None
    etapa: str = "Prospecção"
    valor_estimado: float | None = None
    observacoes: str | None = None


class LeadResponse(BaseModel):
    id: UUID
    empresa_id: UUID
    nome: str
    empresa: str | None
    contato: str | None
    etapa: str
    valor_estimado: float | None
    observacoes: str | None
    criado_em: datetime
    atualizado_em: datetime


def _empresa_id(usuario: UsuarioAtualDep) -> UUID:
    from fastapi import HTTPException
    if usuario.empresa_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Selecione uma empresa")
    return usuario.empresa_id


def _to_response(l: LeadORM) -> LeadResponse:
    return LeadResponse(
        id=UUID(l.id), empresa_id=UUID(l.empresa_id),
        nome=l.nome, empresa=l.empresa_lead, contato=l.contato,
        etapa=l.etapa,
        valor_estimado=float(l.valor_estimado) if l.valor_estimado is not None else None,
        observacoes=l.observacoes,
        criado_em=l.criado_em, atualizado_em=l.atualizado_em,
    )


@router.get("", response_model=list[LeadResponse])
async def listar_leads(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    etapa: str | None = Query(None),
) -> list[LeadResponse]:
    eid = str(_empresa_id(usuario))
    q = select(LeadORM).where(LeadORM.empresa_id == eid)
    if etapa:
        q = q.where(LeadORM.etapa == etapa)
    result = await db.execute(q.order_by(LeadORM.atualizado_em.desc()))
    return [_to_response(l) for l in result.scalars()]


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def criar_lead(
    body: LeadRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LeadResponse:
    eid = str(_empresa_id(usuario))
    now = datetime.now(UTC)
    lead = LeadORM(
        id=str(uuid4()), empresa_id=eid, nome=body.nome,
        empresa_lead=body.empresa, contato=body.contato,
        etapa=body.etapa, valor_estimado=body.valor_estimado,
        observacoes=body.observacoes, criado_por=str(usuario.id),
        criado_em=now, atualizado_em=now,
    )
    db.add(lead)
    await db.flush()
    return _to_response(lead)


@router.put("/{lead_id}", response_model=LeadResponse)
async def atualizar_lead(
    lead_id: UUID,
    body: LeadRequest,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LeadResponse:
    eid = str(_empresa_id(usuario))
    result = await db.execute(select(LeadORM).where(LeadORM.id == str(lead_id), LeadORM.empresa_id == eid))
    lead = result.scalar_one_or_none()
    if lead is None:
        from fastapi import HTTPException
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    lead.nome = body.nome
    lead.empresa_lead = body.empresa
    lead.contato = body.contato
    lead.etapa = body.etapa
    lead.valor_estimado = body.valor_estimado
    lead.observacoes = body.observacoes
    lead.atualizado_em = datetime.now(UTC)
    return _to_response(lead)


@router.post("/{lead_id}/avancar", response_model=LeadResponse)
async def avancar_etapa(
    lead_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LeadResponse:
    eid = str(_empresa_id(usuario))
    result = await db.execute(select(LeadORM).where(LeadORM.id == str(lead_id), LeadORM.empresa_id == eid))
    lead = result.scalar_one_or_none()
    if lead is None:
        from fastapi import HTTPException
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    idx = ETAPAS.index(lead.etapa) if lead.etapa in ETAPAS else 0
    if idx < len(ETAPAS) - 1:
        lead.etapa = ETAPAS[idx + 1]
        lead.atualizado_em = datetime.now(UTC)
    return _to_response(lead)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar_lead(
    lead_id: UUID,
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    eid = str(_empresa_id(usuario))
    result = await db.execute(select(LeadORM).where(LeadORM.id == str(lead_id), LeadORM.empresa_id == eid))
    lead = result.scalar_one_or_none()
    if lead is not None:
        await db.delete(lead)
