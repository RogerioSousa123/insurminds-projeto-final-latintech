from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class FieldStatus(str, Enum):
    ENCONTRADO = "encontrado"
    NAO_LOCALIZADO = "nao_localizado"
    AMBIGUO = "ambiguo"
    NAO_APLICAVEL = "nao_aplicavel"


class AttentionLevel(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    INDETERMINADA = "indeterminada"


class Evidence(BaseModel):
    page: int = Field(ge=1)
    excerpt: str = Field(min_length=1, max_length=2500)
    confidence: float = Field(default=0.5, ge=0, le=1)

    @field_validator("excerpt")
    @classmethod
    def clean_excerpt(cls, value: str) -> str:
        return " ".join(value.split())


class ExtractedField(BaseModel):
    key: str
    label: str
    category: str
    status: FieldStatus = FieldStatus.NAO_LOCALIZADO
    value_text: str | None = None
    normalized_value: Any = None
    unit: str | None = None
    summary: str | None = None
    evidences: list[Evidence] = Field(default_factory=list)
    confidence: float = Field(default=0, ge=0, le=1)

    @field_validator("value_text", "unit", "summary")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.split())
        return cleaned or None


class DocumentInfo(BaseModel):
    id: str
    filename: str
    sha256: str
    mime_type: str
    page_count: int = Field(ge=1)
    character_count: int = Field(ge=0)
    ocr_pages: list[int] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now_iso)


class PageText(BaseModel):
    page: int = Field(ge=1)
    text: str
    extraction_method: str = "native"


class PolicyAnalysis(BaseModel):
    id: str
    document: DocumentInfo
    fields: list[ExtractedField]
    warnings: list[str] = Field(default_factory=list)
    model_name: str = "unknown"
    prompt_version: str = "1.0"
    input_tokens: int = 0
    output_tokens: int = 0
    elapsed_seconds: float = 0
    created_at: str = Field(default_factory=utc_now_iso)

    def field_map(self) -> dict[str, ExtractedField]:
        return {item.key: item for item in self.fields}


class ComparisonCell(BaseModel):
    policy_id: str
    filename: str
    status: FieldStatus
    value_text: str | None = None
    normalized_value: Any = None
    evidences: list[Evidence] = Field(default_factory=list)


class ComparisonRow(BaseModel):
    key: str
    label: str
    category: str
    cells: list[ComparisonCell]
    is_different: bool = False
    attention: AttentionLevel = AttentionLevel.INDETERMINADA
    explanation: str = ""


class ComparisonResult(BaseModel):
    id: str
    policy_ids: list[str]
    rows: list[ComparisonRow]
    executive_summary: str = ""
    caveats: list[str] = Field(default_factory=list)
    model_name: str = "deterministic"
    created_at: str = Field(default_factory=utc_now_iso)


class ProcessingEvent(BaseModel):
    stage: str
    message: str
    progress: float = Field(ge=0, le=1)

