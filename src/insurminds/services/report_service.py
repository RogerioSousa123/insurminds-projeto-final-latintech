from __future__ import annotations

import io
from html import escape

from insurminds.domain.models import ComparisonResult, PolicyAnalysis


def _shorten(value: str, limit: int) -> str:
    cleaned = " ".join(value.split())
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 1].rstrip() + "…"


def build_comparison_pdf(comparison: ComparisonResult, analyses: list[PolicyAnalysis]) -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            PageBreak,
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError as exc:
        raise RuntimeError("Instale reportlab para exportar o relatório PDF.") from exc

    output = io.BytesIO()
    page_size = landscape(A4)
    document = SimpleDocTemplate(
        output,
        pagesize=page_size,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="Relatório comparativo de apólices D&O",
        author="InsurMinds",
    )
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CenterTitle", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#12304A")))
    small = ParagraphStyle(name="SmallBody", parent=styles["BodyText"], fontSize=7.5, leading=9.5)
    note = ParagraphStyle(name="Note", parent=styles["BodyText"], fontSize=8, leading=10, textColor=colors.HexColor("#52616B"))
    story = [
        Paragraph("InsurMinds — Relatório Comparativo D&amp;O", styles["CenterTitle"]),
        Spacer(1, 5 * mm),
        Paragraph(f"Gerado em: {escape(comparison.created_at)}", note),
        Paragraph("Documentos: " + ", ".join(escape(item.document.filename) for item in analyses), note),
        Spacer(1, 5 * mm),
        Paragraph("Resumo executivo", styles["Heading2"]),
        Paragraph(escape(comparison.executive_summary).replace("\n", "<br/>"), styles["BodyText"]),
        Spacer(1, 4 * mm),
    ]

    header = [Paragraph("Critério", small)]
    header.extend(Paragraph(escape(item.document.filename), small) for item in analyses)
    header.extend([Paragraph("Atenção", small), Paragraph("Análise", small)])
    table_data = [header]
    for row in comparison.rows:
        values = []
        for cell in row.cells:
            value = _shorten(cell.value_text or cell.status.value.replace("_", " "), 480)
            pages = sorted({evidence.page for evidence in cell.evidences})
            if pages:
                page_list = ", ".join(str(page) for page in pages[:10])
                if len(pages) > 10:
                    page_list += ", …"
                value += "\n(p. " + page_list + ")"
            values.append(Paragraph(escape(value).replace("\n", "<br/>"), small))
        table_data.append(
            [
                Paragraph(escape(row.label), small),
                *values,
                Paragraph(row.attention.value.title(), small),
                Paragraph(escape(_shorten(row.explanation, 320)), small),
            ]
        )

    available_width = page_size[0] - 28 * mm
    policy_width = 47 * mm if len(analyses) == 2 else 38 * mm
    remaining = available_width - 43 * mm - len(analyses) * policy_width - 22 * mm
    col_widths = [43 * mm] + [policy_width] * len(analyses) + [22 * mm, max(remaining, 40 * mm)]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12304A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#B8C4CE")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6F8")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.extend([table, PageBreak(), Paragraph("Evidências", styles["Heading1"])])

    for row in comparison.rows:
        evidences_exist = any(cell.evidences for cell in row.cells)
        if not evidences_exist:
            continue
        story.append(Paragraph(escape(row.label), styles["Heading3"]))
        for cell in row.cells:
            for evidence in cell.evidences[:3]:
                story.append(
                    Paragraph(
                        f"<b>{escape(cell.filename)}, p. {evidence.page}:</b> "
                        f"{escape(_shorten(evidence.excerpt, 700))}",
                        small,
                    )
                )
                story.append(Spacer(1, 1.5 * mm))

    story.extend(
        [
            Spacer(1, 4 * mm),
            Paragraph("Limitações e ressalvas", styles["Heading2"]),
            *[Paragraph("• " + escape(caveat), note) for caveat in comparison.caveats],
        ]
    )

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor("#52616B"))
        canvas.drawString(14 * mm, 8 * mm, "InsurMinds — protótipo acadêmico; requer validação humana.")
        canvas.drawRightString(page_size[0] - 14 * mm, 8 * mm, f"Página {doc.page}")
        canvas.restoreState()

    document.build(story, onFirstPage=footer, onLaterPages=footer)
    return output.getvalue()
