from __future__ import annotations

from dataclasses import dataclass

from app.identity.domain.exceptions import (
    CredenciaisInvalidasError,
    TokenInvalidoError,
    UsuarioInativoError,
    UsuarioNaoEncontradoError,
)
from app.identity.infrastructure import jwt_service
from app.identity.infrastructure.repository import UsuarioRepository


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthService:
    def __init__(self, usuario_repo: UsuarioRepository) -> None:
        self._repo = usuario_repo

    async def login(self, email: str, senha: str) -> TokenPair:
        usuario = await self._repo.buscar_por_email(email)
        if usuario is None or not usuario.verificar_senha(senha):
            raise CredenciaisInvalidasError("E-mail ou senha incorretos")
        if not usuario.ativo:
            raise UsuarioInativoError("Usuário inativo. Contate o administrador.")
        return self._emitir_tokens(usuario)

    async def refresh(self, refresh_token: str) -> TokenPair:
        try:
            payload = jwt_service.decodificar_refresh_token(refresh_token)
        except Exception as exc:
            raise TokenInvalidoError() from exc

        from uuid import UUID
        usuario = await self._repo.buscar_por_id(UUID(str(payload["sub"])))
        if usuario is None:
            raise UsuarioNaoEncontradoError()
        if not usuario.ativo:
            raise UsuarioInativoError()
        return self._emitir_tokens(usuario)

    def _emitir_tokens(self, usuario) -> TokenPair:  # type: ignore[no-untyped-def]
        access = jwt_service.criar_access_token(
            usuario_id=usuario.id,
            grupo_id=usuario.grupo_id,
            empresa_id=usuario.empresa_id,
            perfil=usuario.perfil.value,
        )
        refresh = jwt_service.criar_refresh_token(usuario_id=usuario.id)
        return TokenPair(access_token=access, refresh_token=refresh)
