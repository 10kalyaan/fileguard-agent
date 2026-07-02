from pathlib import Path

import pytest

from fileguard.safety import (
    is_protected_path,
    validate_file_for_planning,
    validate_source_folder,
)


def test_protected_filenames_are_blocked(tmp_path: Path) -> None:
    is_protected, reason = is_protected_path(tmp_path / ".env")

    assert is_protected
    assert "Filename is protected" in reason


def test_ssh_paths_are_blocked(tmp_path: Path) -> None:
    is_protected, reason = is_protected_path(tmp_path / ".ssh" / "config")

    assert is_protected
    assert ".ssh" in reason


def test_git_paths_are_blocked(tmp_path: Path) -> None:
    is_protected, reason = is_protected_path(tmp_path / ".git" / "config")

    assert is_protected
    assert ".git" in reason


def test_node_modules_paths_are_blocked(tmp_path: Path) -> None:
    is_protected, reason = is_protected_path(tmp_path / "node_modules" / "package.json")

    assert is_protected
    assert "node_modules" in reason


def test_normal_temp_folder_paths_are_allowed(tmp_path: Path) -> None:
    is_protected, reason = is_protected_path(tmp_path / "downloads" / "resume.pdf")

    assert not is_protected
    assert reason == ""


def test_validate_source_folder_rejects_nonexistent_path(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="does not exist"):
        validate_source_folder(tmp_path / "missing")


def test_validate_source_folder_rejects_file_path(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("demo")

    with pytest.raises(ValueError, match="not a directory"):
        validate_source_folder(file_path)


def test_validate_source_folder_accepts_normal_directory(tmp_path: Path) -> None:
    validate_source_folder(tmp_path)


def test_validate_file_for_planning_rejects_hidden_file(tmp_path: Path) -> None:
    is_safe, reason = validate_file_for_planning(tmp_path / ".hidden")

    assert not is_safe
    assert reason
