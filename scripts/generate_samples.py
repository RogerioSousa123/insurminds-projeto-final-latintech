from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "examples"


def build_policy(path: Path, title: str, insurer: str, insured: str, policy_number: str, pages: list[list[tuple[str, str]]]):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="PolicyTitle", parent=styles["Title"], alignment=TA_CENTER, textColor=colors.HexColor("#12304A")))
    styles.add(ParagraphStyle(name="Clause", parent=styles["BodyText"], fontSize=9.5, leading=13, spaceAfter=5))
    doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=22 * mm, leftMargin=22 * mm, topMargin=18 * mm, bottomMargin=18 * mm)
    story = [
        Paragraph(title, styles["PolicyTitle"]),
        Paragraph("DOCUMENTO SINTÉTICO PARA DEMONSTRAÇÃO — SEM VALIDADE CONTRATUAL", styles["Heading3"]),
        Spacer(1, 4 * mm),
        Table(
            [
                ["Seguradora", insurer],
                ["Segurado/Tomador", insured],
                ["Apólice nº", policy_number],
            ],
            colWidths=[45 * mm, 105 * mm],
            style=TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C4CE")),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E7F0F7")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            ),
        ),
        Spacer(1, 6 * mm),
    ]
    for page_index, clauses in enumerate(pages):
        if page_index:
            story.append(PageBreak())
        story.append(Paragraph(f"Seção {page_index + 1}", styles["Heading1"]))
        for heading, body in clauses:
            story.append(Paragraph(heading, styles["Heading2"]))
            story.append(Paragraph(body, styles["Clause"]))
    doc.build(story)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    policy_a = [
        [
            ("1. Vigência e limite", "Vigência: das 00h de 01/01/2026 às 24h de 31/12/2026. Limite máximo de garantia: R$ 10.000.000,00, agregado para todas as coberturas."),
            ("2. Franquia", "Franquia geral / participação obrigatória do segurado: R$ 100.000,00 por reclamação."),
            ("3. Coberturas básicas", "Cobertura A: indenização aos administradores quando a companhia não puder indenizá-los. Cobertura B: reembolso à companhia por indenizações pagas aos administradores. Cobertura C: cobertura da entidade exclusivamente para reclamações de valores mobiliários."),
        ],
        [
            ("4. Custos de defesa", "Os custos de defesa estão cobertos e integram, consumindo, o limite máximo de garantia. A escolha de advogado depende de aprovação prévia da seguradora."),
            ("5. Reclamações trabalhistas", "Reclamações por práticas trabalhistas estão cobertas até o sublimite de R$ 1.000.000,00, observadas as exclusões contratuais."),
            ("6. Investigações", "Despesas de representação em investigação formal estão cobertas a partir da notificação escrita ao administrador."),
            ("7. Multas", "Multas civis e administrativas são cobertas somente quando legalmente seguráveis, até o sublimite de R$ 500.000,00."),
        ],
        [
            ("8. Temporalidade", "Data de retroatividade: 01/01/2020. Prazo complementar: 12 meses, sem cobrança adicional. Prazo suplementar: 24 meses, mediante prêmio adicional."),
            ("9. Território e jurisdição", "Âmbito territorial mundial, exceto países sujeitos a sanções. Jurisdição mundial, excluídos Estados Unidos e Canadá."),
            ("10. Exclusões", "Ficam excluídos atos dolosos, fraude ou vantagem pessoal indevida após decisão final irrecorrível. A exclusão segurado contra segurado não se aplica a reclamações derivativas independentes. Fatos e processos anteriores conhecidos antes do início da vigência estão excluídos."),
            ("11. Mudança de controle", "Em caso de mudança de controle, a cobertura permanece apenas para atos praticados antes da operação. O segurado deverá comunicar a seguradora em até 30 dias."),
            ("12. Cancelamento", "O cancelamento por falta de pagamento observará notificação prévia de 30 dias."),
        ],
    ]
    policy_b = [
        [
            ("1. Vigência e limite", "Vigência: das 00h de 01/01/2026 às 24h de 31/12/2026. Limite máximo de garantia: R$ 15.000.000,00, agregado para todas as coberturas."),
            ("2. Franquia", "Franquia geral / participação obrigatória do segurado: R$ 250.000,00 por reclamação."),
            ("3. Coberturas básicas", "Cobertura A: proteção aos administradores por perdas não indenizadas pela companhia. Cobertura B: reembolso à companhia. Cobertura C: reclamações de valores mobiliários apresentadas contra a entidade."),
        ],
        [
            ("4. Custos de defesa", "Os custos de defesa estão cobertos dentro do limite máximo de garantia e reduzem o saldo disponível para indenização. Advogados do painel da seguradora independem de autorização adicional."),
            ("5. Reclamações trabalhistas", "Ficam excluídas reclamações decorrentes de práticas trabalhistas apresentadas contra a entidade. Administradores permanecem cobertos quando nomeados individualmente, sujeitos à franquia."),
            ("6. Investigações", "Investigações formais possuem sublimite de R$ 2.000.000,00. Entrevistas voluntárias e investigações internas não estão incluídas."),
            ("7. Multas", "Multas, penalidades e tributos estão excluídos, ainda que aplicados em processo administrativo."),
        ],
        [
            ("8. Temporalidade", "Data de retroatividade: 01/01/2022. Prazo complementar: 36 meses, sem prêmio adicional. Não há prazo suplementar previsto."),
            ("9. Território e jurisdição", "Âmbito territorial: Brasil. Âmbito de jurisdição: tribunais brasileiros e aplicação das leis brasileiras."),
            ("10. Exclusões", "Atos dolosos, fraudulentos ou criminosos ficam excluídos após confissão ou decisão judicial, aplicando-se a separabilidade entre segurados. Reclamações de segurado contra segurado estão excluídas, exceto ações trabalhistas de ex-administradores. Processos pendentes anteriores a 01/01/2022 estão excluídos."),
            ("11. Mudança de controle", "Mudança de controle encerra a cobertura para atos futuros imediatamente. Poderá ser contratado período de descoberta mediante negociação."),
            ("12. Cancelamento", "A seguradora poderá cancelar por falta de pagamento mediante notificação prévia de 15 dias."),
        ],
    ]
    build_policy(OUTPUT / "Apolice_Demo_A.pdf", "APÓLICE D&O DEMONSTRAÇÃO A", "Aegis Seguros S.A.", "Empresa Alpha S.A.", "IM-A-2026-001", policy_a)
    build_policy(OUTPUT / "Apolice_Demo_B.pdf", "APÓLICE D&O DEMONSTRAÇÃO B", "Boreal Companhia de Seguros", "Empresa Alpha S.A.", "IM-B-2026-002", policy_b)
    print(f"Documentos gerados em {OUTPUT}")


if __name__ == "__main__":
    main()
