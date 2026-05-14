"""
Fatores de geração solar por estado brasileiro (kWh/kWp/dia).
Fonte: Atlas Solarimétrico do Brasil / CRESESB / INMET.
"""
from __future__ import annotations

from typing import TypedDict


class EstadoSolar(TypedDict):
    uf: str
    nome: str
    regiao: str
    fator_geracao: float   # kWh/kWp/dia (HSP média anual)
    irradiacao_media: float  # kWh/m²/dia


ESTADOS_SOLARES: list[EstadoSolar] = [
    {"uf": "AC", "nome": "Acre",                 "regiao": "Norte",         "fator_geracao": 4.50, "irradiacao_media": 4.80},
    {"uf": "AL", "nome": "Alagoas",              "regiao": "Nordeste",      "fator_geracao": 5.50, "irradiacao_media": 5.85},
    {"uf": "AP", "nome": "Amapá",                "regiao": "Norte",         "fator_geracao": 4.30, "irradiacao_media": 4.60},
    {"uf": "AM", "nome": "Amazonas",             "regiao": "Norte",         "fator_geracao": 4.40, "irradiacao_media": 4.70},
    {"uf": "BA", "nome": "Bahia",                "regiao": "Nordeste",      "fator_geracao": 5.60, "irradiacao_media": 5.95},
    {"uf": "CE", "nome": "Ceará",                "regiao": "Nordeste",      "fator_geracao": 5.70, "irradiacao_media": 6.05},
    {"uf": "DF", "nome": "Distrito Federal",     "regiao": "Centro-Oeste",  "fator_geracao": 5.50, "irradiacao_media": 5.80},
    {"uf": "ES", "nome": "Espírito Santo",       "regiao": "Sudeste",       "fator_geracao": 5.20, "irradiacao_media": 5.50},
    {"uf": "GO", "nome": "Goiás",                "regiao": "Centro-Oeste",  "fator_geracao": 5.50, "irradiacao_media": 5.80},
    {"uf": "MA", "nome": "Maranhão",             "regiao": "Nordeste",      "fator_geracao": 5.50, "irradiacao_media": 5.85},
    {"uf": "MT", "nome": "Mato Grosso",          "regiao": "Centro-Oeste",  "fator_geracao": 5.30, "irradiacao_media": 5.60},
    {"uf": "MS", "nome": "Mato Grosso do Sul",   "regiao": "Centro-Oeste",  "fator_geracao": 5.20, "irradiacao_media": 5.50},
    {"uf": "MG", "nome": "Minas Gerais",         "regiao": "Sudeste",       "fator_geracao": 5.40, "irradiacao_media": 5.70},
    {"uf": "PA", "nome": "Pará",                 "regiao": "Norte",         "fator_geracao": 4.80, "irradiacao_media": 5.10},
    {"uf": "PB", "nome": "Paraíba",              "regiao": "Nordeste",      "fator_geracao": 5.60, "irradiacao_media": 5.95},
    {"uf": "PR", "nome": "Paraná",               "regiao": "Sul",           "fator_geracao": 4.80, "irradiacao_media": 5.10},
    {"uf": "PE", "nome": "Pernambuco",           "regiao": "Nordeste",      "fator_geracao": 5.60, "irradiacao_media": 5.95},
    {"uf": "PI", "nome": "Piauí",                "regiao": "Nordeste",      "fator_geracao": 5.80, "irradiacao_media": 6.15},
    {"uf": "RJ", "nome": "Rio de Janeiro",       "regiao": "Sudeste",       "fator_geracao": 5.00, "irradiacao_media": 5.30},
    {"uf": "RN", "nome": "Rio Grande do Norte",  "regiao": "Nordeste",      "fator_geracao": 5.70, "irradiacao_media": 6.05},
    {"uf": "RS", "nome": "Rio Grande do Sul",    "regiao": "Sul",           "fator_geracao": 4.70, "irradiacao_media": 4.95},
    {"uf": "RO", "nome": "Rondônia",             "regiao": "Norte",         "fator_geracao": 4.70, "irradiacao_media": 5.00},
    {"uf": "RR", "nome": "Roraima",              "regiao": "Norte",         "fator_geracao": 4.50, "irradiacao_media": 4.80},
    {"uf": "SC", "nome": "Santa Catarina",       "regiao": "Sul",           "fator_geracao": 4.60, "irradiacao_media": 4.90},
    {"uf": "SP", "nome": "São Paulo",            "regiao": "Sudeste",       "fator_geracao": 4.90, "irradiacao_media": 5.20},
    {"uf": "SE", "nome": "Sergipe",              "regiao": "Nordeste",      "fator_geracao": 5.50, "irradiacao_media": 5.85},
    {"uf": "TO", "nome": "Tocantins",            "regiao": "Norte",         "fator_geracao": 5.40, "irradiacao_media": 5.70},
]

_BY_UF: dict[str, EstadoSolar] = {e["uf"]: e for e in ESTADOS_SOLARES}


def get_estado(uf: str) -> EstadoSolar | None:
    return _BY_UF.get(uf.upper())
