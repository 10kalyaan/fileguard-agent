import pytest


@pytest.fixture(autouse=True)
def disable_real_claude(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("FILEGUARD_CLAUDE_ENABLED", raising=False)
    monkeypatch.delenv("FILEGUARD_CLASSIFICATION_MODE", raising=False)

