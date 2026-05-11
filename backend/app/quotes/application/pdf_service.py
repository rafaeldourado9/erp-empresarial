from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)


def _fmt(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


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
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle("titulo", parent=styles["Heading1"], fontSize=18, spaceAfter=4)
    subtitulo_style = ParagraphStyle("subtitulo", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#6b7280"), spaceAfter=12)
    secao_style = ParagraphStyle("secao", parent=styles["Heading2"], fontSize=11, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#1e40af"))
    normal = styles["Normal"]

    story = []

    # Header
    story.append(Paragraph(empresa_nome or "Orçamento", titulo_style))
    story.append(Paragraph(f"Nº {orc.numero}  ·  {orc.titulo}", subtitulo_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
    story.append(Spacer(1, 0.3 * cm))

    # Informações gerais
    info_data = [["Campo", "Valor"]]
    if cliente_nome:
        info_data.append(["Cliente", cliente_nome])
    if vendedor_nome:
        info_data.append(["Vendedor", vendedor_nome])
    if orc.validade_dias:
        info_data.append(["Validade", f"{orc.validade_dias} dias"])
    if orc.email:
        info_data.append(["E-mail", orc.email])
    if orc.telefone:
        info_data.append(["Telefone", orc.telefone])
    if orc.endereco:
        info_data.append(["Endereço", orc.endereco])

    if len(info_data) > 1:
        story.append(secao_style and Paragraph("Informações", secao_style))
        t = Table(info_data, colWidths=[4 * cm, 13 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5 * cm))

    # Premissas
    if premissas:
        story.append(Paragraph("Premissas", secao_style))
        rows = [["Premissa", "Tipo", "Valor", "Calculado"]]
        for p in premissas:
            rows.append([
                p.nome,
                "Percentual" if p.tipo == "percentual" else "Fixo",
                f"{float(p.valor):.2f}{'%' if p.tipo == 'percentual' else ' R$'}",
                _fmt(float(p.valor_calculado)),
            ])
        t = Table(rows, colWidths=[7 * cm, 3 * cm, 3 * cm, 4 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ede9fe")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f3ff")]),
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5 * cm))

    # Itens adicionais
    if itens:
        story.append(Paragraph("Itens Adicionais", secao_style))
        rows = [["Descrição", "Qtd", "Vlr Unit.", "Total"]]
        for i in itens:
            rows.append([
                i.descricao,
                f"{float(i.quantidade):.3f}" if i.quantidade else "—",
                _fmt(float(i.valor_unitario)) if i.valor_unitario else "—",
                _fmt(float(i.valor_calculado)),
            ])
        t = Table(rows, colWidths=[8 * cm, 2 * cm, 3.5 * cm, 3.5 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#fff7ed")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fffbeb")]),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5 * cm))

    # Totais
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
    story.append(Spacer(1, 0.3 * cm))

    totais_data = [
        ["Custo base", _fmt(float(orc.custo_base))],
        ["Subtotal (com premissas/itens)", _fmt(float(orc.subtotal))],
    ]
    totais = Table(totais_data, colWidths=[13 * cm, 4 * cm])
    totais.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#6b7280")),
        ("PADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(totais)

    story.append(Spacer(1, 0.2 * cm))
    pv_data = [["VALOR DE VENDA", _fmt(float(orc.valor_venda))]]
    pv = Table(pv_data, colWidths=[13 * cm, 4 * cm])
    pv.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#dbeafe")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1d4ed8")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#93c5fd")),
    ]))
    story.append(pv)

    # Observações
    if orc.observacoes:
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph("Observações", secao_style))
        story.append(Paragraph(orc.observacoes, normal))

    doc.build(story)
    return buf.getvalue()
