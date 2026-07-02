from pathlib import Path

import pytest

from fileguard.db import approve_plan, get_audit_log, get_plan, save_plan
from fileguard.executor import execute_plan
from fileguard.models import PlannedMove
from fileguard.rollback import get_safe_rollback_path, rollback_plan


def test_executed_plan_can_be_rolled_back(tmp_path: Path) -> None:
    db_path, plan_id, source_file, destination = _executed_plan(tmp_path)

    summary = rollback_plan(db_path, plan_id)
    plan = get_plan(db_path, plan_id)

    assert summary["restored_count"] == 1
    assert source_file.exists()
    assert not destination.exists()
    assert plan["status"] == "rolled_back"
    assert plan["rolled_back_at"] is not None


def test_rollback_writes_audit_log_entries(tmp_path: Path) -> None:
    db_path, plan_id, _source_file, _destination = _executed_plan(tmp_path)

    rollback_plan(db_path, plan_id)
    actions = [entry["action"] for entry in get_audit_log(db_path, plan_id)]

    assert "rollback_started" in actions
    assert "file_restored" in actions
    assert "plan_rolled_back" in actions


def test_rollback_refuses_previewed_plans(tmp_path: Path) -> None:
    db_path = tmp_path / "fileguard.db"
    plan_id = save_plan(db_path, tmp_path, tmp_path / "Organized", [])

    with pytest.raises(ValueError, match="must be executed"):
        rollback_plan(db_path, plan_id)


def test_rollback_refuses_approved_but_not_executed_plans(tmp_path: Path) -> None:
    db_path = tmp_path / "fileguard.db"
    plan_id = save_plan(db_path, tmp_path, tmp_path / "Organized", [])
    approve_plan(db_path, plan_id)

    with pytest.raises(ValueError, match="must be executed"):
        rollback_plan(db_path, plan_id)


def test_rollback_refuses_already_rolled_back_plans(tmp_path: Path) -> None:
    db_path, plan_id, _source_file, _destination = _executed_plan(tmp_path)
    rollback_plan(db_path, plan_id)

    with pytest.raises(ValueError, match="must be executed"):
        rollback_plan(db_path, plan_id)


def test_rollback_handles_missing_destination_by_skipping(tmp_path: Path) -> None:
    db_path, plan_id, _source_file, destination = _executed_plan(tmp_path)
    destination.unlink()

    summary = rollback_plan(db_path, plan_id)
    actions = [entry["action"] for entry in get_audit_log(db_path, plan_id)]

    assert summary["restored_count"] == 0
    assert summary["skipped_count"] == 1
    assert "file_restore_skipped" in actions


def test_safe_rollback_path_uses_duplicate_safe_names(tmp_path: Path) -> None:
    original_source = tmp_path / "resume.pdf"
    original_source.write_text("existing")
    (tmp_path / "resume_rollback_2.pdf").write_text("existing")

    assert get_safe_rollback_path(original_source) == tmp_path / "resume_rollback_3.pdf"


def test_rollback_handles_source_path_conflict(tmp_path: Path) -> None:
    db_path, plan_id, source_file, destination = _executed_plan(tmp_path)
    source_file.write_text("new conflicting file")

    summary = rollback_plan(db_path, plan_id)
    restored_path = source_file.parent / "resume_rollback_2.pdf"

    assert summary["restored_count"] == 1
    assert source_file.exists()
    assert restored_path.exists()
    assert not destination.exists()


def _executed_plan(tmp_path: Path) -> tuple[Path, str, Path, Path]:
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
    return db_path, plan_id, source_file, destination


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
