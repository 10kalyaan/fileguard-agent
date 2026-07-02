from pathlib import Path

import pytest

from fileguard.db import approve_plan, get_audit_log, get_plan, save_plan, update_plan_status
from fileguard.models import PlannedMove


def test_database_saves_and_retrieves_plan(tmp_path: Path) -> None:
    db_path = tmp_path / "fileguard.db"
    move = PlannedMove(
        source_path=str(tmp_path / "source.pdf"),
        destination_path=str(tmp_path / "Organized" / "Documents" / "PDFs" / "Misc" / "source.pdf"),
        filename="source.pdf",
        extension=".pdf",
        top_level_folder="Documents/PDFs",
        semantic_folder="Misc",
        classifier="extension+keyword",
        confidence=0.5,
        reason="test reason",
    )

    plan_id = save_plan(db_path, tmp_path, tmp_path / "Organized", [move])
    plan = get_plan(db_path, plan_id)

    assert plan["id"] == plan_id
    assert plan["status"] == "previewed"
    assert plan["source_folder"] == str(tmp_path)
    assert len(plan["moves"]) == 1
    assert plan["moves"][0]["filename"] == "source.pdf"
    assert plan["moves"][0]["reason"] == "test reason"


def test_previewed_plan_can_be_approved(tmp_path: Path) -> None:
    db_path = tmp_path / "fileguard.db"
    plan_id = save_plan(db_path, tmp_path, tmp_path / "Organized", [])

    message = approve_plan(db_path, plan_id)
    plan = get_plan(db_path, plan_id)

    assert message == f"Plan approved: {plan_id}"
    assert plan["status"] == "approved"
    assert plan["approved_at"] is not None


def test_approving_nonexistent_plan_raises_clear_error(tmp_path: Path) -> None:
    with pytest.raises(KeyError, match="Plan not found"):
        approve_plan(tmp_path / "fileguard.db", "missing")


def test_executed_plan_cannot_be_approved_again(tmp_path: Path) -> None:
    db_path = tmp_path / "fileguard.db"
    plan_id = save_plan(db_path, tmp_path, tmp_path / "Organized", [])
    update_plan_status(db_path, plan_id, "executed")

    with pytest.raises(ValueError, match="already been executed"):
        approve_plan(db_path, plan_id)


def test_approval_creates_audit_log_entry(tmp_path: Path) -> None:
    db_path = tmp_path / "fileguard.db"
    plan_id = save_plan(db_path, tmp_path, tmp_path / "Organized", [])

    approve_plan(db_path, plan_id)
    entries = get_audit_log(db_path, plan_id)

    assert len(entries) == 1
    assert entries[0]["action"] == "plan_approved"
    assert entries[0]["status"] == "approved"
