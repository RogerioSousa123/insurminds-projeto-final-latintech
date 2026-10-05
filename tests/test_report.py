from insurminds.llm.providers import DemoProvider
from insurminds.services.comparison_service import ComparisonService
from insurminds.services.report_service import build_comparison_pdf

from test_comparison import make_analysis


def test_report_is_a_pdf():
    analyses = [make_analysis("d", "D.pdf", 10_000_000), make_analysis("e", "E.pdf", 12_000_000)]
    comparison = ComparisonService(DemoProvider()).compare(analyses, use_ai_summary=False)
    content = build_comparison_pdf(comparison, analyses)
    assert content.startswith(b"%PDF")
    assert len(content) > 1000


def test_report_handles_long_comparison_values():
    analyses = [make_analysis("a", "A.pdf", 10_000_000), make_analysis("b", "B.pdf", 15_000_000)]
    for analysis in analyses:
        for field in analysis.fields:
            field.status = field.status.ENCONTRADO
            field.value_text = "Cláusula extensa com condições, exceções e requisitos. " * 80
    comparison = ComparisonService(DemoProvider()).compare(analyses, use_ai_summary=False)

    content = build_comparison_pdf(comparison, analyses)

    assert content.startswith(b"%PDF")
