from fileguard.keyword_classifier import classify_keywords


def test_classify_keywords_returns_semantic_folder_for_match() -> None:
    folder, confidence, reason = classify_keywords("Kalyaan_Resume_Final.pdf", "Documents/PDFs")

    assert folder == "Resumes"
    assert confidence == 0.9
    assert "resume" in reason


def test_classify_keywords_returns_misc_without_match() -> None:
    folder, confidence, reason = classify_keywords("random_download.bin", "Review Needed")

    assert folder == "Misc"
    assert confidence == 0.5
    assert "No filename keyword matched" in reason

