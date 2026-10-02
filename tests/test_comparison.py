from insurminds.domain.models import (
    DocumentInfo,
    Evidence,
    ExtractedField,
    FieldStatus,
    PolicyAnalysis,
)
from insurminds.domain.taxonomy import FIELD_DEFINITIONS
from insurminds.llm.providers import DemoProvider
from insurminds.services.comparison_service import ComparisonService


def make_analysis(identifier: str, filename: str, limit: int) -> PolicyAnalysis:
    fields = []
    for definition in FIELD_DEFINITIONS:
        if definition.key == "limite_maximo_garantia":
            fields.append(
                ExtractedField(
                    key=definition.key,
                    label=definition.label,
                    category=definition.category,
                    status=FieldStatus.ENCONTRADO,
                    value_text=f"R$ {limit:,}",
                    normalized_value=limit,
                    evidences=[Evidence(page=2, excerpt=f"Limite máximo de garantia R$ {limit:,}", confidence=0.9)],
                    confidence=0.9,
                )
            )
        else:
            fields.append(ExtractedField(key=definition.key, label=definition.label, category=definition.category))
    return PolicyAnalysis(
        id=identifier,
        document=DocumentInfo(
            id=f"doc-{identifier}",
            filename=filename,
            sha256=identifier * 64,
            mime_type="application/pdf",
            page_count=3,
            character_count=100,
        ),
        fields=fields,
    )


def test_comparison_detects_limit_difference():
    first = make_analysis("a", "A.pdf", 10_000_000)
    second = make_analysis("b", "B.pdf", 15_000_000)
    result = ComparisonService(DemoProvider()).compare([first, second], use_ai_summary=False)
    row = next(item for item in result.rows if item.key == "limite_maximo_garantia")
    assert row.is_different is True
    assert row.attention.value == "alta"

