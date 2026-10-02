from __future__ import annotations

import json
import re
import time
from typing import Callable

from insurminds.config import Settings
from insurminds.llm.base import ChatProvider, ChatResult


class LLMConfigurationError(ValueError):
    pass


class AnthropicProvider:
    def __init__(self, settings: Settings):
        from anthropic import Anthropic

        if not settings.anthropic_api_key:
            raise LLMConfigurationError("ANTHROPIC_API_KEY não configurada.")
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model_name = settings.anthropic_model
        self.temperature = settings.llm_temperature
        self.workspace_id = settings.anthropic_workspace_id

    def chat(self, system: str, user: str, max_tokens: int = 4096) -> ChatResult:
        extra_headers = (
            {"anthropic-workspace-id": self.workspace_id} if self.workspace_id else None
        )
        response = _with_retry(
            lambda: self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
                extra_headers=extra_headers,
            )
        )
        text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")
        usage = getattr(response, "usage", None)
        return ChatResult(
            text=text,
            model=getattr(response, "model", self.model_name),
            input_tokens=getattr(usage, "input_tokens", 0) if usage else 0,
            output_tokens=getattr(usage, "output_tokens", 0) if usage else 0,
        )


class OpenAIProvider:
    def __init__(self, settings: Settings):
        from openai import OpenAI

        if not settings.openai_api_key:
            raise LLMConfigurationError("OPENAI_API_KEY não configurada.")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model_name = settings.openai_model
        self.temperature = settings.llm_temperature

    def chat(self, system: str, user: str, max_tokens: int = 4096) -> ChatResult:
        response = _with_retry(
            lambda: self.client.chat.completions.create(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
        )
        text = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        return ChatResult(
            text=text,
            model=getattr(response, "model", self.model_name),
            input_tokens=getattr(usage, "prompt_tokens", 0) if usage else 0,
            output_tokens=getattr(usage, "completion_tokens", 0) if usage else 0,
        )


class DemoProvider:
    """Fallback determinístico para conhecer a interface; não é IA generativa."""

    model_name = "demo-local"

    def chat(self, system: str, user: str, max_tokens: int = 4096) -> ChatResult:
        if "EXTRAIR_CLAUSULAS" in user:
            return ChatResult(text=json.dumps(self._extract_demo(user), ensure_ascii=False), model=self.model_name)
        if "GERAR_RESUMO_COMPARATIVO" in user:
            return ChatResult(
                text=(
                    "Comparação gerada no modo de demonstração. Existem diferenças nos campos sinalizados; "
                    "confira as evidências e execute com uma API de IA para obter interpretação jurídica contextual."
                ),
                model=self.model_name,
            )
        if "RESPONDER_COM_EVIDENCIAS" in user:
            return ChatResult(
                text="Modo de demonstração: consulte os valores e trechos exibidos na matriz comparativa.",
                model=self.model_name,
            )
        return ChatResult(text="Modo de demonstração ativo.", model=self.model_name)

    def _extract_demo(self, text: str) -> dict:
        items: list[dict] = []
        page_matches = list(re.finditer(r"<<<PAGINA (\d+)>>>\s*(.*?)(?=<<<PAGINA|\Z)", text, re.DOTALL))
        patterns = (
            ("numero_apolice", r"(?:apólice|apolice)(?:\s+n[ºo°.]*)?\s*[:\-]?\s*([A-Z0-9./-]{4,})"),
            ("seguradora", r"seguradora\s*[:\-]\s*([^\n]{3,100})"),
            ("segurado", r"(?:segurado|tomador)\s*[:\-]\s*([^\n]{3,100})"),
            ("limite_maximo_garantia", r"(?:limite máximo de garantia|lmg)\s*[:\-]?\s*(R\$\s*[\d.,]+)"),
            ("franquia_geral", r"(?:franquia|participação obrigatória)\s*[:\-]?\s*(R\$\s*[\d.,]+)"),
            ("prazo_complementar", r"prazo complementar\s*[:\-]?\s*(\d+\s*(?:meses|anos))"),
        )
        for page_match in page_matches:
            page = int(page_match.group(1))
            page_text = page_match.group(2)
            for key, pattern in patterns:
                found = re.search(pattern, page_text, re.IGNORECASE)
                if not found:
                    continue
                excerpt = found.group(0).strip()
                value = found.group(1).strip()
                items.append(
                    {
                        "key": key,
                        "status": "encontrado",
                        "value_text": value,
                        "normalized_value": value,
                        "unit": None,
                        "summary": excerpt,
                        "confidence": 0.65,
                        "evidences": [{"page": page, "excerpt": excerpt, "confidence": 0.65}],
                    }
                )
            clause_patterns = (
                ("vigencia_inicio", r"Vigência:\s*das\s+00h\s+de\s+([^\s]+)"),
                ("vigencia_fim", r"às\s+24h\s+de\s+([^\s.]+)"),
                ("cobertura_a", r"(Cobertura A:\s*.*?)(?=Cobertura B:|\n\d+\.|\Z)"),
                ("cobertura_b", r"(Cobertura B:\s*.*?)(?=Cobertura C:|\n\d+\.|\Z)"),
                ("cobertura_c", r"(Cobertura C:\s*.*?)(?=\n\d+\.|\Z)"),
                ("custos_defesa", r"((?:Os\s+)?custos de defesa\s+.*?\.)"),
                ("reclamacoes_trabalhistas", r"((?:Reclamações|Ficam excluídas reclamações).*?trabalhist.*?\.)"),
                ("investigacoes", r"((?:Despesas de representação em investigação|Investigações formais).*?\.)"),
                ("multas_penalidades", r"((?:Multas civis|Multas, penalidades).*?\.)"),
                ("data_retroatividade", r"(Data de retroatividade:\s*[^.]+\.)"),
                ("prazo_complementar", r"(Prazo complementar:\s*[^.]+\.)"),
                ("prazo_suplementar", r"((?:Prazo suplementar:|Não há prazo suplementar).*?\.)"),
                ("territorio", r"((?:Âmbito territorial mundial|Âmbito territorial:\s*Brasil).*?\.)"),
                ("jurisdicao", r"((?:Jurisdição mundial|Âmbito de jurisdição:).*?\.)"),
                ("atos_dolosos", r"((?:Ficam excluídos atos dolosos|Atos dolosos, fraudulentos).*?\.)"),
                ("segurado_contra_segurado", r"((?:A exclusão segurado contra segurado|Reclamações de segurado contra segurado).*?\.)"),
                ("fatos_anteriores", r"((?:Fatos e processos anteriores|Processos pendentes anteriores).*?\.)"),
                ("mudanca_controle", r"((?:Em caso de mudança de controle|Mudança de controle).*?\.)"),
                ("cancelamento", r"((?:O cancelamento|A seguradora poderá cancelar).*?\.)"),
            )
            existing_keys = {item["key"] for item in items}
            for key, pattern in clause_patterns:
                if key in existing_keys:
                    continue
                found = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if not found:
                    continue
                excerpt = " ".join(found.group(0).split())[:900]
                value = " ".join(found.group(1).split())[:700] if found.lastindex else excerpt
                items.append(
                    {
                        "key": key,
                        "status": "encontrado",
                        "value_text": value,
                        "normalized_value": value,
                        "unit": None,
                        "summary": value,
                        "confidence": 0.55,
                        "evidences": [{"page": page, "excerpt": excerpt, "confidence": 0.55}],
                    }
                )
        return {"items": items, "warnings": ["Extração heurística do modo demo; não representa uso de IA generativa."]}


def _with_retry(call: Callable, attempts: int = 3):
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return call()
        except Exception as exc:  # o SDK expõe classes distintas por versão
            last_error = exc
            status_code = getattr(exc, "status_code", None)
            if isinstance(exc, (TypeError, ValueError)):
                raise
            if status_code is not None and status_code not in {408, 409, 429} and status_code < 500:
                raise
            if attempt == attempts - 1:
                break
            time.sleep(1.5 * (2**attempt))
    assert last_error is not None
    raise last_error


def build_provider(settings: Settings) -> ChatProvider:
    if settings.llm_provider == "anthropic":
        return AnthropicProvider(settings)
    if settings.llm_provider == "openai":
        return OpenAIProvider(settings)
    if settings.llm_provider == "demo":
        return DemoProvider()
    raise LLMConfigurationError(f"Provedor desconhecido: {settings.llm_provider}")
