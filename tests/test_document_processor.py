from insurminds.config import Settings
from insurminds.services.document_processor import DocumentProcessor


def test_native_pdf_text_extraction(tmp_path):
    import pymupdf

    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Apolice D&O - Limite maximo de garantia: R$ 10.000.000,00")
    content = document.tobytes()
    document.close()

    processor = DocumentProcessor(Settings(database_path=tmp_path / "x.db"))
    bundle = processor.process("apolice.pdf", content, "application/pdf")
    assert bundle.document.page_count == 1
    assert "Limite maximo" in bundle.pages[0].text
