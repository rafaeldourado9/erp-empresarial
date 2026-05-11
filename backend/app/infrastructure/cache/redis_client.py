"""
Infraestrutura de Cache Redis para o Catalog.

Contém:
  - FakeRedis       — implementação in-memory para testes (sem dependência de servidor).
  - RedisAdapter    — wrapper fino sobre redis.asyncio que expõe a mesma interface.
  - CardapioCacheService — serviço de cache com regras de TTL e serialização.

Chaves Redis utilizadas:
  cardapio:{est_id}      TTL 3600s  (1 hora)
  cardapio_pdf:{est_id}  TTL  900s  (15 minutos)
"""
from __future__ import annotations

import json
from decimal import Decimal
from typing import Any, Protocol, cast
from uuid import UUID

from app.catalog.domain.models import Produto

# ─────────────────────────────────────────────────────────────────────────────
# Protocol — interface mínima de Redis que o serviço precisa
# ─────────────────────────────────────────────────────────────────────────────

class IRedis(Protocol):
    async def get(self, key: str) -> str | bytes | None: ...
    async def set(self, key: str, value: str | bytes, ex: int | None = None) -> None: ...
    async def delete(self, *keys: str) -> None: ...


# ─────────────────────────────────────────────────────────────────────────────
# FakeRedis — para testes, sem servidor real
# ─────────────────────────────────────────────────────────────────────────────

class FakeRedis:
    """
    Redis in-memory para testes unitários.
    Expõe _store e _ttls para assertivas nos testes.
    """

    def __init__(self) -> None:
        self._store: dict[str, str | bytes] = {}
        self._ttls: dict[str, int] = {}

    async def get(self, key: str) -> str | bytes | None:
        return self._store.get(key)

    async def set(self, key: str, value: str | bytes, ex: int | None = None) -> None:
        self._store[key] = value
        if ex is not None:
            self._ttls[key] = ex

    async def delete(self, *keys: str) -> None:
        for key in keys:
            self._store.pop(key, None)
            self._ttls.pop(key, None)


# ─────────────────────────────────────────────────────────────────────────────
# RedisAdapter — wrapper sobre redis.asyncio para produção
# ─────────────────────────────────────────────────────────────────────────────

class RedisAdapter:
    """
    Adapta o cliente redis.asyncio para a interface IRedis.
    Instanciado a partir da URL via `from_url()`.
    """

    def __init__(self, client: Any) -> None:
        self._client = client

    @classmethod
    def from_url(cls, url: str) -> "RedisAdapter":
        import redis.asyncio as aioredis
        client = aioredis.from_url(url, decode_responses=False)  # type: ignore[no-untyped-call]
        return cls(client)

    async def get(self, key: str) -> str | bytes | None:
        return cast("str | bytes | None", await self._client.get(key))

    async def set(self, key: str, value: str | bytes, ex: int | None = None) -> None:
        await self._client.set(key, value, ex=ex)

    async def delete(self, *keys: str) -> None:
        if keys:
            await self._client.delete(*keys)


# ─────────────────────────────────────────────────────────────────────────────
# Serialização / Deserialização
# ─────────────────────────────────────────────────────────────────────────────

def _produto_para_dict(produto: Produto) -> dict[str, object]:
    """Converte Produto em dict serializável para JSON."""
    return {
        "id": str(produto.id),
        "estabelecimento_id": produto.estabelecimento_id,
        "categoria_id": str(produto.categoria_id),
        "nome": produto.nome,
        "descricao": produto.descricao,
        "preco_real": str(produto.preco_real),
        "preco_cardapio": str(produto.preco_cardapio),
        "disponivel": produto.disponivel,
        "imagem_url": produto.imagem_url,
        "created_at": produto.created_at.isoformat(),
    }


def _dict_para_produto(data: dict[str, object]) -> Produto:
    """Reconstrói um Produto a partir de um dict JSON."""
    from datetime import datetime

    return Produto(
        id=UUID(str(data["id"])),
        estabelecimento_id=str(data["estabelecimento_id"]),
        categoria_id=UUID(str(data["categoria_id"])),
        nome=str(data["nome"]),
        descricao=str(data["descricao"]),
        preco_real=Decimal(str(data["preco_real"])),
        preco_cardapio=Decimal(str(data["preco_cardapio"])),
        disponivel=bool(data["disponivel"]),
        grupos_adicionais=[],  # grupos não são cacheados — consultados separadamente se necessário
        imagem_url=str(data["imagem_url"]) if data.get("imagem_url") else None,
        created_at=datetime.fromisoformat(str(data["created_at"])),
    )


# ─────────────────────────────────────────────────────────────────────────────
# CardapioCacheService
# ─────────────────────────────────────────────────────────────────────────────

_TTL_CARDAPIO = 3600   # 1 hora
_TTL_PDF      = 900    # 15 minutos

_KEY_CARDAPIO = "cardapio:{}"
_KEY_PDF      = "cardapio_pdf:{}"


class CardapioCacheService:
    """
    Serviço de cache para o Catalog.

    Implementa a interface ICardapioCache (definida em handlers.py),
    podendo ser usado diretamente pelo CatalogoService em produção.
    """

    def __init__(self, redis: IRedis) -> None:
        self._redis = redis

    # ── cardápio ──────────────────────────────────────────

    async def get_cardapio(self, estabelecimento_id: str) -> list[Produto] | None:
        raw = await self._redis.get(_KEY_CARDAPIO.format(estabelecimento_id))
        if raw is None:
            return None
        data: list[dict[str, object]] = json.loads(raw)
        return [_dict_para_produto(d) for d in data]

    async def set_cardapio(self, estabelecimento_id: str, produtos: list[Produto]) -> None:
        payload = json.dumps([_produto_para_dict(p) for p in produtos])
        await self._redis.set(
            _KEY_CARDAPIO.format(estabelecimento_id),
            payload,
            ex=_TTL_CARDAPIO,
        )

    async def invalidar_cardapio(self, estabelecimento_id: str) -> None:
        await self._redis.delete(_KEY_CARDAPIO.format(estabelecimento_id))

    # ── PDF ───────────────────────────────────────────────

    async def get_pdf(self, estabelecimento_id: str) -> bytes | None:
        raw = await self._redis.get(_KEY_PDF.format(estabelecimento_id))
        if raw is None:
            return None
        return raw if isinstance(raw, bytes) else raw.encode()

    async def set_pdf(self, estabelecimento_id: str, dados: bytes) -> None:
        await self._redis.set(
            _KEY_PDF.format(estabelecimento_id),
            dados,
            ex=_TTL_PDF,
        )

    async def invalidar_pdf(self, estabelecimento_id: str) -> None:
        await self._redis.delete(_KEY_PDF.format(estabelecimento_id))
