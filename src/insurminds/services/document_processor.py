from __future__ import annotations

import hashlib
import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from insurminds.config import Settings
from insurminds.domain.models import DocumentInfo, PageText


class DocumentProcessingError(ValueError):
    """Erro esperado durante leitura ou OCR de um documento."""


@dataclass
class DocumentBundle:
    document: DocumentInfo
    pages: list[PageText]
    warnings: list[str]

    @property
    def full_text(self) -> str:
        return "\n\n".join(f"[PÁGINA {p.page}]\n{p.text}" for p in self.pages)


class DocumentProcessor:
    SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}
    MAX_FILE_BYTES = 50 * 1024 * 1024

    def __init__(self, settings: Settings):
        self.settings = settings

    def process(
        self,
        filename: str,
        content: bytes,
        mime_type: str | None = None,
        progress: Callable[[int, int, str], None] | None = None,
    ) -> DocumentBundle:
        if not content:
            raise DocumentProcessingError("O arquivo está vazio.")
        if len(content) > self.MAX_FILE_BYTES:
            raise DocumentProcessingError("O arquivo excede o limite de 50 MB do MVP.")

        safe_name = Path(filename).name
        extension = Path(safe_name).suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise DocumentProcessingError(f"Formato não suportado: {extension or 'sem extensão'}.")

        digest = hashlib.sha256(content).hexdigest()
        document_id = digest[:20]
        warnings: list[str] = []

        if extension == ".pdf":
            pages, ocr_pages = self._process_pdf(content, warnings, progress)
            detected_mime = "application/pdf"
        else:
            pages, ocr_pages = self._process_image(content, warnings)
            detected_mime = mime_type or "image/*"

        if not any(page.text.strip() for page in pages):
            raise DocumentProcessingError(
                "Não foi possível extrair texto. Instale/configure o Tesseract para documentos digitalizados."
            )

        info = DocumentInfo(
            id=document_id,
            filename=safe_name,
            sha256=digest,
            mime_type=detected_mime,
            page_count=len(pages),
            character_count=sum(len(page.text) for page in pages),
            ocr_pages=ocr_pages,
        )
        return DocumentBundle(document=info, pages=pages, warnings=warnings)

    def _process_pdf(
        self,
        content: bytes,
        warnings: list[str],
        progress: Callable[[int, int, str], None] | None,
    ) -> tuple[list[PageText], list[int]]:
        try:
            import pymupdf
        except ImportError as exc:
            raise DocumentProcessingError("A dependência PyMuPDF não está instalada.") from exc

        try:
            pdf = pymupdf.open(stream=content, filetype="pdf")
        except Exception as exc:
            raise DocumentProcessingError(f"PDF inválido ou corrompido: {exc}") from exc

        if pdf.needs_pass:
            pdf.close()
            raise DocumentProcessingError("PDF protegido por senha não é suportado.")
        if pdf.page_count < 1:
            pdf.close()
            raise DocumentProcessingError("O PDF não possui páginas.")
        if pdf.page_count > self.settings.max_document_pages:
            count = pdf.page_count
            pdf.close()
            raise DocumentProcessingError(
                f"O PDF possui {count} páginas; o limite configurado é {self.settings.max_document_pages}."
            )

        pages: list[PageText] = []
        ocr_pages: list[int] = []
        total = pdf.page_count
        try:
            for index, page in enumerate(pdf):
                number = index + 1
                if progress:
                    progress(number, total, f"Lendo página {number} de {total}")
                native_text = self._clean_text(page.get_text("text", sort=True))
                method = "native"
                text = native_text
                if self._needs_ocr(native_text):
                    ocr_text = self._ocr_pdf_page(page, warnings, number)
                    if len(ocr_text) > len(native_text):
                        text = ocr_text
                        method = "ocr"
                        ocr_pages.append(number)
                pages.append(PageText(page=number, text=text, extraction_method=method))
        finally:
            pdf.close()

        empty_pages = [str(item.page) for item in pages if not item.text.strip()]
        if empty_pages:
            warnings.append("Páginas sem texto extraído: " + ", ".join(empty_pages[:20]))
        return pages, ocr_pages

    def _process_image(self, content: bytes, warnings: list[str]) -> tuple[list[PageText], list[int]]:
        try:
            from PIL import Image, ImageOps, ImageSequence
        except ImportError as exc:
            raise DocumentProcessingError("A dependência Pillow não está instalada.") from exc

        try:
            image = Image.open(io.BytesIO(content))
            frames = [ImageOps.exif_transpose(frame.copy()).convert("RGB") for frame in ImageSequence.Iterator(image)]
        except Exception as exc:
            raise DocumentProcessingError(f"Imagem inválida ou corrompida: {exc}") from exc

        if len(frames) > self.settings.max_document_pages:
            raise DocumentProcessingError("A imagem multipágina excede o limite configurado.")
        pages: list[PageText] = []
        for index, frame in enumerate(frames, start=1):
            text = self._ocr_image(frame, warnings, index)
            pages.append(PageText(page=index, text=text, extraction_method="ocr"))
        return pages, list(range(1, len(pages) + 1))

    def _ocr_pdf_page(self, page: object, warnings: list[str], page_number: int) -> str:
        try:
            from PIL import Image

            pixmap = page.get_pixmap(matrix=self._fitz_matrix(2.0), alpha=False)
            image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
            return self._ocr_image(image, warnings, page_number)
        except Exception as exc:
            warnings.append(f"OCR indisponível na página {page_number}: {exc}")
            return ""

    @staticmethod
    def _fitz_matrix(scale: float):
        import pymupdf

        return pymupdf.Matrix(scale, scale)

    def _ocr_image(self, image: object, warnings: list[str], page_number: int) -> str:
        try:
            import pytesseract

            if self.settings.tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = self.settings.tesseract_cmd
            text = pytesseract.image_to_string(image, lang=self.settings.ocr_language)
            return self._clean_text(text)
        except Exception as exc:
            warnings.append(f"Falha no OCR da página {page_number}: {exc}")
            return ""

    @staticmethod
    def _needs_ocr(text: str) -> bool:
        if len(text.strip()) < 80:
            return True
        printable = sum(character.isprintable() for character in text)
        return printable / max(len(text), 1) < 0.85

    @staticmethod
    def _clean_text(text: str) -> str:
        text = text.replace("\x00", " ").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def chunk_pages(pages: list[PageText], max_chars: int) -> list[list[PageText]]:
    """Agrupa páginas sem quebrá-las, preservando a referência da evidência."""
    chunks: list[list[PageText]] = []
    current: list[PageText] = []
    current_size = 0
    for page in pages:
        page_size = len(page.text) + 40
        if current and current_size + page_size > max_chars:
            chunks.append(current)
            current = []
            current_size = 0
        current.append(page)
        current_size += page_size
    if current:
        chunks.append(current)
    return chunks


def pages_as_prompt_text(pages: list[PageText]) -> str:
    return "\n\n".join(f"<<<PAGINA {page.page}>>>\n{page.text}" for page in pages)
