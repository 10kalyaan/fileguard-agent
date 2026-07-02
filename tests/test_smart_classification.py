from pathlib import Path

import pytest

from fileguard.claude_classifier import ClaudeClassificationError
from fileguard.models import FileItem
from fileguard.planner import create_plan


def test_create_plan_without_claude_does_not_call_claude(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def fake_classify_with_claude(**_kwargs):
        nonlocal called
        called = True
        return "Projects", 0.8, "Claude: project"

    monkeypatch.setattr("fileguard.planner.claude_classifier.classify_with_claude", fake_classify_with_claude)

    moves = create_plan([_file_item(tmp_path, "main.py", ".py")], tmp_path / "Organized")

    assert not called
    assert moves[0].classifier == "rules"
    assert moves[0].semantic_folder == "Misc"


def test_low_confidence_triggers_claude(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_classify_with_claude(**_kwargs):
        return "Projects", 0.84, "Claude: Looks like a project file."

    monkeypatch.setattr("fileguard.planner.claude_classifier.classify_with_claude", fake_classify_with_claude)

    moves = create_plan(
        [_file_item(tmp_path, "main.py", ".py")],
        tmp_path / "Organized",
        use_claude=True,
        claude_config=_config(),
    )

    assert moves[0].classifier == "claude"
    assert moves[0].semantic_folder == "Projects"
    assert "Code" in moves[0].top_level_folder


def test_high_confidence_skips_claude(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def fake_classify_with_claude(**_kwargs):
        nonlocal called
        called = True
        return "Projects", 0.84, "Claude: project"

    monkeypatch.setattr("fileguard.planner.claude_classifier.classify_with_claude", fake_classify_with_claude)

    moves = create_plan(
        [_file_item(tmp_path, "Kalyaan_Resume_Final.pdf", ".pdf")],
        tmp_path / "Organized",
        use_claude=True,
        claude_config=_config(),
    )

    assert not called
    assert moves[0].classifier == "rules"
    assert moves[0].semantic_folder == "Resumes"


def test_claude_failure_falls_back_to_rules(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_classify_with_claude(**_kwargs):
        raise ClaudeClassificationError("boom")

    monkeypatch.setattr("fileguard.planner.claude_classifier.classify_with_claude", fake_classify_with_claude)

    moves = create_plan(
        [_file_item(tmp_path, "main.py", ".py")],
        tmp_path / "Organized",
        use_claude=True,
        claude_config=_config(),
    )

    assert moves[0].classifier == "rules_fallback"
    assert moves[0].semantic_folder == "Misc"
    assert "Claude unavailable; fallback to rules." in moves[0].reason


def test_max_call_limit_is_enforced(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def fake_classify_with_claude(**_kwargs):
        nonlocal calls
        calls += 1
        return "Projects", 0.8, "Claude: project"

    monkeypatch.setattr("fileguard.planner.claude_classifier.classify_with_claude", fake_classify_with_claude)

    moves = create_plan(
        [
            _file_item(tmp_path, "main.py", ".py"),
            _file_item(tmp_path, "random_download.bin", ".bin"),
        ],
        tmp_path / "Organized",
        use_claude=True,
        claude_config=_config(max_calls=1),
    )

    assert calls == 1
    assert moves[0].classifier == "claude"
    assert moves[1].classifier == "rules"


def _file_item(tmp_path: Path, name: str, extension: str) -> FileItem:
    return FileItem(
        name=name,
        source_path=str((tmp_path / name).resolve()),
        extension=extension,
        size_bytes=0,
        modified_time="2026-06-22T15:30:12",
    )


def _config(max_calls: int = 50) -> dict:
    return {
        "enabled": True,
        "api_key": "test-key",
        "model": "test-model",
        "classify_if_confidence_below": 0.75,
        "max_api_calls_per_run": max_calls,
        "max_estimated_cost_usd": 0.25,
    }

