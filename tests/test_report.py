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

