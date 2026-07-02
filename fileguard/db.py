from datetime import datetime
from pathlib import Path
import sqlite3

from fileguard.models import PlannedMove


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS plans (
                id TEXT PRIMARY KEY,
                source_folder TEXT NOT NULL,
                output_root TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS planned_moves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id TEXT NOT NULL,
                source_path TEXT NOT NULL,
                destination_path TEXT NOT NULL,
                filename TEXT NOT NULL,
                extension TEXT NOT NULL,
                top_level_folder TEXT NOT NULL,
                semantic_folder TEXT NOT NULL,
                classifier TEXT NOT NULL,
                confidence REAL NOT NULL,
                reason TEXT NOT NULL,
                FOREIGN KEY(plan_id) REFERENCES plans(id)
            )
            """
        )


def save_plan(db_path: Path, source_folder: Path, output_root: Path, moves: list[PlannedMove]) -> str:
    init_db(db_path)
    now = datetime.now()
    plan_id = f"plan_{now.strftime('%Y%m%d_%H%M%S')}"
    created_at = now.isoformat(timespec="seconds")

    with sqlite3.connect(db_path) as connection:
        suffix = 1
        unique_plan_id = plan_id
        while _plan_exists(connection, unique_plan_id):
            suffix += 1
            unique_plan_id = f"{plan_id}_{suffix}"

        connection.execute(
            """
            INSERT INTO plans (id, source_folder, output_root, status, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (unique_plan_id, str(source_folder), str(output_root), "previewed", created_at),
        )
        connection.executemany(
            """
            INSERT INTO planned_moves (
                plan_id,
                source_path,
                destination_path,
                filename,
                extension,
                top_level_folder,
                semantic_folder,
                classifier,
                confidence,
                reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    unique_plan_id,
                    move.source_path,
                    move.destination_path,
                    move.filename,
                    move.extension,
                    move.top_level_folder,
                    move.semantic_folder,
                    move.classifier,
                    move.confidence,
                    move.reason,
                )
                for move in moves
            ],
        )

    return unique_plan_id


def get_plan(db_path: Path, plan_id: str) -> dict:
    init_db(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        plan_row = connection.execute(
            """
            SELECT id, source_folder, output_root, status, created_at
            FROM plans
            WHERE id = ?
            """,
            (plan_id,),
        ).fetchone()

        if plan_row is None:
            raise KeyError(f"Plan not found: {plan_id}")

        move_rows = connection.execute(
            """
            SELECT
                source_path,
                destination_path,
                filename,
                extension,
                top_level_folder,
                semantic_folder,
                classifier,
                confidence,
                reason
            FROM planned_moves
            WHERE plan_id = ?
            ORDER BY id
            """,
            (plan_id,),
        ).fetchall()

    plan = dict(plan_row)
    plan["moves"] = [dict(row) for row in move_rows]
    return plan


def _plan_exists(connection: sqlite3.Connection, plan_id: str) -> bool:
    row = connection.execute("SELECT 1 FROM plans WHERE id = ?", (plan_id,)).fetchone()
    return row is not None

