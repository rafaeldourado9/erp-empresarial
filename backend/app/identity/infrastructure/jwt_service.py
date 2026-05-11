from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import cast
from uuid import UUID, uuid4

from jose import JWTError, jwt

from app.config import get_settings
from app.identity.domain.exceptions import TokenInvalidoError

ALGORITHM = "RS256"


def _private_key() -> str:
    return get_settings().get_private_key()


def _public_key() -> str:
    return get_settings().get_public_key()


def criar_access_token(
    usuario_id: UUID,
    grupo_id: UUID,
    empresa_id: UUID | None,
    perfil: str,
) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": str(usuario_id),
        "grupo": str(grupo_id),
        "empresa": str(empresa_id) if empresa_id else None,
        "perfil": perfil,
        "exp": expire,
        "iat": datetime.now(UTC),
        "jti": str(uuid4()),
        "type": "access",
    }
    return str(jwt.encode(payload, _private_key(), algorithm=ALGORITHM))


def criar_refresh_token(usuario_id: UUID) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days)
    payload = {
        "sub": str(usuario_id),
        "exp": expire,
        "iat": datetime.now(UTC),
        "jti": str(uuid4()),
        "type": "refresh",
    }
    return str(jwt.encode(payload, _private_key(), algorithm=ALGORITHM))


def decodificar_access_token(token: str) -> dict[str, object]:
    try:
        payload = jwt.decode(token, _public_key(), algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise TokenInvalidoError()
        return cast("dict[str, object]", payload)
    except JWTError as exc:
        raise TokenInvalidoError() from exc


def decodificar_refresh_token(token: str) -> dict[str, object]:
    try:
        payload = jwt.decode(token, _public_key(), algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise TokenInvalidoError()
        return cast("dict[str, object]", payload)
    except JWTError as exc:
        raise TokenInvalidoError() from exc
