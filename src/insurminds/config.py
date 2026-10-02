from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "demo").strip().lower()
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "").strip()
    anthropic_model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5").strip()
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "").strip()
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()
    database_path: Path = Path(os.getenv("DATABASE_PATH", "data/insurminds.db"))
    max_document_pages: int = _int_env("MAX_DOCUMENT_PAGES", 150)
    llm_chunk_chars: int = _int_env("LLM_CHUNK_CHARS", 28000)
    llm_temperature: float = _float_env("LLM_TEMPERATURE", 0.0)
    ocr_language: str = os.getenv("OCR_LANGUAGE", "por+eng").strip()
    tesseract_cmd: str = os.getenv("TESSERACT_CMD", "").strip()

    @property
    def model_name(self) -> str:
        if self.llm_provider == "anthropic":
            return self.anthropic_model
        if self.llm_provider == "openai":
            return self.openai_model
        return "demo-local"

    def validate_provider(self) -> list[str]:
        errors: list[str] = []
        if self.llm_provider not in {"anthropic", "openai", "demo"}:
            errors.append("LLM_PROVIDER deve ser anthropic, openai ou demo.")
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            errors.append("ANTHROPIC_API_KEY não foi configurada.")
        if self.llm_provider == "openai" and not self.openai_api_key:
            errors.append("OPENAI_API_KEY não foi configurada.")
        return errors

