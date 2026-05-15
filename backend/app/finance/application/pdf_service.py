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

# ── Paleta corporativa ────────────────────────────────────────────────────────
_NAVY   = colors.HexColor("#0f2d52")
_GOLD   = colors.HexColor("#c8a84b")
_GRAY1  = colors.HexColor("#f1f5f9")
_GRAY2  = colors.HexColor("#e2e8f0")
_GRAY3  = colors.HexColor("#94a3b8")
_GREEN  = colors.HexColor("#166534")
_GBG    = colors.HexColor("#dcfce7")
_RED    = colors.HexColor("#991b1b")
_RBG    = colors.HexColor("#fee2e2")
_WHITE  = colors.white
_TEXT   = colors.HexColor("#1e293b")

A4_W, A4_H = A4
_LM = 1.8 * cm
_RM = 1.8 * cm
_TM = 2.0 * cm
_BM = 2.2 * cm
_TW = A4_W - _LM - _RM


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


def _footer_cb(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(_NAVY)
    canvas.rect(_LM, 0.6 * cm, _TW, 0.04 * cm, fill=1, stroke=0)
    canvas.setFillColor(_GRAY3)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(_LM, 0.3 * cm, f"Gerado em {date.today().strftime('%d/%m/%Y')}")
    canvas.drawRightString(_LM + _TW, 0.3 * cm, f"Página {doc.page}")
    canvas.restoreState()


def _doc(buf: BytesIO) -> SimpleDocTemplate:
    return SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=_LM, rightMargin=_RM,
        topMargin=_TM, bottomMargin=_BM,
    )


def _build_header(story: list, empresa: str, titulo: str, subtitulo: str) -> None:
    styles = getSampleStyleSheet()
    banner_data = [[
        Paragraph(
            f'<font color="white" size="14"><b>{empresa or "ERP Empresarial"}</b></font>',
            ParagraphStyle("bh", parent=styles["Normal"], leading=17),
        ),
        Paragraph(
            f'<font color="#c8a84b" size="10"><b>{titulo}</b></font><br/>'
            f'<font color="#cbd5e1" size="8">{subtitulo}</font>',
            ParagraphStyle("bsub", parent=styles["Normal"], alignment=2, leading=14),
        ),
    ]]
    banner = Table(banner_data, colWidths=[_TW * 0.58, _TW * 0.42])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (0, 0), 14),
    ]))
    story.append(banner)
    gold = Table([[""]], colWidths=[_TW])
    gold.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _GOLD),
        ("ROWHEIGHT", (0, 0), (-1, -1), 3),
        ("PADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(gold)
    story.append(Spacer(1, 0.35 * cm))


def _section(texto: str) -> Table:
    styles = getSampleStyleSheet()
    t = Table(
        [[Paragraph(f'<b><font color="#0f2d52">{texto}</font></b>',
                    ParagraphStyle("st", parent=styles["Normal"], fontSize=9))]],
        colWidths=[_TW],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#dbeafe")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (0, 0), 8),
    ]))
    return t


def _hdr_style() -> ParagraphStyle:
    return ParagraphStyle("h", parent=getSampleStyleSheet()["Normal"],
                          fontSize=8, textColor=_WHITE, fontName="Helvetica-Bold")


# ── DRE ──────────────────────────────────────────────────────────────────────

def gerar_pdf_dre(dre, empresa_nome: str = "") -> bytes:
    buf = BytesIO()
    doc = _doc(buf)
    story: list = []
    periodo = _periodo_str(dre.periodo_inicio, dre.periodo_fim)
    _build_header(story, empresa_nome, "DEMONSTRATIVO DE RESULTADO — DRE", periodo)

    story.append(_section("RESULTADO DO EXERCÍCIO"))
    story.append(Spacer(1, 0.15 * cm))

    hdr = _hdr_style()
    rows = [[Paragraph("Conta", hdr), Paragraph("Valor (R$)", hdr)]]
    styles = [
        ("BACKGROUND", (0, 0), (-1, 0), _NAVY),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, _GRAY2),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (0, -1), 10),
    ]
    for idx, linha in enumerate(dre.linhas, start=1):
        v = float(linha.valor)
        rows.append([linha.descricao, _fmt(v)])
        if linha.negrito:
            styles.append(("FONTNAME", (0, idx), (-1, idx), "Helvetica-Bold"))
            styles.append(("BACKGROUND", (0, idx), (-1, idx), _GRAY1))
        # Colorir saldo positivo/negativo na última linha bold
        if linha.negrito and v >= 0:
            styles.append(("TEXTCOLOR", (1, idx), (1, idx), _GREEN))
        elif linha.negrito and v < 0:
            styles.append(("TEXTCOLOR", (1, idx), (1, idx), _RED))

    t = Table(rows, colWidths=[13 * cm, 4 * cm])
    t.setStyle(TableStyle(styles))
    story.append(t)

    # Sumário visual
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=_GOLD))
    story.append(Spacer(1, 0.2 * cm))
    rb = float(dre.receita_bruta)
    lo = float(dre.lucro_operacional)
    sum_data = [
        ["Receita Bruta", _fmt(rb), "Lucro Operacional", _fmt(lo)],
    ]
    sum_t = Table(sum_data, colWidths=[_TW * 0.28, _TW * 0.22, _TW * 0.28, _TW * 0.22])
    text_c = _GREEN if lo >= 0 else _RED
    bg_c   = _GBG   if lo >= 0 else _RBG
    sum_t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("ALIGN", (3, 0), (3, -1), "RIGHT"),
        ("TEXTCOLOR", (3, 0), (3, -1), text_c),
        ("BACKGROUND", (2, 0), (3, -1), bg_c),
        ("GRID", (0, 0), (-1, -1), 0.4, _GRAY2),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (0, -1), 10),
    ]))
    story.append(sum_t)

    doc.build(story, onFirstPage=_footer_cb, onLaterPages=_footer_cb)
    return buf.getvalue()


# ── Aging ─────────────────────────────────────────────────────────────────────

_FAIXAS = [
    ("Em dia",      0,   0),
    ("1–30 dias",   1,  30),
    ("31–60 dias", 31,  60),
    ("61–90 dias", 61,  90),
    ("> 90 dias",  91, 10_000),
]

_FAIXA_CORES = [
    colors.HexColor("#dcfce7"),   # verde  — em dia
    colors.HexColor("#fef9c3"),   # amarelo — 1-30
    colors.HexColor("#ffedd5"),   # laranja — 31-60
    colors.HexColor("#fee2e2"),   # vermelho claro — 61-90
    colors.HexColor("#fecaca"),   # vermelho forte — >90
]


def gerar_pdf_aging(contas: list, tipo: str, empresa_nome: str = "") -> bytes:
    buf = BytesIO()
    doc = _doc(buf)
    story: list = []
    label_tipo = "CONTAS A RECEBER" if tipo == "receber" else "CONTAS A PAGAR"
    _build_header(
        story, empresa_nome,
        f"AGING — {label_tipo}",
        f"Data base: {date.today().strftime('%d/%m/%Y')}  ·  {len(contas)} contas",
    )

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

    # Resumo por faixa
    story.append(_section("RESUMO POR FAIXA DE VENCIMENTO"))
    story.append(Spacer(1, 0.15 * cm))
    hdr = _hdr_style()
    resumo = [[Paragraph(h, hdr) for h in ["Faixa", "Qtd", "Total Restante", "% do Total"]]]
    total_geral = sum(
        sum(float(getattr(c, "_restante", float(c.valor))) for c in itens)
        for itens in buckets.values()
    ) or 1.0
    estilos_res = [
        ("BACKGROUND", (0, 0), (-1, 0), _NAVY),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, _GRAY2),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (0, -1), 8),
    ]
    for i, (label, _, _) in enumerate(_FAIXAS):
        itens = buckets[label]
        soma = sum(float(getattr(c, "_restante", float(c.valor))) for c in itens)
        pct = soma / total_geral * 100
        resumo.append([label, str(len(itens)), _fmt(soma), f"{pct:.1f}%"])
        if itens:
            estilos_res.append(("BACKGROUND", (0, i + 1), (0, i + 1), _FAIXA_CORES[i]))
    # Linha total
    total_soma = sum(float(getattr(c, "_restante", float(c.valor))) for itens in buckets.values() for c in itens)
    resumo.append(["TOTAL", str(len(contas)), _fmt(total_soma), "100,0%"])
    estilos_res += [
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), _GRAY1),
    ]
    res_t = Table(resumo, colWidths=[4.5 * cm, 2.5 * cm, 5.5 * cm, 4.5 * cm])
    res_t.setStyle(TableStyle(estilos_res))
    story.append(res_t)
    story.append(Spacer(1, 0.5 * cm))

    # Detalhamento
    story.append(_section("DETALHAMENTO POR CONTA"))
    story.append(Spacer(1, 0.15 * cm))
    hdr = _hdr_style()
    det_rows = [[Paragraph(h, hdr) for h in ["Faixa", "Vencimento", "Parceiro", "Descrição", "Restante"]]]
    det_estilos = [
        ("BACKGROUND", (0, 0), (-1, 0), _NAVY),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, _GRAY2),
        ("ALIGN", (4, 0), (4, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (0, -1), 6),
    ]
    row_idx = 1
    for i, (label, _, _) in enumerate(_FAIXAS):
        for c in buckets[label]:
            det_rows.append([
                label,
                c.data_vencimento.strftime("%d/%m/%Y"),
                (c.parceiro or "—")[:20],
                (c.descricao or "")[:30],
                _fmt(float(getattr(c, "_restante", float(c.valor)))),
            ])
            det_estilos.append(("BACKGROUND", (0, row_idx), (0, row_idx), _FAIXA_CORES[i]))
            row_idx += 1

    if len(det_rows) == 1:
        det_rows.append(["Nenhuma conta encontrada", "", "", "", ""])
    det = Table(det_rows, colWidths=[2.8 * cm, 2.5 * cm, 3.8 * cm, 5.2 * cm, 2.7 * cm])
    det.setStyle(TableStyle(det_estilos))
    story.append(det)

    doc.build(story, onFirstPage=_footer_cb, onLaterPages=_footer_cb)
    return buf.getvalue()


# ── Extrato ───────────────────────────────────────────────────────────────────

def gerar_pdf_extrato(
    movimentos: list,
    inicio: date | None,
    fim: date | None,
    filtros: dict[str, str] | None = None,
    empresa_nome: str = "",
) -> bytes:
    buf = BytesIO()
    doc = _doc(buf)
    story: list = []

    subtitulo = _periodo_str(inicio, fim)
    if filtros:
        partes = [f"{k}: {v}" for k, v in filtros.items() if v]
        if partes:
            subtitulo += "  ·  " + "  ·  ".join(partes)

    _build_header(story, empresa_nome, "EXTRATO DE MOVIMENTAÇÕES",
                  f"{subtitulo}  ·  {len(movimentos)} lançamentos")

    story.append(_section("LANÇAMENTOS DO PERÍODO"))
    story.append(Spacer(1, 0.15 * cm))

    hdr = _hdr_style()
    rows = [[Paragraph(h, hdr) for h in ["Data", "Tipo", "Categoria", "Origem", "Descrição", "Valor"]]]
    estilos = [
        ("BACKGROUND", (0, 0), (-1, 0), _NAVY),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, _GRAY2),
        ("ALIGN", (5, 0), (5, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (0, -1), 6),
    ]
    entradas = saidas = 0.0
    for row_i, m in enumerate(movimentos, start=1):
        v = float(m.valor)
        is_entrada = m.tipo == "entrada"
        if is_entrada:
            entradas += v
        else:
            saidas += v
        sinal = v if is_entrada else -v
        rows.append([
            m.data.strftime("%d/%m/%Y"),
            "ENT" if is_entrada else "SAI",
            (m.categoria or "")[:14],
            (m.origem or "manual")[:10],
            (m.descricao or "")[:34],
            _fmt(sinal),
        ])
        estilos.append(("TEXTCOLOR", (5, row_i), (5, row_i), _GREEN if is_entrada else _RED))
        if row_i % 2 == 0:
            estilos.append(("BACKGROUND", (0, row_i), (-1, row_i), _GRAY1))

    if len(rows) == 1:
        rows.append(["Nenhum lançamento", "", "", "", "", ""])

    t = Table(rows, colWidths=[2.2 * cm, 1.4 * cm, 2.8 * cm, 2.2 * cm, 6.1 * cm, 2.3 * cm])
    t.setStyle(TableStyle(estilos))
    story.append(t)
    story.append(Spacer(1, 0.4 * cm))

    # Totalizadores
    saldo = entradas - saidas
    saldo_cor = _GREEN if saldo >= 0 else _RED
    saldo_bg  = _GBG   if saldo >= 0 else _RBG
    tot_data = [
        ["Total de Entradas", _fmt(entradas)],
        ["Total de Saídas",   _fmt(-saidas)],
        ["Saldo do Período",  _fmt(saldo)],
    ]
    tot = Table(tot_data, colWidths=[_TW - 4 * cm, 4 * cm])
    tot.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TEXTCOLOR", (1, 0), (1, 0), _GREEN),
        ("TEXTCOLOR", (1, 1), (1, 1), _RED),
        ("TEXTCOLOR", (1, 2), (1, 2), saldo_cor),
        ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
        ("BACKGROUND", (0, 2), (-1, 2), saldo_bg),
        ("GRID", (0, 0), (-1, -1), 0.4, _GRAY2),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (0, -1), 10),
    ]))
    story.append(tot)

    doc.build(story, onFirstPage=_footer_cb, onLaterPages=_footer_cb)
    return buf.getvalue()


# ── Auditoria ─────────────────────────────────────────────────────────────────

def gerar_pdf_auditoria(
    registros: list,
    filtros: dict[str, str] | None = None,
    empresa_nome: str = "",
) -> bytes:
    buf = BytesIO()
    doc = _doc(buf)
    story: list = []

    partes_sub = [f"{len(registros)} registros"]
    if filtros:
        partes_sub += [f"{k}: {v}" for k, v in filtros.items() if v]

    _build_header(story, empresa_nome, "REGISTROS DE AUDITORIA",
                  "  ·  ".join(partes_sub))

    story.append(_section("EVENTOS DO SISTEMA"))
    story.append(Spacer(1, 0.15 * cm))

    hdr = _hdr_style()
    rows = [[Paragraph(h, hdr) for h in ["Data/Hora", "Usuário", "Ação", "Recurso", "Detalhes", "IP"]]]
    estilos = [
        ("BACKGROUND", (0, 0), (-1, 0), _NAVY),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, _GRAY2),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (0, -1), 6),
    ]
    for row_i, r in enumerate(registros, start=1):
        rows.append([
            r.criado_em.strftime("%d/%m %H:%M"),
            (r.usuario_nome or "—")[:16],
            r.acao,
            ((r.recurso or "") + (f" #{r.recurso_id[:6]}" if r.recurso_id else ""))[:18],
            (r.detalhes or "")[:32],
            (r.ip or "—")[:14],
        ])
        if row_i % 2 == 0:
            estilos.append(("BACKGROUND", (0, row_i), (-1, row_i), _GRAY1))

    if len(rows) == 1:
        rows.append(["Nenhum registro", "", "", "", "", ""])

    t = Table(rows, colWidths=[2.5 * cm, 2.5 * cm, 1.8 * cm, 3.2 * cm, 5 * cm, 2 * cm])
    t.setStyle(TableStyle(estilos))
    story.append(t)

    doc.build(story, onFirstPage=_footer_cb, onLaterPages=_footer_cb)
    return buf.getvalue()
