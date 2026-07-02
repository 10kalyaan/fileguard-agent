from pathlib import Path

import pytest

from fileguard.scanner import scan_folder


def test_scan_folder_scans_direct_files_and_ignores_directories(tmp_path: Path) -> None:
    file_path = tmp_path / "Report.PDF"
    file_path.write_text("demo")
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    (nested_dir / "ignored.txt").write_text("ignored")

    files = scan_folder(tmp_path)

    assert len(files) == 1
    assert files[0].name == "Report.PDF"
    assert files[0].source_path == str(file_path.resolve())
    assert files[0].extension == ".pdf"
    assert files[0].size_bytes == 4


def test_scan_folder_raises_for_missing_path(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Folder does not exist"):
        scan_folder(tmp_path / "missing")


def test_scan_folder_raises_for_non_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("demo")

    with pytest.raises(NotADirectoryError, match="Path is not a directory"):
        scan_folder(file_path)

