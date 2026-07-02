from fileguard.extension_classifier import classify_extension


def test_classify_extension_returns_known_top_level_folder() -> None:
    folder, confidence, reason = classify_extension(".PDF")

    assert folder == "Documents/PDFs"
    assert confidence == 1.0
    assert ".pdf" in reason


def test_classify_extension_returns_review_needed_for_unknown() -> None:
    folder, confidence, reason = classify_extension(".bin")

    assert folder == "Review Needed"
    assert confidence == 0.3
    assert "Unknown extension" in reason

