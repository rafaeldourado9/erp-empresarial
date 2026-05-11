from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.identity.domain.constants import Permissao, PerfilUsuario
from app.identity.domain.exceptions import TokenInvalidoError
from app.identity.domain.models import Usuario
from app.identity.infrastructure import jwt_service
from app.identity.infrastructure.repository import UsuarioRepository
from app.infrastructure.database import get_db

_bearer = HTTPBearer(auto_error=False)


async def get_usuario_atual(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Usuario:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token não fornecido")
    try:
        payload = jwt_service.decodificar_access_token(credentials.credentials)
    except TokenInvalidoError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado")

    usuario = await UsuarioRepository(db).buscar_por_id(UUID(str(payload["sub"])))
    if usuario is None or not usuario.ativo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado ou inativo")
    return usuario


UsuarioAtualDep = Annotated[Usuario, Depends(get_usuario_atual)]


def requer_perfil(*perfis: PerfilUsuario):
    async def _check(usuario: UsuarioAtualDep) -> Usuario:
        if usuario.perfil not in perfis:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        return usuario
    return Depends(_check)


def requer_permissao(permissao: Permissao):
    async def _check(usuario: UsuarioAtualDep) -> Usuario:
        if not usuario.tem_permissao(permissao):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente")
        return usuario
    return Depends(_check)
