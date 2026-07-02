from pathlib import Path


def test_documentation_files_exist() -> None:
    root = Path(__file__).resolve().parents[1]

    assert (root / "README.md").exists()
    assert (root / "docs" / "ARCHITECTURE.md").exists()
    assert (root / "docs" / "SAFETY.md").exists()
    assert (root / "docs" / "DEMO.md").exists()
    assert (root / "docs" / "ROADMAP.md").exists()
    assert (root / "docs" / "OPENCLAW.md").exists()


def test_readme_mentions_resume_bullet() -> None:
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")

    assert "Built a permission-aware local file organization agent" in readme
