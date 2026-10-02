from __future__ import annotations

import json
import re
from typing import Any


class JSONResponseError(ValueError):
    pass


def parse_json_object(text: str) -> dict[str, Any]:
    """Extrai um objeto JSON mesmo quando o modelo adiciona uma cerca Markdown."""
    candidate = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", candidate, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        candidate = fence.group(1)
    else:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start >= 0 and end > start:
            candidate = candidate[start : end + 1]
    try:
        result = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise JSONResponseError(f"A IA não retornou JSON válido: {exc.msg}.") from exc
    if not isinstance(result, dict):
        raise JSONResponseError("A resposta da IA não é um objeto JSON.")
    return result

