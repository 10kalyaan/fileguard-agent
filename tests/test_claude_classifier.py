from types import SimpleNamespace
import sys

import pytest

from fileguard.claude_classifier import (
    ClaudeClassificationError,
    build_claude_prompt,
    classify_with_claude,
    parse_claude_response,
)
from fileguard.config import ALLOWED_SEMANTIC_FOLDERS


def test_build_claude_prompt_includes_metadata_and_rules() -> None:
    prompt = build_claude_prompt(
        "Sarvam_Backend_Takehome.pdf",
        ".pdf",
        "Documents/PDFs",
        ALLOWED_SEMANTIC_FOLDERS,
    )

    assert "Sarvam_Backend_Takehome.pdf" in prompt
    assert ".pdf" in prompt
    assert "Documents/PDFs" in prompt
    assert "Job Applications" in prompt
    assert "Return valid JSON only" in prompt
    assert "Do not invent categories" in prompt


def test_parse_claude_response_parses_valid_json() -> None:
    category, confidence, reason, needs_review = parse_claude_response(
        """
        {
            "category": "Job Applications",
            "confidence": 0.86,
            "reason": "Filename suggests a take-home assignment.",
            "needs_review": false
        }
        """,
        ALLOWED_SEMANTIC_FOLDERS,
    )

    assert category == "Job Applications"
    assert confidence == 0.86
    assert reason == "Filename suggests a take-home assignment."
    assert not needs_review


def test_parse_claude_response_rejects_invalid_json() -> None:
    with pytest.raises(ClaudeClassificationError, match="invalid JSON"):
        parse_claude_response("not json", ALLOWED_SEMANTIC_FOLDERS)


def test_parse_claude_response_rejects_confidence_outside_range() -> None:
    with pytest.raises(ClaudeClassificationError, match="between 0 and 1"):
        parse_claude_response(
            '{"category":"Misc","confidence":1.5,"reason":"x","needs_review":true}',
            ALLOWED_SEMANTIC_FOLDERS,
        )


def test_parse_claude_response_rejects_invalid_category() -> None:
    with pytest.raises(ClaudeClassificationError, match="invalid category"):
        parse_claude_response(
            '{"category":"Taxes","confidence":0.8,"reason":"x","needs_review":false}',
            ALLOWED_SEMANTIC_FOLDERS,
        )


def test_classify_with_claude_uses_mocked_anthropic_client(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeMessages:
        def create(self, **_kwargs):
            return SimpleNamespace(
                content=[
                    SimpleNamespace(
                        text=(
                            '{"category":"Projects","confidence":0.82,'
                            '"reason":"Looks like source code.","needs_review":false}'
                        )
                    )
                ]
            )

    class FakeAnthropic:
        def __init__(self, api_key: str):
            self.api_key = api_key
            self.messages = FakeMessages()

    monkeypatch.setitem(sys.modules, "anthropic", SimpleNamespace(Anthropic=FakeAnthropic))

    category, confidence, reason = classify_with_claude(
        "main.py",
        ".py",
        "Code/Python",
        ALLOWED_SEMANTIC_FOLDERS,
        api_key="test-key",
        model="test-model",
    )

    assert category == "Projects"
    assert confidence == 0.82
    assert reason == "Claude: Looks like source code."


def test_classify_with_claude_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(ClaudeClassificationError, match="ANTHROPIC_API_KEY is missing"):
        classify_with_claude("main.py", ".py", "Code/Python", ALLOWED_SEMANTIC_FOLDERS)
