from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.audit.infrastructure.orm_models import RegistroAuditoriaORM
from app.identity.api.deps import UsuarioAtualDep
from app.infrastructure.database import get_db

router = APIRouter(prefix="/auditoria", tags=["auditoria"])


class AuditoriaResponse(BaseModel):
    id: UUID
    empresa_id: UUID | None
    grupo_id: UUID | None
    usuario_id: UUID | None
    usuario_nome: str | None
    acao: str
    recurso: str
    recurso_id: str | None
    detalhes: str | None
    ip: str | None
    criado_em: datetime


def _to_response(r: RegistroAuditoriaORM) -> AuditoriaResponse:
    return AuditoriaResponse(
        id=UUID(r.id),
        empresa_id=UUID(r.empresa_id) if r.empresa_id else None,
        grupo_id=UUID(r.grupo_id) if r.grupo_id else None,
        usuario_id=UUID(r.usuario_id) if r.usuario_id else None,
        usuario_nome=r.usuario_nome,
        acao=r.acao,
        recurso=r.recurso,
        recurso_id=r.recurso_id,
        detalhes=r.detalhes,
        ip=r.ip,
        criado_em=r.criado_em,
    )


@router.get("", response_model=list[AuditoriaResponse])
async def listar_auditoria(
    usuario: UsuarioAtualDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    busca: str | None = Query(None),
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(50, le=200),
) -> list[AuditoriaResponse]:
    eid = str(usuario.empresa_id) if usuario.empresa_id else None
    gid = str(usuario.grupo_id)

    q = select(RegistroAuditoriaORM)
    if eid:
        q = q.where(RegistroAuditoriaORM.empresa_id == eid)
    else:
        q = q.where(RegistroAuditoriaORM.grupo_id == gid)

    if busca:
        pattern = f"%{busca}%"
        q = q.where(or_(
            RegistroAuditoriaORM.acao.ilike(pattern),
            RegistroAuditoriaORM.recurso.ilike(pattern),
            RegistroAuditoriaORM.usuario_nome.ilike(pattern),
            RegistroAuditoriaORM.detalhes.ilike(pattern),
        ))

    q = q.order_by(RegistroAuditoriaORM.criado_em.desc())
    q = q.offset((pagina - 1) * por_pagina).limit(por_pagina)
    result = await db.execute(q)
    return [_to_response(r) for r in result.scalars()]
