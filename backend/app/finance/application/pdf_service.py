from __future__ import annotations

from datetime import date
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)


def _fmt(v: float) -> str:
    sign = "-" if v < 0 else ""
    return f"{sign}R$ {abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _periodo_str(inicio: date | None, fim: date | None) -> str:
    if inicio and fim:
        return f"{inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}"
    if inicio:
        return f"a partir de {inicio.strftime('%d/%m/%Y')}"
    if fim:
        return f"até {fim.strftime('%d/%m/%Y')}"
    return "todos os períodos"


def _doc(buf: BytesIO) -> SimpleDocTemplate:
    return SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )


def _styles():
    s = getSampleStyleSheet()
    return {
        "titulo": ParagraphStyle("t", parent=s["Heading1"], fontSize=17, spaceAfter=2),
        "sub": ParagraphStyle("sub", parent=s["Normal"], fontSize=10,
                              textColor=colors.HexColor("#6b7280"), spaceAfter=10),
        "secao": ParagraphStyle("sec", parent=s["Heading2"], fontSize=12,
                                spaceBefore=10, spaceAfter=5,
                                textColor=colors.HexColor("#1e40af")),
        "normal": s["Normal"],
    }


def _header(story: list, st: dict, empresa: str, titulo: str, subtitulo: str) -> None:
    story.append(Paragraph(f"{empresa} — {titulo}" if empresa else titulo, st["titulo"]))
    story.append(Paragraph(subtitulo, st["sub"]))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
    story.append(Spacer(1, 0.3 * cm))


# ── DRE ──────────────────────────────────────────────────────────────────────

def gerar_pdf_dre(dre, empresa_nome: str = "") -> bytes:
    buf = BytesIO()
    doc = _doc(buf)
    st = _styles()
    story = []
    _header(story, st, empresa_nome, "DRE — Demonstrativo de Resultado",
            f"Período: {_periodo_str(dre.periodo_inicio, dre.periodo_fim)}")

    rows = [["Conta", "Valor"]]
    for linha in dre.linhas:
        rows.append([linha.descricao, _fmt(float(linha.valor))])
    t = Table(rows, colWidths=[12 * cm, 5 * cm])
    estilos = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]
    for idx, linha in enumerate(dre.linhas, start=1):
        if linha.negrito:
            estilos.append(("FONTNAME", (0, idx), (-1, idx), "Helvetica-Bold"))
            estilos.append(("BACKGROUND", (0, idx), (-1, idx), colors.HexColor("#f3f4f6")))
    t.setStyle(TableStyle(estilos))
    story.append(t)
    doc.build(story)
    return buf.getvalue()


# ── Aging (recebíveis / pagáveis) ────────────────────────────────────────────

_FAIXAS = [
    ("Em dia", 0, 0),
    ("1-30 dias", 1, 30),
    ("31-60 dias", 31, 60),
    ("61-90 dias", 61, 90),
    ("> 90 dias", 91, 10_000),
]


def gerar_pdf_aging(contas: list, tipo: str, empresa_nome: str = "") -> bytes:
    """contas: lista de ContaORM com valor_pago/valor_restante calculados externamente."""
    buf = BytesIO()
    doc = _doc(buf)
    st = _styles()
    story = []
    label_tipo = "Recebíveis" if tipo == "receber" else "Pagáveis"
    _header(story, st, empresa_nome, f"Aging — {label_tipo}",
            f"Data base: {date.today().strftime('%d/%m/%Y')}  ·  {len(contas)} contas")

    hoje = date.today()
    buckets: dict[str, list] = {f[0]: [] for f in _FAIXAS}
    for c in contas:
        diff = (hoje - c.data_vencimento).days
        if diff <= 0:
            buckets["Em dia"].append(c)
        else:
            for label, lo, hi in _FAIXAS[1:]:
                if lo <= diff <= hi:
                    buckets[label].append(c)
                    break

    # Tabela de resumo
    resumo = [["Faixa", "Qtd", "Total restante"]]
    total_geral = 0.0
    for label, _, _ in _FAIXAS:
        items = buckets[label]
        soma = sum(float(getattr(c, "_restante", float(c.valor))) for c in items)
        total_geral += soma
        resumo.append([label, str(len(items)), _fmt(soma)])
    resumo.append(["TOTAL", str(sum(len(v) for v in buckets.values())), _fmt(total_geral)])
    t = Table(resumo, colWidths=[5 * cm, 3 * cm, 5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f3f4f6")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5 * cm))

    # Detalhamento
    story.append(Paragraph("Detalhamento", st["secao"]))
    det_rows = [["Faixa", "Vencimento", "Parceiro", "Descrição", "Restante"]]
    for label, _, _ in _FAIXAS:
        for c in buckets[label]:
            det_rows.append([
                label, c.data_vencimento.strftime("%d/%m/%Y"),
                (c.parceiro or "—")[:22],
                (c.descricao or "")[:28],
                _fmt(float(getattr(c, "_restante", float(c.valor)))),
            ])
    if len(det_rows) == 1:
        det_rows.append(["—", "—", "—", "—", "—"])
    det = Table(det_rows, colWidths=[2.5 * cm, 2.5 * cm, 4 * cm, 5 * cm, 3 * cm])
    det.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
        ("ALIGN", (4, 0), (4, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(det)
    doc.build(story)
    return buf.getvalue()


# ── Extrato genérico (filtrável por categoria/origem) ────────────────────────

def gerar_pdf_extrato(
    movimentos: list,
    inicio: date | None,
    fim: date | None,
    filtros: dict[str, str] | None = None,
    empresa_nome: str = "",
) -> bytes:
    buf = BytesIO()
    doc = _doc(buf)
    st = _styles()
    story = []

    subtitulo = f"Período: {_periodo_str(inicio, fim)}"
    if filtros:
        partes = [f"{k}: {v}" for k, v in filtros.items() if v]
        if partes:
            subtitulo += "  ·  " + "  ·  ".join(partes)

    _header(story, st, empresa_nome, "Extrato de Movimentos",
            f"{subtitulo}  ·  {len(movimentos)} lançamentos")

    rows = [["Data", "Tipo", "Categoria", "Origem", "Descrição", "Valor"]]
    entradas = saidas = 0.0
    for m in movimentos:
        v = float(m.valor)
        sinal = v if m.tipo == "entrada" else -v
        if m.tipo == "entrada":
            entradas += v
        else:
            saidas += v
        rows.append([
            m.data.strftime("%d/%m/%Y"),
            "ENT" if m.tipo == "entrada" else "SAI",
            (m.categoria or "")[:14],
            (m.origem or "manual")[:10],
            (m.descricao or "")[:34],
            _fmt(sinal),
        ])
    if len(rows) == 1:
        rows.append(["—"] * 6)
    t = Table(rows, colWidths=[2.2 * cm, 1.5 * cm, 2.8 * cm, 2.2 * cm, 6 * cm, 2.8 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
        ("ALIGN", (5, 0), (5, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4 * cm))

    totais_data = [
        ["Total entradas", _fmt(entradas)],
        ["Total saídas", _fmt(-saidas)],
        ["Saldo", _fmt(entradas - saidas)],
    ]
    tot = Table(totais_data, colWidths=[14 * cm, 4 * cm])
    tot.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#dbeafe")),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(tot)
    doc.build(story)
    return buf.getvalue()


# ── Auditoria filtrada ───────────────────────────────────────────────────────

def gerar_pdf_auditoria(
    registros: list,
    filtros: dict[str, str] | None = None,
    empresa_nome: str = "",
) -> bytes:
    buf = BytesIO()
    doc = _doc(buf)
    st = _styles()
    story = []

    subtitulo_partes = [f"{len(registros)} registros"]
    if filtros:
        subtitulo_partes += [f"{k}: {v}" for k, v in filtros.items() if v]
    _header(story, st, empresa_nome, "Auditoria — Registros Filtrados",
            "  ·  ".join(subtitulo_partes))

    rows = [["Data/Hora", "Usuário", "Ação", "Recurso", "Detalhes", "IP"]]
    for r in registros:
        rows.append([
            r.criado_em.strftime("%d/%m/%Y %H:%M"),
            (r.usuario_nome or "—")[:18],
            r.acao,
            (r.recurso or "")[:16] + (f" #{r.recurso_id[:6]}" if r.recurso_id else ""),
            (r.detalhes or "")[:32],
            (r.ip or "—")[:14],
        ])
    if len(rows) == 1:
        rows.append(["—"] * 6)
    t = Table(rows, colWidths=[3 * cm, 2.5 * cm, 1.7 * cm, 3.5 * cm, 5 * cm, 2 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3e8ff")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    doc.build(story)
    return buf.getvalue()
