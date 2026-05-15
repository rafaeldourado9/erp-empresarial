from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.audit.infrastructure.orm_models import RegistroAuditoriaORM


async def registrar_evento(
    db: AsyncSession,
    *,
    usuario_id: str | None,
    usuario_nome: str | None,
    empresa_id: str | None,
    grupo_id: str | None,
    acao: str,
    recurso: str,
    recurso_id: str | None = None,
    detalhes: str | None = None,
    ip: str | None = None,
) -> None:
    registro = RegistroAuditoriaORM(
        id=str(uuid4()),
        grupo_id=grupo_id,
        empresa_id=empresa_id,
        usuario_id=usuario_id,
        usuario_nome=usuario_nome,
        acao=acao,
        recurso=recurso,
        recurso_id=recurso_id,
        detalhes=detalhes,
        ip=ip,
        criado_em=datetime.now(UTC),
    )
    db.add(registro)
    # Sem flush explícito — participa da transação do endpoint
