from pathlib import Path
import shutil

from fileguard.db import add_audit_log, get_plan, mark_plan_rolled_back, update_plan_status


def rollback_plan(db_path: Path, plan_id: str) -> dict:
    plan = get_plan(db_path, plan_id)
    if plan["status"] != "executed":
        raise ValueError(f"Plan must be executed before rollback. Current status: {plan['status']}")

    summary = {
        "plan_id": plan_id,
        "restored_count": 0,
        "skipped_count": 0,
        "failed_count": 0,
        "restored_files": [],
        "skipped_files": [],
        "failed_files": [],
    }

    add_audit_log(
        db_path,
        plan_id,
        action="rollback_started",
        status="started",
        message=f"Rollback started for plan: {plan_id}",
    )

    for move in plan["moves"]:
        current_path = Path(move["destination_path"])
        original_source_path = Path(move["source_path"])

        if not current_path.exists():
            message = f"Current destination file does not exist: {current_path}"
            summary["skipped_count"] += 1
            summary["skipped_files"].append(
                {
                    "source_path": str(current_path),
                    "destination_path": str(original_source_path),
                    "message": message,
                }
            )
            add_audit_log(
                db_path,
                plan_id,
                action="file_restore_skipped",
                status="skipped",
                message=message,
                source_path=str(current_path),
                destination_path=str(original_source_path),
            )
            continue

        try:
            rollback_destination = get_safe_rollback_path(original_source_path)
            rollback_destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(current_path), str(rollback_destination))
            message = f"Restored file to {rollback_destination}"
            summary["restored_count"] += 1
            summary["restored_files"].append(
                {
                    "source_path": str(current_path),
                    "destination_path": str(rollback_destination),
                    "message": message,
                }
            )
            add_audit_log(
                db_path,
                plan_id,
                action="file_restored",
                status="restored",
                message=message,
                source_path=str(current_path),
                destination_path=str(rollback_destination),
            )
        except Exception as exc:
            message = f"Failed to restore file: {exc}"
            summary["failed_count"] += 1
            summary["failed_files"].append(
                {
                    "source_path": str(current_path),
                    "destination_path": str(original_source_path),
                    "message": message,
                }
            )
            add_audit_log(
                db_path,
                plan_id,
                action="file_restore_failed",
                status="failed",
                message=message,
                source_path=str(current_path),
                destination_path=str(original_source_path),
            )

    if summary["failed_count"] == 0:
        mark_plan_rolled_back(db_path, plan_id)
        add_audit_log(
            db_path,
            plan_id,
            action="plan_rolled_back",
            status="rolled_back",
            message=(
                f"Rollback completed with {summary['restored_count']} restored "
                f"and {summary['skipped_count']} skipped."
            ),
        )
    else:
        update_plan_status(db_path, plan_id, "failed")
        add_audit_log(
            db_path,
            plan_id,
            action="rollback_failed",
            status="failed",
            message=f"Rollback failed with {summary['failed_count']} failed files.",
        )

    return summary


def get_safe_rollback_path(original_source_path: Path) -> Path:
    if not original_source_path.exists():
        return original_source_path

    parent = original_source_path.parent
    stem = original_source_path.stem
    suffix = original_source_path.suffix
    counter = 2

    while True:
        candidate = parent / f"{stem}_rollback_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1

