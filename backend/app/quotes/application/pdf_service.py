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
_NAVY    = colors.HexColor("#0f2d52")
_GOLD    = colors.HexColor("#c8a84b")
_GRAY1   = colors.HexColor("#f1f5f9")   # fundo suave de linhas pares
_GRAY2   = colors.HexColor("#e2e8f0")   # grid / separadores
_GRAY3   = colors.HexColor("#94a3b8")   # texto secundário
_WHITE   = colors.white
_TEXT    = colors.HexColor("#1e293b")   # texto principal

A4_W = A4[0]   # 595.27 pt
A4_H = A4[1]   # 841.89 pt
_LM  = 1.8 * cm
_RM  = 1.8 * cm
_TM  = 2.0 * cm
_BM  = 2.2 * cm
_TW  = A4_W - _LM - _RM   # largura útil ≈ 17.0 cm


def _fmt(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _footer_cb(canvas, doc):
    """Rodapé em todas as páginas."""
    canvas.saveState()
    canvas.setFillColor(_NAVY)
    canvas.rect(_LM, 0.6 * cm, _TW, 0.04 * cm, fill=1, stroke=0)
    canvas.setFillColor(_GRAY3)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(_LM, 0.3 * cm, f"Documento gerado em {date.today().strftime('%d/%m/%Y')}")
    canvas.drawRightString(_LM + _TW, 0.3 * cm, f"Página {doc.page}")
    canvas.restoreState()


def _build_header_block(story, empresa_nome: str, doc_tipo: str, doc_subtitulo: str):
    """Bloco de cabeçalho azul-marinho com destaque dourado."""
    styles = getSampleStyleSheet()

    # Banner azul
    banner_data = [[
        Paragraph(
            f'<font color="white" size="15"><b>{empresa_nome or "ERP Empresarial"}</b></font>',
            ParagraphStyle("bh", parent=styles["Normal"], leading=18),
        ),
        Paragraph(
            f'<font color="#c8a84b" size="10"><b>{doc_tipo}</b></font><br/>'
            f'<font color="#cbd5e1" size="8">{doc_subtitulo}</font>',
            ParagraphStyle("bsub", parent=styles["Normal"], alignment=2, leading=14),
        ),
    ]]
    banner = Table(banner_data, colWidths=[_TW * 0.6, _TW * 0.4])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("PADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (0, 0), 14),
    ]))
    story.append(banner)

    # Linha dourada
    story.append(Table([[""]], colWidths=[_TW]))
    gold_line = Table([[""]], colWidths=[_TW])
    gold_line.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _GOLD),
        ("ROWHEIGHT", (0, 0), (-1, -1), 3),
        ("PADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(gold_line)
    story.append(Spacer(1, 0.35 * cm))


def _section_title(texto: str) -> Table:
    """Título de seção com fundo azul claro."""
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


# ── Orçamento ─────────────────────────────────────────────────────────────────

def gerar_pdf_orcamento(
    orc: object,
    premissas: list[object],
    itens: list[object],
    empresa_nome: str = "",
    cliente_nome: str = "",
    vendedor_nome: str = "",
) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=_LM, rightMargin=_RM,
        topMargin=_TM, bottomMargin=_BM,
    )
    story: list = []

    _build_header_block(
        story, empresa_nome,
        f"PROPOSTA COMERCIAL  Nº {orc.numero}",
        orc.titulo,
    )

    # Informações gerais — grade 2 colunas
    info_rows: list[list] = []
    pairs = [
        ("Cliente", cliente_nome or "—"),
        ("Vendedor", vendedor_nome or "—"),
        ("Validade", f"{orc.validade_dias} dias" if orc.validade_dias else "—"),
        ("Data", date.today().strftime("%d/%m/%Y")),
    ]
    if orc.email:    pairs.append(("E-mail", orc.email))
    if orc.telefone: pairs.append(("Telefone", orc.telefone))
    if orc.endereco: pairs.append(("Endereço", orc.endereco))
    if orc.cpf:      pairs.append(("CPF/CNPJ", orc.cpf))

    styles = getSampleStyleSheet()
    cell_lbl = ParagraphStyle("cl", parent=styles["Normal"], fontSize=8,
                               textColor=_GRAY3, fontName="Helvetica-Bold")
    cell_val = ParagraphStyle("cv", parent=styles["Normal"], fontSize=9, textColor=_TEXT)

    # Distribuir em 2 colunas
    for i in range(0, len(pairs), 2):
        row = []
        for k, v in pairs[i:i+2]:
            row.append(Paragraph(k, cell_lbl))
            row.append(Paragraph(str(v), cell_val))
        while len(row) < 4:
            row.extend([Paragraph("", cell_lbl), Paragraph("", cell_val)])
        info_rows.append(row)

    if info_rows:
        story.append(_section_title("INFORMAÇÕES DO CLIENTE"))
        story.append(Spacer(1, 0.15 * cm))
        t = Table(info_rows, colWidths=[2.2 * cm, 6.3 * cm, 2.2 * cm, 6.3 * cm])
        t.setStyle(TableStyle([
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.4, _GRAY2),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [_WHITE, _GRAY1]),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (0, -1), 8),
            ("LEFTPADDING", (2, 0), (2, -1), 8),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.4 * cm))

    # Premissas
    if premissas:
        story.append(_section_title("PREMISSAS DE PRECIFICAÇÃO"))
        story.append(Spacer(1, 0.15 * cm))
        hdr = ParagraphStyle("h", parent=styles["Normal"], fontSize=8,
                              textColor=_WHITE, fontName="Helvetica-Bold")
        rows = [[
            Paragraph("Premissa", hdr), Paragraph("Tipo", hdr),
            Paragraph("Valor", hdr),    Paragraph("Calculado", hdr),
        ]]
        for p in premissas:
            rows.append([
                p.nome,
                "Percentual" if p.tipo == "percentual" else "Fixo",
                f"{float(p.valor):.2f}%" if p.tipo == "percentual" else _fmt(float(p.valor)),
                _fmt(float(p.valor_calculado)),
            ])
        t = Table(rows, colWidths=[7.5 * cm, 3 * cm, 3 * cm, 3.5 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _NAVY),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.4, _GRAY2),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_WHITE, _GRAY1]),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (0, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.4 * cm))

    # Itens adicionais
    if itens:
        story.append(_section_title("ITENS DO ORÇAMENTO"))
        story.append(Spacer(1, 0.15 * cm))
        hdr = ParagraphStyle("h", parent=styles["Normal"], fontSize=8,
                              textColor=_WHITE, fontName="Helvetica-Bold")
        rows = [[
            Paragraph("Descrição", hdr), Paragraph("Qtd", hdr),
            Paragraph("Vlr Unit.", hdr), Paragraph("Total", hdr),
        ]]
        for i in itens:
            rows.append([
                i.descricao,
                f"{float(i.quantidade):.3f}" if i.quantidade else "—",
                _fmt(float(i.valor_unitario)) if i.valor_unitario else "—",
                _fmt(float(i.valor_calculado)),
            ])
        t = Table(rows, colWidths=[8.5 * cm, 2 * cm, 3.5 * cm, 3 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _NAVY),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.4, _GRAY2),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [_WHITE, _GRAY1]),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (0, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.4 * cm))

    # Totais
    story.append(_section_title("RESUMO FINANCEIRO"))
    story.append(Spacer(1, 0.15 * cm))
    tot_rows = [
        ["Custo base",                     _fmt(float(orc.custo_base))],
        ["Subtotal (premissas + itens)",   _fmt(float(orc.subtotal))],
    ]
    tot = Table(tot_rows, colWidths=[13.5 * cm, 3.5 * cm])
    tot.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TEXTCOLOR", (0, 0), (-1, -1), _GRAY3),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (0, -1), 8),
    ]))
    story.append(tot)
    story.append(Spacer(1, 0.2 * cm))

    pv = Table([["VALOR TOTAL DA PROPOSTA", _fmt(float(orc.valor_venda))]],
               colWidths=[13.5 * cm, 3.5 * cm])
    pv.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _NAVY),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TEXTCOLOR", (0, 0), (-1, -1), _WHITE),
        ("PADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (0, -1), 14),
    ]))
    story.append(pv)

    # Validade e observações
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=_GOLD))
    story.append(Spacer(1, 0.3 * cm))

    nota_style = ParagraphStyle("nota", parent=styles["Normal"], fontSize=8,
                                 textColor=_GRAY3, leading=12)
    if orc.validade_dias:
        story.append(Paragraph(
            f"Esta proposta é válida por <b>{orc.validade_dias} dias</b> a partir da data de emissão.",
            nota_style,
        ))
    if orc.observacoes:
        story.append(Spacer(1, 0.2 * cm))
        story.append(Paragraph(f"<b>Observações:</b> {orc.observacoes}", nota_style))

    doc.build(story, onFirstPage=_footer_cb, onLaterPages=_footer_cb)
    return buf.getvalue()
