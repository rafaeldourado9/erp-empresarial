from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)


def _hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return r / 255, g / 255, b / 255


def gerar_relatorio_estoque(
    empresa_nome: str,
    cor_primaria: str,
    itens: list[dict],
    gerado_em: datetime,
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
    )

    r, g, b = _hex_to_rgb(cor_primaria)
    brand = colors.Color(r, g, b)
    brand_light = colors.Color(r, g, b, alpha=0.12)
    alert_color = colors.HexColor("#dc2626")
    alert_light = colors.HexColor("#fef2f2")

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title", parent=styles["Normal"],
        fontSize=18, textColor=brand, spaceAfter=2 * mm, fontName="Helvetica-Bold",
    )
    sub_style = ParagraphStyle(
        "sub", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#6b7280"), spaceAfter=6 * mm,
    )
    cell_style = ParagraphStyle(
        "cell", parent=styles["Normal"], fontSize=8, leading=10,
    )

    elements = []

    elements.append(Paragraph(empresa_nome, title_style))
    elements.append(Paragraph(
        f"Relatório de Estoque — gerado em {gerado_em.strftime('%d/%m/%Y %H:%M')}",
        sub_style,
    ))

    # ── Resumo ────────────────────────────────────────────────────────────────
    total_itens = len(itens)
    itens_alerta = sum(1 for i in itens if i.get("alerta"))
    valor_total = sum(
        (i.get("quantidade", 0) * i.get("valor_unitario", 0))
        for i in itens if i.get("valor_unitario")
    )

    resumo_data = [
        ["Total de itens", "Itens em alerta", "Valor total em estoque"],
        [
            str(total_itens),
            str(itens_alerta),
            f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        ],
    ]
    resumo_table = Table(resumo_data, colWidths=[60 * mm, 60 * mm, 60 * mm])
    resumo_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), brand),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [brand_light, colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("TOPPADDING", (0, 0), (-1, -1), 4 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4 * mm),
        ("ROUNDEDCORNERS", [3, 3, 3, 3]),
    ]))
    elements.append(resumo_table)
    elements.append(Spacer(1, 6 * mm))

    # ── Tabela de itens ───────────────────────────────────────────────────────
    col_widths = [65 * mm, 22 * mm, 22 * mm, 22 * mm, 22 * mm, 22 * mm]
    header = ["Descrição / Marca", "Qtd", "Mín.", "Unidade", "Vlr. Unit.", "Situação"]
    table_data = [header]

    for item in itens:
        alerta = item.get("alerta", False)
        qtd = item.get("quantidade", 0)
        minimo = item.get("estoque_minimo")
        valor = item.get("valor_unitario")

        descricao = item.get("descricao", "")
        if item.get("marca"):
            descricao += f"\n{item['marca']}"
            if item.get("modelo"):
                descricao += f" — {item['modelo']}"

        table_data.append([
            Paragraph(descricao, cell_style),
            f"{qtd:g}",
            f"{minimo:g}" if minimo is not None else "—",
            item.get("unidade", "un"),
            f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if valor else "—",
            "⚠ BAIXO" if alerta else "OK",
        ])

    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    row_styles: list = [
        ("BACKGROUND", (0, 0), (-1, 0), brand),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
        ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
        ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
    ]

    for row_idx, item in enumerate(itens, start=1):
        if item.get("alerta"):
            row_styles.append(("BACKGROUND", (0, row_idx), (-1, row_idx), alert_light))
            row_styles.append(("TEXTCOLOR", (5, row_idx), (5, row_idx), alert_color))
            row_styles.append(("FONTNAME", (5, row_idx), (5, row_idx), "Helvetica-Bold"))
        elif row_idx % 2 == 0:
            row_styles.append(("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor("#f9fafb")))

    table.setStyle(TableStyle(row_styles))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
