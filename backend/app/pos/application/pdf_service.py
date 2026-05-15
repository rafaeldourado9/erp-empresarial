from __future__ import annotations

from datetime import date, datetime
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


def _data_br(dt: datetime | None) -> str:
    if dt is None:
        return "—"
    return dt.strftime("%d/%m/%Y %H:%M")


_STATUS_LABEL = {
    "aberta": "Aberta",
    "concluida": "Concluída",
    "cancelada": "Cancelada",
}


# ── PDF de uma única OS ──────────────────────────────────────────────────────

def gerar_pdf_os(os, itens: list, empresa_nome: str = "") -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle("titulo", parent=styles["Heading1"], fontSize=18, spaceAfter=4)
    subtitulo_style = ParagraphStyle("subtitulo", parent=styles["Normal"], fontSize=10,
                                     textColor=colors.HexColor("#6b7280"), spaceAfter=12)
    secao_style = ParagraphStyle("secao", parent=styles["Heading2"], fontSize=11,
                                 spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#0e7490"))
    normal = styles["Normal"]

    story = []

    # Cabeçalho
    story.append(Paragraph(empresa_nome or "Ordem de Serviço", titulo_style))
    story.append(Paragraph(
        f"OS Nº {os.numero}  ·  {os.nome_cliente}  ·  {_STATUS_LABEL.get(os.status, os.status)}",
        subtitulo_style,
    ))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
    story.append(Spacer(1, 0.3 * cm))

    # Informações gerais
    info_data = [["Campo", "Valor"]]
    info_data.append(["Cliente", os.nome_cliente])
    info_data.append(["Tipo de serviço", os.tipo_servico])
    info_data.append(["Forma de pagamento", os.forma_pagamento])
    info_data.append(["Criada em", _data_br(os.criado_em)])
    if os.concluido_em:
        info_data.append(["Concluída em", _data_br(os.concluido_em)])

    story.append(Paragraph("Informações", secao_style))
    t = Table(info_data, colWidths=[5 * cm, 12 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4 * cm))

    # Descrição do serviço
    story.append(Paragraph("Descrição do Serviço", secao_style))
    story.append(Paragraph(os.descricao_servico or "—", normal))
    story.append(Spacer(1, 0.4 * cm))

    # Produtos / itens utilizados
    if itens:
        story.append(Paragraph("Produtos / Itens", secao_style))
        rows = [["Descrição", "Qtd", "Vlr Unit.", "Total"]]
        for i in itens:
            rows.append([
                i.descricao,
                f"{float(i.quantidade):.2f}".rstrip("0").rstrip(".") or "1",
                _fmt(float(i.valor_unitario)),
                _fmt(float(i.valor_total)),
            ])
        t = Table(rows, colWidths=[9 * cm, 2 * cm, 3 * cm, 3 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ecfdf5")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0fdf4")]),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.4 * cm))

    # Totais
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
    story.append(Spacer(1, 0.3 * cm))

    totais_data: list[list[str]] = [
        ["Valor do serviço", _fmt(float(os.valor_servico))],
        ["Valor dos produtos", _fmt(float(os.valor_produtos))],
    ]
    if float(os.desconto) > 0:
        totais_data.append(["Desconto", "- " + _fmt(float(os.desconto))])

    totais = Table(totais_data, colWidths=[13 * cm, 4 * cm])
    totais.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#6b7280")),
        ("PADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(totais)

    story.append(Spacer(1, 0.2 * cm))
    total_box = Table([["TOTAL", _fmt(float(os.total))]], colWidths=[13 * cm, 4 * cm])
    total_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#cffafe")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0e7490")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#67e8f9")),
    ]))
    story.append(total_box)

    # Observações
    if os.observacoes:
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph("Observações", secao_style))
        story.append(Paragraph(os.observacoes, normal))

    # Assinatura
    story.append(Spacer(1, 1.5 * cm))
    sig = Table(
        [["_" * 35, "_" * 35], ["Cliente", "Responsável"]],
        colWidths=[8.5 * cm, 8.5 * cm],
    )
    sig.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#6b7280")),
        ("TOPPADDING", (0, 1), (-1, 1), 2),
    ]))
    story.append(sig)

    doc.build(story)
    return buf.getvalue()


# ── PDF de relatório do período ──────────────────────────────────────────────

def gerar_pdf_relatorio_os(
    ordens: list,
    inicio: date | None,
    fim: date | None,
    status_filtro: str | None,
    empresa_nome: str = "",
) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle("titulo", parent=styles["Heading1"], fontSize=16, spaceAfter=2)
    subtitulo_style = ParagraphStyle("subtitulo", parent=styles["Normal"], fontSize=10,
                                     textColor=colors.HexColor("#6b7280"), spaceAfter=10)
    secao_style = ParagraphStyle("secao", parent=styles["Heading2"], fontSize=11,
                                 spaceBefore=10, spaceAfter=5, textColor=colors.HexColor("#0e7490"))

    story = []
    story.append(Paragraph(f"{empresa_nome or ''} — Relatório de Ordens de Serviço", titulo_style))
    desc_periodo = []
    if inicio:
        desc_periodo.append(f"de {inicio.strftime('%d/%m/%Y')}")
    if fim:
        desc_periodo.append(f"até {fim.strftime('%d/%m/%Y')}")
    if status_filtro:
        desc_periodo.append(f"status: {_STATUS_LABEL.get(status_filtro, status_filtro)}")
    desc_periodo.append(f"{len(ordens)} OS")
    story.append(Paragraph(" · ".join(desc_periodo), subtitulo_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
    story.append(Spacer(1, 0.3 * cm))

    if not ordens:
        story.append(Paragraph("Nenhuma OS encontrada no período.", styles["Normal"]))
        doc.build(story)
        return buf.getvalue()

    # Tabela detalhada
    rows = [["Nº", "Data", "Cliente", "Tipo", "Pgto", "Status", "Total"]]
    for os in ordens:
        rows.append([
            os.numero,
            os.criado_em.strftime("%d/%m/%Y") if os.criado_em else "—",
            (os.nome_cliente or "")[:24],
            (os.tipo_servico or "")[:18],
            (os.forma_pagamento or "")[:10],
            _STATUS_LABEL.get(os.status, os.status),
            _fmt(float(os.total)),
        ])

    tbl = Table(rows, colWidths=[2 * cm, 2 * cm, 4.5 * cm, 3.5 * cm, 2.2 * cm, 2.3 * cm, 2.5 * cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#cffafe")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e5e7eb")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
        ("ALIGN", (6, 0), (6, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.5 * cm))

    # Resumos
    story.append(Paragraph("Totais do período", secao_style))
    por_status: dict[str, float] = {}
    por_pgto: dict[str, float] = {}
    total_geral = 0.0
    for os in ordens:
        if os.status == "cancelada":
            por_status[os.status] = por_status.get(os.status, 0.0) + float(os.total)
            continue
        por_status[os.status] = por_status.get(os.status, 0.0) + float(os.total)
        por_pgto[os.forma_pagamento] = por_pgto.get(os.forma_pagamento, 0.0) + float(os.total)
        total_geral += float(os.total)

    status_rows = [["Status", "Total"]] + [
        [_STATUS_LABEL.get(s, s), _fmt(v)] for s, v in sorted(por_status.items())
    ]
    pgto_rows = [["Forma de pagamento", "Total"]] + [
        [k, _fmt(v)] for k, v in sorted(por_pgto.items(), key=lambda x: -x[1])
    ]

    def _resumo_table(data: list[list[str]]) -> Table:
        t = Table(data, colWidths=[5.5 * cm, 3 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("PADDING", (0, 0), (-1, -1), 4),
        ]))
        return t

    duas_colunas = Table(
        [[_resumo_table(status_rows), _resumo_table(pgto_rows)]],
        colWidths=[9 * cm, 9 * cm],
    )
    duas_colunas.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(duas_colunas)

    story.append(Spacer(1, 0.4 * cm))
    geral = Table([["TOTAL (excluindo canceladas)", _fmt(total_geral)]], colWidths=[14 * cm, 4 * cm])
    geral.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#cffafe")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0e7490")),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#67e8f9")),
    ]))
    story.append(geral)

    doc.build(story)
    return buf.getvalue()
