from insurminds.services.chat_service import ChatService, _validate_answer_citations

from test_comparison import make_analysis


class NoopProvider:
    model_name = "noop"


def test_broad_comparison_context_contains_both_documents():
    analyses = [make_analysis("a", "A.pdf", 10_000_000), make_analysis("b", "B.pdf", 15_000_000)]
    context = ChatService(NoopProvider())._select_context("Quais são as principais diferenças?", analyses)

    limit_items = [item for item in context if item["chave"] == "limite_maximo_garantia"]
    assert {item["arquivo"] for item in limit_items} == {"A.pdf", "B.pdf"}


def test_normalizes_and_validates_multi_page_citations():
    context = [
        {
            "arquivo": "A.pdf",
            "evidencias": [
                {"pagina": 2, "trecho": "Trecho dois"},
                {"pagina": 6, "trecho": "Trecho seis"},
            ],
        }
    ]

    checked = _validate_answer_citations("Informação [A.pdf, p. 2 e 6].", context)

    assert "[A.pdf, p. 2] [A.pdf, p. 6]" in checked
