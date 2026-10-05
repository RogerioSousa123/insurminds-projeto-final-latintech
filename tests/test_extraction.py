import json

from insurminds.config import Settings
from insurminds.domain.models import DocumentInfo, FieldStatus, PageText
from insurminds.llm.base import ChatResult
from insurminds.services.document_processor import DocumentBundle
from insurminds.services.extraction_service import ExtractionService


class FakeExtractionProvider:
    model_name = "fake-model"

    def chat(self, system: str, user: str, max_tokens: int = 4096) -> ChatResult:
        payload = {
            "items": [
                {
                    "key": "limite_maximo_garantia",
                    "status": "encontrado",
                    "value_text": "R$ 10.000.000,00",
                    "normalized_value": 10000000,
                    "unit": "BRL",
                    "summary": "Limite agregado.",
                    "confidence": 0.95,
                    "evidences": [
                        {
                            "page": 1,
                            "excerpt": "Limite máximo de garantia: R$ 10.000.000,00",
                            "confidence": 0.95,
                        }
                    ],
                },
                {
                    "key": "campo_inventado",
                    "status": "encontrado",
                    "value_text": "não deve entrar",
                    "confidence": 1,
                    "evidences": [{"page": 1, "excerpt": "texto qualquer longo", "confidence": 1}],
                },
            ],
            "warnings": [],
        }
        return ChatResult(text=json.dumps(payload), model=self.model_name, input_tokens=100, output_tokens=50)


def test_extracts_only_taxonomy_fields_with_verified_evidence(tmp_path):
    settings = Settings(database_path=tmp_path / "test.db", llm_chunk_chars=10000)
    page = PageText(
        page=1,
        text="CONDIÇÕES PARTICULARES\nLimite máximo de garantia: R$ 10.000.000,00\nDemais cláusulas.",
    )
    bundle = DocumentBundle(
        document=DocumentInfo(
            id="doc1",
            filename="teste.pdf",
            sha256="a" * 64,
            mime_type="application/pdf",
            page_count=1,
            character_count=len(page.text),
        ),
        pages=[page],
        warnings=[],
    )
    analysis = ExtractionService(settings, FakeExtractionProvider()).analyze(bundle)
    field = analysis.field_map()["limite_maximo_garantia"]
    assert field.status == FieldStatus.ENCONTRADO
    assert field.normalized_value == 10000000
    assert field.evidences[0].page == 1
    assert "campo_inventado" not in analysis.field_map()
    assert any("Campo desconhecido" in warning for warning in analysis.warnings)


class HallucinatingProvider:
    model_name = "fake-model"

    def chat(self, system: str, user: str, max_tokens: int = 4096) -> ChatResult:
        return ChatResult(
            text=json.dumps(
                {
                    "items": [
                        {
                            "key": "franquia_geral",
                            "status": "encontrado",
                            "value_text": "R$ 1,00",
                            "confidence": 0.99,
                            "evidences": [
                                {"page": 1, "excerpt": "Esta frase não existe no documento original", "confidence": 0.99}
                            ],
                        }
                    ],
                    "warnings": [],
                }
            ),
            model=self.model_name,
        )


def test_discards_unverifiable_evidence(tmp_path):
    settings = Settings(database_path=tmp_path / "test.db")
    page = PageText(page=1, text="Documento contendo apenas informações sobre a vigência anual da apólice.")
    bundle = DocumentBundle(
        document=DocumentInfo(
            id="doc2",
            filename="teste.pdf",
            sha256="b" * 64,
            mime_type="application/pdf",
            page_count=1,
            character_count=len(page.text),
        ),
        pages=[page],
        warnings=[],
    )
    analysis = ExtractionService(settings, HallucinatingProvider()).analyze(bundle)
    assert analysis.field_map()["franquia_geral"].status == FieldStatus.NAO_LOCALIZADO
    assert any("descartado" in warning for warning in analysis.warnings)


class PartiallyBrokenProvider:
    model_name = "fake-model"

    def chat(self, system: str, user: str, max_tokens: int = 4096) -> ChatResult:
        if "<<<PAGINA 1>>>" in user and "TAREFA: EXTRAIR_CLAUSULAS" in user:
            return ChatResult(
                text=json.dumps(
                    {
                        "items": [
                            {
                                "key": "custos_defesa",
                                "status": "encontrado",
                                "value_text": "Custos de defesa cobertos.",
                                "normalized_value": "coberto",
                                "summary": "Cobertura prevista.",
                                "confidence": 0.9,
                                "evidences": [
                                    {
                                        "page": 1,
                                        "excerpt": "Custos de defesa cobertos.",
                                        "confidence": 0.9,
                                    }
                                ],
                            }
                        ],
                        "warnings": [],
                    }
                ),
                model=self.model_name,
            )
        return ChatResult(text='{"items": [{"key": "quebrado"}', model=self.model_name)


def test_keeps_partial_analysis_when_one_chunk_is_invalid(tmp_path):
    settings = Settings(database_path=tmp_path / "test.db", llm_chunk_chars=80)
    pages = [
        PageText(page=1, text="Custos de defesa cobertos. " * 4),
        PageText(page=2, text="Trecho que sempre retorna JSON inválido. " * 4),
    ]
    bundle = DocumentBundle(
        document=DocumentInfo(
            id="doc3",
            filename="parcial.pdf",
            sha256="c" * 64,
            mime_type="application/pdf",
            page_count=2,
            character_count=sum(len(page.text) for page in pages),
        ),
        pages=pages,
        warnings=[],
    )

    analysis = ExtractionService(settings, PartiallyBrokenProvider()).analyze(bundle)

    assert analysis.field_map()["custos_defesa"].status == FieldStatus.ENCONTRADO
    assert any("Análise parcial" in warning for warning in analysis.warnings)


class NarrativeVariantsProvider:
    model_name = "fake-model"

    def chat(self, system: str, user: str, max_tokens: int = 4096) -> ChatResult:
        page = 1 if "<<<PAGINA 1>>>" in user else 2
        excerpt = "Custos de defesa cobertos." if page == 1 else "Custos de defesa consomem o limite."
        payload = {
            "items": [
                {
                    "key": "custos_defesa",
                    "status": "encontrado",
                    "value_text": excerpt,
                    "normalized_value": excerpt,
                    "summary": excerpt,
                    "confidence": 0.9,
                    "evidences": [{"page": page, "excerpt": excerpt, "confidence": 0.9}],
                }
            ],
            "warnings": [],
        }
        return ChatResult(text=json.dumps(payload), model=self.model_name)


def test_consolidates_narrative_clauses_without_marking_ambiguity(tmp_path):
    settings = Settings(database_path=tmp_path / "test.db", llm_chunk_chars=80)
    pages = [
        PageText(page=1, text="Custos de defesa cobertos. " * 4),
        PageText(page=2, text="Custos de defesa consomem o limite. " * 4),
    ]
    bundle = DocumentBundle(
        document=DocumentInfo(
            id="doc4",
            filename="clausulas.pdf",
            sha256="d" * 64,
            mime_type="application/pdf",
            page_count=2,
            character_count=sum(len(page.text) for page in pages),
        ),
        pages=pages,
        warnings=[],
    )

    analysis = ExtractionService(settings, NarrativeVariantsProvider()).analyze(bundle)

    field = analysis.field_map()["custos_defesa"]
    assert field.status == FieldStatus.ENCONTRADO
    assert len(field.evidences) == 2
