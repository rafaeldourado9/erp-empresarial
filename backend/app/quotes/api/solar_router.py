from __future__ import annotations

import math
from typing import Any

from fastapi import APIRouter, Query

from app.quotes.data.solar_catalog import (
    INVERSORES,
    MODULOS,
    filtrar_inversores,
    filtrar_modulos,
    get_inversor,
    get_modulo,
)
from app.quotes.data.solar_states import ESTADOS_SOLARES, get_estado

router = APIRouter(prefix="/solar", tags=["solar"])

PERFORMANCE_RATIO = 0.75  # perdas do sistema (cabeamento, sujeira, temperatura…)


# ── Catálogo ────────────────────────────────────────────────────────────────

@router.get("/estados")
async def listar_estados() -> list[dict]:
    return ESTADOS_SOLARES  # type: ignore[return-value]


@router.get("/modulos")
async def listar_modulos(
    tipo: str | None = Query(None),
    potencia_min: int | None = Query(None),
    potencia_max: int | None = Query(None),
    q: str | None = Query(None, description="Busca livre por marca ou modelo"),
) -> list[dict]:
    resultado = filtrar_modulos(tipo=tipo, potencia_min=potencia_min, potencia_max=potencia_max)
    if q:
        termo = q.lower()
        resultado = [m for m in resultado if termo in m["marca"].lower() or termo in m["modelo"].lower()]
    return resultado  # type: ignore[return-value]


@router.get("/inversores")
async def listar_inversores(
    tipo: str | None = Query(None, description="string | micro | hibrido | off_grid | central"),
    potencia_min: float | None = Query(None),
    potencia_max: float | None = Query(None),
    fases: int | None = Query(None),
    q: str | None = Query(None, description="Busca livre por marca ou modelo"),
) -> list[dict]:
    resultado = filtrar_inversores(tipo=tipo, potencia_min=potencia_min, potencia_max=potencia_max, fases=fases)
    if q:
        termo = q.lower()
        resultado = [i for i in resultado if termo in i["marca"].lower() or termo in i["modelo"].lower()]
    return resultado  # type: ignore[return-value]


# ── Dimensionamento ──────────────────────────────────────────────────────────

@router.post("/dimensionar")
async def dimensionar(payload: dict[str, Any]) -> dict:
    """
    Retorna um dimensionamento solar completo.

    Payload aceita dois modos (podem coexistir):
    - Por consumo: { uf, consumo_mensal_kwh, modulo_id, inversor_id }
    - Por módulos:  { uf, modulo_id, qtd_modulos, inversor_id, qtd_inversores }

    Campos opcionais:
    - tipo_sistema: "on_grid" | "hibrido" | "off_grid"  (default "on_grid")
    - performance_ratio: float 0-1  (default 0.75)
    """
    uf: str = payload.get("uf", "SP")
    consumo_mensal: float | None = payload.get("consumo_mensal_kwh")
    modulo_id: str | None = payload.get("modulo_id")
    inversor_id: str | None = payload.get("inversor_id")
    qtd_modulos_manual: int | None = payload.get("qtd_modulos")
    qtd_inversores: int | None = payload.get("qtd_inversores", 1)
    tipo_sistema: str = payload.get("tipo_sistema", "on_grid")
    pr: float = float(payload.get("performance_ratio", PERFORMANCE_RATIO))

    estado = get_estado(uf)
    if not estado:
        estado = {"uf": uf, "nome": uf, "regiao": "-", "fator_geracao": 4.9, "irradiacao_media": 5.2}

    fator = estado["fator_geracao"]
    resultado: dict[str, Any] = {
        "uf": estado["uf"],
        "estado_nome": estado["nome"],
        "regiao": estado["regiao"],
        "fator_geracao_dia": fator,
        "performance_ratio": pr,
        "tipo_sistema": tipo_sistema,
    }

    modulo = get_modulo(modulo_id) if modulo_id else None
    inversor = get_inversor(inversor_id) if inversor_id else None

    # ── Modo 1: a partir do consumo mensal ──────────────────────────────────
    if consumo_mensal and consumo_mensal > 0:
        potencia_kwp_necessaria = consumo_mensal / (fator * 30 * pr)
        resultado["consumo_mensal_kwh"] = consumo_mensal
        resultado["potencia_kwp_necessaria"] = round(potencia_kwp_necessaria, 2)

        if modulo:
            qtd_calculados = math.ceil(potencia_kwp_necessaria * 1000 / modulo["potencia_wp"])
            resultado["qtd_modulos_sugerida"] = qtd_calculados
        else:
            resultado["qtd_modulos_sugerida"] = None

    # ── Modo 2: a partir de módulos informados ───────────────────────────────
    qtd_modulos = qtd_modulos_manual
    if modulo and qtd_modulos and qtd_modulos > 0:
        potencia_total_kwp = (modulo["potencia_wp"] * qtd_modulos) / 1000
        geracao_mensal = potencia_total_kwp * fator * 30 * pr
        resultado["potencia_total_kwp"] = round(potencia_total_kwp, 2)
        resultado["geracao_mensal_estimada_kwh"] = round(geracao_mensal, 1)
        resultado["geracao_anual_estimada_kwh"] = round(geracao_mensal * 12, 1)

        if consumo_mensal and consumo_mensal > 0:
            resultado["cobertura_percentual"] = round(min(geracao_mensal / consumo_mensal * 100, 100), 1)

    # ── Detalhes do módulo ───────────────────────────────────────────────────
    if modulo:
        resultado["modulo"] = {
            "id": modulo["id"],
            "marca": modulo["marca"],
            "modelo": modulo["modelo"],
            "potencia_wp": modulo["potencia_wp"],
            "eficiencia": modulo["eficiencia"],
            "tipo": modulo["tipo"],
        }

    # ── Detalhes do inversor + compatibilidade ───────────────────────────────
    if inversor:
        resultado["inversor"] = {
            "id": inversor["id"],
            "marca": inversor["marca"],
            "modelo": inversor["modelo"],
            "potencia_kw": inversor["potencia_kw"],
            "tipo": inversor["tipo"],
            "fases": inversor["fases"],
        }
        if qtd_inversores:
            potencia_inversores_kw = inversor["potencia_kw"] * qtd_inversores
            resultado["qtd_inversores"] = qtd_inversores
            resultado["potencia_inversores_total_kw"] = round(potencia_inversores_kw, 2)

            if modulo and qtd_modulos and qtd_modulos > 0:
                potencia_modulos_kw = (modulo["potencia_wp"] * qtd_modulos) / 1000
                ratio = potencia_modulos_kw / potencia_inversores_kw if potencia_inversores_kw > 0 else 0
                resultado["fator_dimensionamento"] = round(ratio, 3)
                if ratio > 1.35:
                    resultado["aviso_dimensionamento"] = "Sobrecarga CC > 35%: considere aumentar a potência dos inversores."
                elif ratio < 0.7:
                    resultado["aviso_dimensionamento"] = "Subaproveitamento: potência dos módulos menor que 70% do inversor."
                else:
                    resultado["aviso_dimensionamento"] = None

    return resultado


@router.get("/dimensionar/sugerir-inversor")
async def sugerir_inversor(
    potencia_kwp: float = Query(...),
    tipo: str = Query("string", description="string | micro | hibrido | off_grid"),
    fases: int = Query(3),
) -> list[dict]:
    """Sugere os inversores mais adequados para uma dada potência de pico."""
    alvo_kw = potencia_kwp * 1.1
    candidatos = filtrar_inversores(tipo=tipo, fases=fases)
    adequados = [i for i in candidatos if i["potencia_kw"] >= potencia_kwp * 0.7 and i["potencia_kw"] <= alvo_kw * 2]
    adequados.sort(key=lambda i: abs(i["potencia_kw"] - alvo_kw))
    return adequados[:6]  # type: ignore[return-value]
