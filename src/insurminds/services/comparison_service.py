from __future__ import annotations

import json
import uuid
from typing import Any

from insurminds.domain.models import (
    AttentionLevel,
    ComparisonCell,
    ComparisonResult,
    ComparisonRow,
    FieldStatus,
    PolicyAnalysis,
)
from insurminds.domain.taxonomy import FIELD_DEFINITIONS
from insurminds.llm.base import ChatProvider


COMPARISON_SYSTEM_PROMPT = """Você é um analista técnico de seguros D&O.
Explique diferenças usando somente os dados estruturados fornecidos.
Não invente coberturas, não transforme "não localizado" em "não coberto" e não dê aconselhamento jurídico.
Evite declarar uma apólice como universalmente melhor: descreva amplitude, restrições e pontos que exigem validação humana.
Um número de processo SUSEP não é número de apólice; a data da versão das Condições Gerais não é vigência individual.
Quando um valor depende da Especificação não fornecida, trate-o como lacuna, não como limite ou franquia efetivos.
Seja objetivo e escreva em português do Brasil.
"""


class ComparisonService:
    def __init__(self, provider: ChatProvider):
        self.provider = provider

    def compare(self, analyses: list[PolicyAnalysis], use_ai_summary: bool = True) -> ComparisonResult:
        if len(analyses) < 2:
            raise ValueError("Selecione pelo menos duas apólices para comparar.")
        if len({item.id for item in analyses}) != len(analyses):
            raise ValueError("Uma mesma análise não pode ser comparada consigo própria.")

        rows: list[ComparisonRow] = []
        maps = [analysis.field_map() for analysis in analyses]
        for definition in FIELD_DEFINITIONS:
            cells: list[ComparisonCell] = []
            for analysis, field_map in zip(analyses, maps):
                field = field_map[definition.key]
                cells.append(
                    ComparisonCell(
                        policy_id=analysis.id,
                        filename=analysis.document.filename,
                        status=field.status,
                        value_text=field.value_text,
                        normalized_value=field.normalized_value,
                        evidences=field.evidences,
                    )
                )
            different = _cells_are_different(cells)
            attention = _attention(definition.attention_if_different, cells, different)
            rows.append(
                ComparisonRow(
                    key=definition.key,
                    label=definition.label,
                    category=definition.category,
                    cells=cells,
                    is_different=different,
                    attention=attention,
                    explanation=_deterministic_explanation(cells, different),
                )
            )

        result = ComparisonResult(
            id=str(uuid.uuid4()),
            policy_ids=[item.id for item in analyses],
            rows=rows,
            executive_summary=_fallback_summary(rows),
            caveats=[
                "Informação não localizada não significa ausência de cobertura.",
                "A análise automatizada deve ser validada por profissional especializado antes de uma decisão.",
            ],
        )
        if use_ai_summary and self.provider.model_name != "demo-local":
            self._enrich_with_ai(result)
        elif use_ai_summary:
            demo = self.provider.chat("", "GERAR_RESUMO_COMPARATIVO")
            result.executive_summary = demo.text
            result.model_name = demo.model
        return result

    def _enrich_with_ai(self, result: ComparisonResult) -> None:
        payload = []
        for row in result.rows:
            payload.append(
                {
                    "key": row.key,
                    "label": row.label,
                    "attention": row.attention.value,
                    "is_different": row.is_different,
                    "policies": [
                        {
                            "filename": cell.filename,
                            "status": cell.status.value,
                            "value": (cell.value_text or "")[:650] or None,
                            "pages": sorted({evidence.page for evidence in cell.evidences}),
                        }
                        for cell in row.cells
                    ],
                }
            )
        user = f"""TAREFA: GERAR_RESUMO_COMPARATIVO
Analise os critérios abaixo e escreva uma síntese executiva curta em Markdown, sem JSON.
Use exatamente estas seções:
### Principais diferenças
Apresente de três a cinco diferenças prioritárias e explique o efeito prático de cada redação.
### Em comum
Liste os pontos relevantes tratados pelos dois documentos.
### Lacunas de informação
Informe o que não pode ser comparado porque depende da Especificação da Apólice ou não foi localizado.

Não recomende contratação e não declare um vencedor universal.

<comparacao>
{json.dumps(payload, ensure_ascii=False)}
</comparacao>
"""
        response = self.provider.chat(COMPARISON_SYSTEM_PROMPT, user, max_tokens=2600)
        if response.text.strip():
            result.executive_summary = response.text.strip()
        result.model_name = response.model


def _canonical(value: Any) -> str:
    if value is None:
        return ""
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True).casefold()
    except TypeError:
        return str(value).casefold().strip()


def _cells_are_different(cells: list[ComparisonCell]) -> bool:
    statuses = {cell.status for cell in cells}
    if len(statuses) > 1:
        return True
    if statuses == {FieldStatus.NAO_LOCALIZADO}:
        return False
    values = {_canonical(cell.normalized_value if cell.normalized_value is not None else cell.value_text) for cell in cells}
    return len(values) > 1


def _attention(level: str, cells: list[ComparisonCell], different: bool) -> AttentionLevel:
    if any(cell.status in {FieldStatus.NAO_LOCALIZADO, FieldStatus.AMBIGUO} for cell in cells):
        return AttentionLevel.INDETERMINADA
    if not different:
        return AttentionLevel.BAIXA
    return AttentionLevel(level)


def _deterministic_explanation(cells: list[ComparisonCell], different: bool) -> str:
    missing = [cell.filename for cell in cells if cell.status == FieldStatus.NAO_LOCALIZADO]
    ambiguous = [cell.filename for cell in cells if cell.status == FieldStatus.AMBIGUO]
    if missing:
        return "Informação não localizada em: " + ", ".join(missing) + "."
    if ambiguous:
        return "Há informação ambígua em: " + ", ".join(ambiguous) + "."
    if different:
        return "Os valores extraídos são diferentes; confira as evidências antes da decisão."
    return "Não foi identificada diferença material nos valores estruturados."


def _fallback_summary(rows: list[ComparisonRow]) -> str:
    differences = sum(row.is_different for row in rows)
    common = sum(
        not row.is_different and all(cell.status == FieldStatus.ENCONTRADO for cell in row.cells)
        for row in rows
    )
    high = sum(row.attention == AttentionLevel.ALTA for row in rows)
    unknown = sum(row.attention == AttentionLevel.INDETERMINADA for row in rows)
    return (
        f"Foram avaliados {len(rows)} critérios: **{differences} diferenças**, sendo **{high} de atenção "
        f"alta**, e **{common} pontos em comum**. Em **{unknown} critérios** faltam dados equivalentes "
        "ou há redação que exige conferência humana."
    )
