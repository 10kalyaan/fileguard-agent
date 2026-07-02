from pathlib import Path
import shutil

from fileguard.db import (
    add_audit_log,
    get_plan,
    update_plan_status,
    update_planned_move_destination,
)
from fileguard.safety import validate_move_operation


def execute_plan(db_path: Path, plan_id: str) -> dict:
    plan = get_plan(db_path, plan_id)
    if plan["status"] != "approved":
        raise ValueError(f"Plan must be approved before execution. Current status: {plan['status']}")

    summary = {
        "plan_id": plan_id,
        "moved_count": 0,
        "skipped_count": 0,
        "failed_count": 0,
        "moved_files": [],
        "skipped_files": [],
        "failed_files": [],
    }

    for move in plan["moves"]:
        source_path = Path(move["source_path"])
        planned_destination = Path(move["destination_path"])
        output_root = Path(plan["output_root"])

        try:
            final_destination = get_safe_destination_path(planned_destination)
            validate_move_operation(source_path, final_destination, output_root)
        except ValueError as exc:
            message = str(exc)
            summary["skipped_count"] += 1
            summary["skipped_files"].append(
                {
                    "source_path": str(source_path),
                    "destination_path": str(planned_destination),
                    "message": message,
                }
            )
            add_audit_log(
                db_path,
                plan_id,
                action="file_skipped",
                status="skipped",
                message=message,
                source_path=str(source_path),
                destination_path=str(planned_destination),
            )
            continue

        try:
            final_destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), str(final_destination))
            update_planned_move_destination(db_path, plan_id, str(source_path), str(final_destination))

            message = f"Moved file to {final_destination}"
            summary["moved_count"] += 1
            summary["moved_files"].append(
                {
                    "source_path": str(source_path),
                    "destination_path": str(final_destination),
                    "message": message,
                }
            )
            add_audit_log(
                db_path,
                plan_id,
                action="file_moved",
                status="moved",
                message=message,
                source_path=str(source_path),
                destination_path=str(final_destination),
            )
        except Exception as exc:
            message = f"Failed to move file: {exc}"
            summary["failed_count"] += 1
            summary["failed_files"].append(
                {
                    "source_path": str(source_path),
                    "destination_path": str(planned_destination),
                    "message": message,
                }
            )
            add_audit_log(
                db_path,
                plan_id,
                action="file_failed",
                status="failed",
                message=message,
                source_path=str(source_path),
                destination_path=str(planned_destination),
            )

    if summary["moved_count"] == 0 and (summary["skipped_count"] > 0 or summary["failed_count"] > 0):
        update_plan_status(db_path, plan_id, "failed")
        add_audit_log(
            db_path,
            plan_id,
            action="plan_failed",
            status="failed",
            message=(
                "Execution failed because no files were moved. "
                f"Skipped: {summary['skipped_count']}; failed: {summary['failed_count']}."
            ),
        )
    elif summary["failed_count"] == 0:
        update_plan_status(db_path, plan_id, "executed")
        add_audit_log(
            db_path,
            plan_id,
            action="plan_executed",
            status="executed",
            message=f"Execution completed with {summary['moved_count']} moved and {summary['skipped_count']} skipped.",
        )
    else:
        update_plan_status(db_path, plan_id, "executed")
        add_audit_log(
            db_path,
            plan_id,
            action="plan_executed",
            status="executed",
            message=(
                f"Execution completed with {summary['moved_count']} moved, "
                f"{summary['skipped_count']} skipped, and {summary['failed_count']} failed."
            ),
        )

    return summary


def get_safe_destination_path(destination_path: Path) -> Path:
    if not destination_path.exists():
        return destination_path

    parent = destination_path.parent
    stem = destination_path.stem
    suffix = destination_path.suffix
    counter = 2

    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
