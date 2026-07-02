import argparse
from pathlib import Path

from fileguard.db import get_plan, save_plan
from fileguard.planner import create_plan
from fileguard.scanner import scan_folder


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    args.handler(args)


def run_preview(args: argparse.Namespace) -> None:
    source_folder = Path(args.path)
    output_root = Path(args.output_root)
    db_path = Path(args.db)

    files = scan_folder(source_folder)
    moves = create_plan(files, output_root)
    plan_id = save_plan(db_path, source_folder, output_root, moves)

    print(f"Plan ID: {plan_id}")
    print(f"Files scanned: {len(files)}")
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
    print(f"Proposed moves: {len(plan['moves'])}")
    print()
    _print_moves(plan["moves"])
    print()
    print("Dry run only. No files were moved.")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FileGuard Agent dry-run file organization planner")
    subparsers = parser.add_subparsers(required=True)

    preview_parser = subparsers.add_parser("preview", help="Scan a folder and create a dry-run movement plan")
    preview_parser.add_argument("--path", required=True, help="Folder to scan")
    preview_parser.add_argument("--output-root", default="./Organized", help="Root folder for proposed destinations")
    preview_parser.add_argument("--db", default="./fileguard.db", help="SQLite database path")
    preview_parser.set_defaults(handler=run_preview)

    show_parser = subparsers.add_parser("show-plan", help="Display a saved dry-run plan")
    show_parser.add_argument("plan_id", help="Plan ID to load")
    show_parser.add_argument("--db", default="./fileguard.db", help="SQLite database path")
    show_parser.set_defaults(handler=run_show_plan)

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


def _field(item: object, field_name: str):
    if isinstance(item, dict):
        return item[field_name]

    return getattr(item, field_name)


if __name__ == "__main__":
    main()

