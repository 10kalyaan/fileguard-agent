from pathlib import Path

import pytest

from fileguard.db import approve_plan, get_audit_log, get_plan, save_plan
from fileguard.executor import execute_plan, get_safe_destination_path
from fileguard.models import PlannedMove


def test_unapproved_plan_cannot_be_executed(tmp_path: Path) -> None:
    db_path = tmp_path / "fileguard.db"
    plan_id = save_plan(db_path, tmp_path, tmp_path / "Organized", [])

    with pytest.raises(ValueError, match="must be approved"):
        execute_plan(db_path, plan_id)


def test_approved_plan_moves_files_and_updates_database(tmp_path: Path) -> None:
    source_folder = tmp_path / "messy"
    source_folder.mkdir()
    source_file = source_folder / "resume.pdf"
    source_file.write_text("resume")
    destination = tmp_path / "Organized" / "Documents" / "PDFs" / "Resumes" / "resume.pdf"
    db_path = tmp_path / "fileguard.db"
    plan_id = save_plan(
        db_path,
        source_folder,
        tmp_path / "Organized",
        [_planned_move(source_file, destination)],
    )
    approve_plan(db_path, plan_id)

    summary = execute_plan(db_path, plan_id)
    plan = get_plan(db_path, plan_id)

    assert summary["moved_count"] == 1
    assert summary["skipped_count"] == 0
    assert summary["failed_count"] == 0
    assert not source_file.exists()
    assert destination.exists()
    assert plan["status"] == "executed"
    assert plan["executed_at"] is not None
    assert plan["moves"][0]["destination_path"] == str(destination)


def test_get_safe_destination_path_uses_duplicate_safe_names(tmp_path: Path) -> None:
    destination = tmp_path / "resume.pdf"
    destination.write_text("existing")
    (tmp_path / "resume_2.pdf").write_text("existing")

    assert get_safe_destination_path(destination) == tmp_path / "resume_3.pdf"


def test_execute_plan_uses_duplicate_safe_destination(tmp_path: Path) -> None:
    source_folder = tmp_path / "messy"
    source_folder.mkdir()
    source_file = source_folder / "resume.pdf"
    source_file.write_text("resume")
    organized = tmp_path / "Organized" / "Documents" / "PDFs" / "Resumes"
    organized.mkdir(parents=True)
    destination = organized / "resume.pdf"
    destination.write_text("existing")
    duplicate_destination = organized / "resume_2.pdf"
    duplicate_destination.write_text("existing")
    final_destination = organized / "resume_3.pdf"
    db_path = tmp_path / "fileguard.db"
    plan_id = save_plan(
        db_path,
        source_folder,
        tmp_path / "Organized",
        [_planned_move(source_file, destination)],
    )
    approve_plan(db_path, plan_id)

    summary = execute_plan(db_path, plan_id)
    plan = get_plan(db_path, plan_id)

    assert summary["moved_count"] == 1
    assert final_destination.exists()
    assert final_destination.read_text() == "resume"
    assert plan["moves"][0]["destination_path"] == str(final_destination)


def test_execution_creates_audit_log_entries(tmp_path: Path) -> None:
    source_folder = tmp_path / "messy"
    source_folder.mkdir()
    source_file = source_folder / "resume.pdf"
    source_file.write_text("resume")
    destination = tmp_path / "Organized" / "Documents" / "PDFs" / "Resumes" / "resume.pdf"
    db_path = tmp_path / "fileguard.db"
    plan_id = save_plan(
        db_path,
        source_folder,
        tmp_path / "Organized",
        [_planned_move(source_file, destination)],
    )
    approve_plan(db_path, plan_id)

    execute_plan(db_path, plan_id)
    actions = [entry["action"] for entry in get_audit_log(db_path, plan_id)]

    assert "plan_approved" in actions
    assert "file_moved" in actions
    assert "plan_executed" in actions


def _planned_move(source_path: Path, destination_path: Path) -> PlannedMove:
    return PlannedMove(
        source_path=str(source_path),
        destination_path=str(destination_path),
        filename=source_path.name,
        extension=source_path.suffix,
        top_level_folder="Documents/PDFs",
        semantic_folder="Resumes",
        classifier="extension+keyword",
        confidence=0.9,
        reason="test move",
    )
