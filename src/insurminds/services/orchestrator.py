from __future__ import annotations

import hashlib
from collections.abc import Callable

from insurminds.config import Settings
from insurminds.domain.models import PolicyAnalysis, ProcessingEvent
from insurminds.llm.base import ChatProvider
from insurminds.services.document_processor import DocumentProcessor
from insurminds.services.extraction_service import ExtractionService
from insurminds.storage.repository import AnalysisRepository


class AnalysisOrchestrator:
    """Coordena ingestão, leitura, IA, validação e persistência."""

    def __init__(self, settings: Settings, provider: ChatProvider, repository: AnalysisRepository):
        self.settings = settings
        self.provider = provider
        self.repository = repository
        self.document_processor = DocumentProcessor(settings)
        self.extraction_service = ExtractionService(settings, provider)

    def process(
        self,
        filename: str,
        content: bytes,
        mime_type: str | None = None,
        force: bool = False,
        notify: Callable[[ProcessingEvent], None] | None = None,
    ) -> tuple[PolicyAnalysis, bool]:
        digest = hashlib.sha256(content).hexdigest()
        if not force:
            cached = self.repository.find_cached(digest, self.settings.model_name)
            if cached:
                if notify:
                    notify(ProcessingEvent(stage="cache", message="Análise recuperada do cache local.", progress=1))
                return cached, True

        if notify:
            notify(ProcessingEvent(stage="ingestao", message="Validando e lendo o documento.", progress=0.05))

        def reading_progress(current: int, total: int, message: str) -> None:
            if notify:
                notify(
                    ProcessingEvent(
                        stage="leitura",
                        message=message,
                        progress=0.05 + (current / max(total, 1)) * 0.25,
                    )
                )

        bundle = self.document_processor.process(filename, content, mime_type, reading_progress)

        def extraction_progress(current: int, total: int, message: str) -> None:
            if notify:
                notify(
                    ProcessingEvent(
                        stage="ia",
                        message=message,
                        progress=0.30 + (current / max(total, 1)) * 0.60,
                    )
                )

        analysis = self.extraction_service.analyze(bundle, extraction_progress)
        if notify:
            notify(ProcessingEvent(stage="persistencia", message="Salvando análise localmente.", progress=0.95))
        self.repository.save_analysis(analysis, bundle.pages)
        if notify:
            notify(ProcessingEvent(stage="concluido", message="Documento processado.", progress=1))
        return analysis, False

