from insurminds.storage.repository import AnalysisRepository

from test_comparison import make_analysis


def test_repository_roundtrip(tmp_path):
    repository = AnalysisRepository(tmp_path / "analyses.db")
    analysis = make_analysis("c", "C.pdf", 5_000_000)
    repository.save_analysis(analysis, [])
    loaded = repository.get_analysis("c")
    assert loaded is not None
    assert loaded.document.filename == "C.pdf"
    assert repository.find_cached(analysis.document.sha256, analysis.model_name) is not None

