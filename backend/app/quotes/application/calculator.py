from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


def _d(v: float | None) -> Decimal:
    return Decimal(str(v)) if v is not None else Decimal("0")


def _q(v: Decimal) -> Decimal:
    return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass
class PremissaCalculo:
    id: str
    nome: str
    descricao: str | None
    tipo: str   # percentual | fixo
    valor: float
    ordem: int = 0


@dataclass
class ItemCalculo:
    id: str
    tipo: str   # manual | produto
    descricao: str
    quantidade: float | None
    valor_unitario: float | None
    ordem: int = 0


@dataclass
class ResultadoCalculo:
    custo_base: Decimal
    premissas: list[dict]
    itens: list[dict]
    subtotal_premissas: Decimal
    subtotal_itens: Decimal
    subtotal: Decimal       # custo_base + itens + premissas_fixas + premissas_percentuais
    valor_venda: Decimal    # = subtotal quando sem override manual


def calcular(
    custo_base: float,
    premissas: list[PremissaCalculo],
    itens: list[ItemCalculo],
    valor_venda_manual: float | None = None,
) -> ResultadoCalculo:
    """
    Cálculo de preço de venda por margem sobre o preço de venda (markup).

    Fórmula:
        custo_fixo   = custo_base + soma(itens) + soma(premissas tipo=fixo)
        soma_margens = soma(premissas tipo=percentual) / 100
        PV           = custo_fixo / (1 - soma_margens)   se PV não for informado manualmente
        valor_premissa_percentual = PV * percentual / 100
    """
    base = _d(custo_base)

    # ── Itens (custo fixo) ────────────────────────────────────────────────────
    itens_result: list[dict] = []
    soma_itens = Decimal("0")
    for item in sorted(itens, key=lambda x: x.ordem):
        if item.tipo == "produto" and item.quantidade is not None and item.valor_unitario is not None:
            valor_calc = _q(_d(item.quantidade) * _d(item.valor_unitario))
        elif item.tipo == "manual" and item.valor_unitario is not None:
            qtd = _d(item.quantidade) if item.quantidade else Decimal("1")
            valor_calc = _q(qtd * _d(item.valor_unitario))
        else:
            valor_calc = Decimal("0")
        soma_itens += valor_calc
        itens_result.append({
            "id": item.id,
            "tipo": item.tipo,
            "descricao": item.descricao,
            "quantidade": item.quantidade,
            "valor_unitario": item.valor_unitario,
            "valor_calculado": float(valor_calc),
            "ordem": item.ordem,
        })

    # ── Premissas fixas (também custo fixo) ───────────────────────────────────
    premissas_fixas = [p for p in premissas if p.tipo == "fixo"]
    premissas_pct   = [p for p in premissas if p.tipo == "percentual"]

    soma_fixas = sum((_q(_d(p.valor)) for p in premissas_fixas), Decimal("0"))

    # ── Custo total fixo e soma das margens ───────────────────────────────────
    custo_fixo = base + soma_itens + soma_fixas
    soma_pct = sum((_d(p.valor) for p in premissas_pct), Decimal("0")) / Decimal("100")

    # Proteção: se soma_pct >= 1, as margens consomem 100 %+ do PV — inválido
    if soma_pct >= Decimal("1"):
        soma_pct = Decimal("0.9999")

    # ── Preço de Venda ────────────────────────────────────────────────────────
    if valor_venda_manual is not None and valor_venda_manual > 0:
        pv = _d(valor_venda_manual)
    else:
        pv = _q(custo_fixo / (Decimal("1") - soma_pct))

    # ── Montar resultado das premissas ────────────────────────────────────────
    premissas_result: list[dict] = []
    soma_premissas = Decimal("0")

    todas = sorted(premissas, key=lambda x: x.ordem)
    for p in todas:
        if p.tipo == "percentual":
            valor_calc = _q(pv * _d(p.valor) / Decimal("100"))
        else:
            valor_calc = _q(_d(p.valor))
        soma_premissas += valor_calc
        premissas_result.append({
            "id": p.id,
            "nome": p.nome,
            "descricao": p.descricao,
            "tipo": p.tipo,
            "valor": p.valor,
            "valor_calculado": float(valor_calc),
            "ordem": p.ordem,
        })

    subtotal = base + soma_itens + soma_premissas

    return ResultadoCalculo(
        custo_base=base,
        premissas=premissas_result,
        itens=itens_result,
        subtotal_premissas=soma_premissas,
        subtotal_itens=soma_itens,
        subtotal=subtotal,
        valor_venda=pv,
    )
