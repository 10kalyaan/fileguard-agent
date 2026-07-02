import argparse
from pathlib import Path
import sys

from fileguard.config import get_claude_config
from fileguard.db import approve_plan, get_audit_log, get_plan, save_plan
from fileguard.executor import execute_plan
from fileguard.planner import create_plan
from fileguard.rollback import rollback_plan
from fileguard.scanner import scan_folder


DEMO_FILES = (
    "Kalyaan_Resume_Final.pdf",
    "Sarvam_Backend_Takehome.pdf",
    "rent_receipt_june.pdf",
    "Screenshot_2026_06_22.png",
    "kafka_project.zip",
    "main.py",
    "bank_statement.xlsx",
    "random_download.bin",
    "lecture_notes.txt",
    "setup_installer.exe",
)


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    try:
        args.handler(args)
    except (FileNotFoundError, KeyError, NotADirectoryError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def run_preview(args: argparse.Namespace) -> None:
    source_folder = Path(args.path)
    output_root = Path(args.output_root)
    db_path = Path(args.db)
    smart_requested = (args.smart or args.claude) and not args.no_claude
    config = get_claude_config()
    use_claude = False

    if smart_requested:
        if not config["enabled"]:
            print("Smart mode requested, but Claude is disabled. Using rule-based classification.")
        elif not config["api_key"]:
            print("Smart mode requested, but ANTHROPIC_API_KEY is missing. Using rule-based classification.")
        else:
            use_claude = True

    files = scan_folder(source_folder)
    moves = create_plan(files, output_root, use_claude=use_claude, claude_config=config)
    plan_id = save_plan(db_path, source_folder, output_root, moves)

    print(f"Plan ID: {plan_id}")
    print(f"Files scanned: {len(files)}")
    if smart_requested:
        _print_smart_summary(moves, config, use_claude)
    print()
    _print_moves(moves)
    print()
    print("Dry run only. No files were moved.")


def run_show_plan(args: argparse.Namespace) -> None:
    plan = get_plan(Path(args.db), args.plan_id)

    print(f"Plan ID: {plan['id']}")
    print(f"Source folder: {plan['source_folder']}")
    print(f"Output root: {plan['output_root']}")
    print(f"Status: {plan['status']}")
    print(f"Created at: {plan['created_at']}")
    if plan.get("approved_at"):
        print(f"Approved at: {plan['approved_at']}")
    if plan.get("executed_at"):
        print(f"Executed at: {plan['executed_at']}")
    if plan.get("rolled_back_at"):
        print(f"Rolled back at: {plan['rolled_back_at']}")
    print(f"Proposed/final moves: {len(plan['moves'])}")
    print()
    _print_moves(plan["moves"])
    print()
    if plan["status"] in {"previewed", "approved"}:
        print("No files are moved until an approved plan is executed.")


def run_approve(args: argparse.Namespace) -> None:
    message = approve_plan(Path(args.db), args.plan_id)
    print(message)
    print("No files were moved.")


def run_execute(args: argparse.Namespace) -> None:
    summary = execute_plan(Path(args.db), args.plan_id)

    print(f"Plan ID: {summary['plan_id']}")
    print(f"Moved: {summary['moved_count']}")
    print(f"Skipped: {summary['skipped_count']}")
    print(f"Failed: {summary['failed_count']}")
    print()

    for moved_file in summary["moved_files"]:
        print(f"- moved: {moved_file['source_path']}")
        print(f"  -> {moved_file['destination_path']}")

    for skipped_file in summary["skipped_files"]:
        print(f"- skipped: {skipped_file['source_path']}")
        print(f"  reason: {skipped_file['message']}")

    for failed_file in summary["failed_files"]:
        print(f"- failed: {failed_file['source_path']}")
        print(f"  reason: {failed_file['message']}")


def run_audit(args: argparse.Namespace) -> None:
    entries = get_audit_log(Path(args.db), args.plan_id)

    if not entries:
        print(f"No audit entries found for plan: {args.plan_id}")
        return

    for entry in entries:
        print(f"- {entry['timestamp']} [{entry['status']}] {entry['action']}")
        if entry["source_path"]:
            print(f"  source: {entry['source_path']}")
        if entry["destination_path"]:
            print(f"  destination: {entry['destination_path']}")
        if entry["message"]:
            print(f"  message: {entry['message']}")


def run_rollback(args: argparse.Namespace) -> None:
    summary = rollback_plan(Path(args.db), args.plan_id)

    print(f"Plan ID: {summary['plan_id']}")
    print(f"Restored: {summary['restored_count']}")
    print(f"Skipped: {summary['skipped_count']}")
    print(f"Failed: {summary['failed_count']}")
    print()

    for restored_file in summary["restored_files"]:
        print(f"- restored: {restored_file['source_path']}")
        print(f"  -> {restored_file['destination_path']}")

    for skipped_file in summary["skipped_files"]:
        print(f"- skipped: {skipped_file['source_path']}")
        print(f"  reason: {skipped_file['message']}")

    for failed_file in summary["failed_files"]:
        print(f"- failed: {failed_file['source_path']}")
        print(f"  reason: {failed_file['message']}")


def run_reset_demo(_args: argparse.Namespace) -> None:
    demo_folder = Path("demo_files") / "messy_downloads"
    demo_folder.mkdir(parents=True, exist_ok=True)

    for filename in DEMO_FILES:
        (demo_folder / filename).touch(exist_ok=True)

    print(f"Demo files are present in {demo_folder}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FileGuard Agent dry-run file organization planner")
    subparsers = parser.add_subparsers(required=True)

    preview_parser = subparsers.add_parser("preview", help="Scan a folder and create a dry-run movement plan")
    preview_parser.add_argument("--path", required=True, help="Folder to scan")
    preview_parser.add_argument("--output-root", default="./Organized", help="Root folder for proposed destinations")
    preview_parser.add_argument("--db", default="./fileguard.db", help="SQLite database path")
    preview_parser.add_argument("--smart", action="store_true", help="Use optional Claude classification for low-confidence files")
    preview_parser.add_argument("--claude", action="store_true", help="Alias for --smart")
    preview_parser.add_argument("--no-claude", action="store_true", help="Disable Claude even if --smart is present")
    preview_parser.set_defaults(handler=run_preview)

    show_parser = subparsers.add_parser("show-plan", help="Display a saved dry-run plan")
    show_parser.add_argument("plan_id", help="Plan ID to load")
    show_parser.add_argument("--db", default="./fileguard.db", help="SQLite database path")
    show_parser.set_defaults(handler=run_show_plan)

    approve_parser = subparsers.add_parser("approve", help="Approve a saved preview plan")
    approve_parser.add_argument("plan_id", help="Plan ID to approve")
    approve_parser.add_argument("--db", default="./fileguard.db", help="SQLite database path")
    approve_parser.set_defaults(handler=run_approve)

    execute_parser = subparsers.add_parser("execute", help="Execute an approved plan")
    execute_parser.add_argument("plan_id", help="Plan ID to execute")
    execute_parser.add_argument("--db", default="./fileguard.db", help="SQLite database path")
    execute_parser.set_defaults(handler=run_execute)

    audit_parser = subparsers.add_parser("audit", help="Display audit log entries for a plan")
    audit_parser.add_argument("plan_id", help="Plan ID to audit")
    audit_parser.add_argument("--db", default="./fileguard.db", help="SQLite database path")
    audit_parser.set_defaults(handler=run_audit)

    rollback_parser = subparsers.add_parser("rollback", help="Rollback an executed plan")
    rollback_parser.add_argument("plan_id", help="Plan ID to rollback")
    rollback_parser.add_argument("--db", default="./fileguard.db", help="SQLite database path")
    rollback_parser.set_defaults(handler=run_rollback)

    reset_demo_parser = subparsers.add_parser("reset-demo", help="Recreate the original empty demo files")
    reset_demo_parser.set_defaults(handler=run_reset_demo)

    return parser


def _print_moves(moves: list) -> None:
    if not moves:
        print("No files found to plan.")
        return

    for move in moves:
        source_path = _field(move, "source_path")
        destination_path = _field(move, "destination_path")
        confidence = _field(move, "confidence")
        reason = _field(move, "reason")
        print(f"- {source_path}")
        print(f"  -> {destination_path}")
        print(f"  confidence: {confidence:.2f}")
        print(f"  reason: {reason}")


def _print_smart_summary(moves: list, config: dict, use_claude: bool) -> None:
    claude_count = _count_classifier(moves, "claude")
    fallback_count = _count_classifier(moves, "rules_fallback")
    rules_count = _count_classifier(moves, "rules")
    max_calls = config.get("max_api_calls_per_run", 0)

    print(f"Claude calls used: {claude_count + fallback_count} / {max_calls if use_claude else 0}")
    print(f"Rule-based classifications: {rules_count}")
    print(f"Claude classifications: {claude_count}")
    print(f"Fallbacks: {fallback_count}")


def _count_classifier(moves: list, classifier: str) -> int:
    return sum(1 for move in moves if _field(move, "classifier") == classifier)


def _field(item: object, field_name: str):
    if isinstance(item, dict):
        return item[field_name]

    return getattr(item, field_name)


if __name__ == "__main__":
    main()
