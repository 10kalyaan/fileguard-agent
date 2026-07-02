from pathlib import Path


def test_openclaw_skill_file_exists_and_has_frontmatter() -> None:
    root = Path(__file__).resolve().parents[1]
    skill = root / "skills" / "fileguard-agent" / "SKILL.md"
    text = skill.read_text(encoding="utf-8")

    assert skill.exists()
    assert text.startswith("---")
    assert "name: fileguard-agent" in text
    assert "description: Safely organize local files" in text
    assert "user-invocable: true" in text


def test_openclaw_skill_mentions_required_commands() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "skills" / "fileguard-agent" / "SKILL.md").read_text(encoding="utf-8")

    assert "python -m fileguard.main preview --path <PATH> --rules-only" in text
    assert "python -m fileguard.main approve <PLAN_ID>" in text
    assert "python -m fileguard.main execute <PLAN_ID>" in text
    assert "python -m fileguard.main rollback <PLAN_ID>" in text
    assert "python -m fileguard.main audit <PLAN_ID>" in text


def test_openclaw_skill_mentions_safety_rules() -> None:
    root = Path(__file__).resolve().parents[1]
    text = (root / "skills" / "fileguard-agent" / "SKILL.md").read_text(encoding="utf-8")

    assert "Always preview first" in text
    assert "Never delete files" in text
    assert "Never overwrite files" in text
    assert "Prefer `demo_files/messy_downloads` for demos" in text
    assert "Do not ask the user to paste API keys into chat" in text
    assert "explicitly asks to execute a specific plan id" in text


def test_openclaw_docs_and_install_scripts_exist() -> None:
    root = Path(__file__).resolve().parents[1]

    assert (root / "docs" / "OPENCLAW.md").exists()
    assert (root / "scripts" / "install_openclaw_skill.ps1").exists()
    assert (root / "scripts" / "install_openclaw_skill.sh").exists()

