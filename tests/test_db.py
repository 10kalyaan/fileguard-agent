from pathlib import Path

from fileguard.db import get_plan, save_plan
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

