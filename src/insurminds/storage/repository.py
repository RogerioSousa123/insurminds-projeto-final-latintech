from __future__ import annotations

import json
import re
import sqlite3
from contextlib import contextmanager
from collections.abc import Iterator
from pathlib import Path

from insurminds.domain.models import ComparisonResult, FieldStatus, PageText, PolicyAnalysis
from insurminds.domain.taxonomy import SCALAR_FIELD_KEYS


class AnalysisRepository:
    def __init__(self, database_path: Path):
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=15)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    document_sha TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    prompt_version TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    pages_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_analyses_sha
                    ON analyses(document_sha, model_name, prompt_version, created_at DESC);

                CREATE TABLE IF NOT EXISTS comparisons (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );
                """
            )

    def save_analysis(self, analysis: PolicyAnalysis, pages: list[PageText]) -> None:
        payload = analysis.model_dump_json()
        pages_payload = json.dumps([page.model_dump(mode="json") for page in pages], ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO analyses
                    (id, document_sha, filename, model_name, prompt_version, created_at, payload_json, pages_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis.id,
                    analysis.document.sha256,
                    analysis.document.filename,
                    analysis.model_name,
                    analysis.prompt_version,
                    analysis.created_at,
                    payload,
                    pages_payload,
                ),
            )

    def list_analyses(self) -> list[PolicyAnalysis]:
        with self._connect() as connection:
            rows = connection.execute("SELECT payload_json FROM analyses ORDER BY created_at DESC").fetchall()
        return [_normalize_legacy_analysis(PolicyAnalysis.model_validate_json(row["payload_json"])) for row in rows]

    def get_analysis(self, analysis_id: str) -> PolicyAnalysis | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM analyses WHERE id = ?", (analysis_id,)
            ).fetchone()
        return _normalize_legacy_analysis(PolicyAnalysis.model_validate_json(row["payload_json"])) if row else None

    def get_pages(self, analysis_id: str) -> list[PageText]:
        with self._connect() as connection:
            row = connection.execute("SELECT pages_json FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
        if not row:
            return []
        return [PageText.model_validate(item) for item in json.loads(row["pages_json"])]

    def find_cached(self, sha256: str, model_name: str, prompt_version: str = "1.0") -> PolicyAnalysis | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload_json FROM analyses
                WHERE document_sha = ? AND model_name = ? AND prompt_version = ?
                ORDER BY created_at DESC LIMIT 1
                """,
                (sha256, model_name, prompt_version),
            ).fetchone()
        return _normalize_legacy_analysis(PolicyAnalysis.model_validate_json(row["payload_json"])) if row else None

    def delete_analysis(self, analysis_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        return cursor.rowcount > 0

    def save_comparison(self, comparison: ComparisonResult) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO comparisons (id, created_at, payload_json) VALUES (?, ?, ?)",
                (comparison.id, comparison.created_at, comparison.model_dump_json()),
            )

    def get_comparison(self, comparison_id: str) -> ComparisonResult | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM comparisons WHERE id = ?", (comparison_id,)
            ).fetchone()
        return ComparisonResult.model_validate_json(row["payload_json"]) if row else None

    def find_latest_comparison(self, policy_ids: list[str]) -> ComparisonResult | None:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT payload_json FROM comparisons ORDER BY created_at DESC"
            ).fetchall()
        for row in rows:
            comparison = ComparisonResult.model_validate_json(row["payload_json"])
            if comparison.policy_ids == policy_ids:
                return comparison
        return None


def _normalize_legacy_analysis(analysis: PolicyAnalysis) -> PolicyAnalysis:
    """Aplica a regra atual de consolidação também às análises já salvas."""
    for field in analysis.fields:
        if field.key not in SCALAR_FIELD_KEYS and field.status == FieldStatus.AMBIGUO and field.evidences:
            field.status = FieldStatus.ENCONTRADO
        value = (field.value_text or "").casefold()
        if field.key == "numero_apolice" and ("processo susep" in value or "registro susep" in value):
            _mark_not_located(field)
        elif field.key in {"vigencia_inicio", "vigencia_fim"} and any(
            marker in value for marker in ("ou posterior", "versão", "versao", "validade das condições")
        ):
            _mark_not_located(field)
        elif field.key in {"limite_maximo_garantia", "franquia_geral"} and not _has_actual_amount(field):
            _mark_not_located(field)
        elif field.key == "data_retroatividade" and not _has_actual_retroactive_date(field):
            _mark_not_located(field)
    return analysis


def _mark_not_located(field) -> None:
    field.status = FieldStatus.NAO_LOCALIZADO
    field.value_text = None
    field.normalized_value = None
    field.unit = None
    field.summary = None
    field.evidences = []
    field.confidence = 0


def _has_actual_amount(field) -> bool:
    value = " ".join(filter(None, [field.value_text, field.summary, field.unit])).casefold()
    if any(marker in value for marker in ("sem franquia", "não se aplica", "nao se aplica")):
        return True
    if isinstance(field.normalized_value, (int, float)) and not isinstance(field.normalized_value, bool):
        return True
    return bool(re.search(r"(?:r\$|usd|eur|brl|us\$)\s*[\d.]", value, flags=re.IGNORECASE))


def _has_actual_retroactive_date(field) -> bool:
    normalized = field.normalized_value
    if isinstance(normalized, str):
        text = normalized.strip().casefold()
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", text)) or "ilimitad" in text
    return False
