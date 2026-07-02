from pathlib import Path

from fileguard.models import FileItem
from fileguard.planner import create_plan


def test_create_plan_builds_expected_destination_path(tmp_path: Path) -> None:
    file_item = FileItem(
        name="Kalyaan_Resume_Final.pdf",
        source_path=str((tmp_path / "Kalyaan_Resume_Final.pdf").resolve()),
        extension=".pdf",
        size_bytes=0,
        modified_time="2026-06-22T15:30:12",
    )

    moves = create_plan([file_item], Path("Organized"))

    assert len(moves) == 1
    assert moves[0].destination_path == str(Path("Organized") / "Documents" / "PDFs" / "Resumes" / file_item.name)
    assert moves[0].source_path == file_item.source_path
    assert moves[0].top_level_folder == "Documents/PDFs"
    assert moves[0].semantic_folder == "Resumes"


def test_create_plan_skips_protected_files(tmp_path: Path) -> None:
    protected_file = FileItem(
        name=".env",
        source_path=str((tmp_path / ".env").resolve()),
        extension="",
        size_bytes=0,
        modified_time="2026-06-22T15:30:12",
    )
    normal_file = FileItem(
        name="lecture_notes.txt",
        source_path=str((tmp_path / "lecture_notes.txt").resolve()),
        extension=".txt",
        size_bytes=0,
        modified_time="2026-06-22T15:30:12",
    )

    moves = create_plan([protected_file, normal_file], Path("Organized"))

    assert len(moves) == 1
    assert moves[0].filename == "lecture_notes.txt"
