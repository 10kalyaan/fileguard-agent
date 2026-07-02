from datetime import datetime
from pathlib import Path
import sqlite3

from fileguard.models import PlannedMove


VALID_PLAN_STATUSES = {"previewed", "approved", "executed", "failed", "rolled_back"}


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
                created_at TEXT NOT NULL,
                approved_at TEXT,
                executed_at TEXT,
                rolled_back_at TEXT
            )
            """
        )
        _add_column_if_missing(connection, "plans", "approved_at", "TEXT")
        _add_column_if_missing(connection, "plans", "executed_at", "TEXT")
        _add_column_if_missing(connection, "plans", "rolled_back_at", "TEXT")
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
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id TEXT NOT NULL,
                action TEXT NOT NULL,
                source_path TEXT,
                destination_path TEXT,
                status TEXT NOT NULL,
                message TEXT,
                timestamp TEXT NOT NULL
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
            SELECT id, source_folder, output_root, status, created_at, approved_at, executed_at, rolled_back_at
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


def approve_plan(db_path: Path, plan_id: str) -> str:
    init_db(db_path)
    with sqlite3.connect(db_path) as connection:
        row = connection.execute("SELECT status FROM plans WHERE id = ?", (plan_id,)).fetchone()
        if row is None:
            raise KeyError(f"Plan not found: {plan_id}")

        status = row[0]
        if status == "previewed":
            approved_at = datetime.now().isoformat(timespec="seconds")
            connection.execute(
                """
                UPDATE plans
                SET status = ?, approved_at = ?
                WHERE id = ?
                """,
                ("approved", approved_at, plan_id),
            )
            message = f"Plan approved: {plan_id}"
            _add_audit_log_with_connection(
                connection,
                plan_id=plan_id,
                action="plan_approved",
                status="approved",
                message=message,
            )
            return message

        if status == "approved":
            return f"Plan is already approved: {plan_id}"

        if status == "executed":
            raise ValueError(f"Plan has already been executed and cannot be approved again: {plan_id}")

        if status == "failed":
            raise ValueError(f"Plan failed and cannot be approved: {plan_id}")

        if status == "rolled_back":
            raise ValueError(f"Plan has already been rolled back and cannot be approved: {plan_id}")

    raise ValueError(f"Plan has unsupported status '{status}': {plan_id}")


def update_plan_status(db_path: Path, plan_id: str, status: str) -> None:
    if status not in VALID_PLAN_STATUSES:
        raise ValueError(f"Unsupported plan status: {status}")

    init_db(db_path)
    timestamp_field = None
    if status == "approved":
        timestamp_field = "approved_at"
    elif status in {"executed", "failed"}:
        timestamp_field = "executed_at"
    elif status == "rolled_back":
        timestamp_field = "rolled_back_at"

    now = datetime.now().isoformat(timespec="seconds")
    with sqlite3.connect(db_path) as connection:
        if timestamp_field is None:
            cursor = connection.execute("UPDATE plans SET status = ? WHERE id = ?", (status, plan_id))
        else:
            cursor = connection.execute(
                f"UPDATE plans SET status = ?, {timestamp_field} = ? WHERE id = ?",
                (status, now, plan_id),
            )

        if cursor.rowcount == 0:
            raise KeyError(f"Plan not found: {plan_id}")


def update_planned_move_destination(
    db_path: Path,
    plan_id: str,
    source_path: str,
    destination_path: str,
) -> None:
    init_db(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            UPDATE planned_moves
            SET destination_path = ?
            WHERE plan_id = ? AND source_path = ?
            """,
            (destination_path, plan_id, source_path),
        )


def mark_plan_rolled_back(db_path: Path, plan_id: str) -> None:
    update_plan_status(db_path, plan_id, "rolled_back")


def add_audit_log(
    db_path: Path,
    plan_id: str,
    action: str,
    status: str,
    message: str = "",
    source_path: str | None = None,
    destination_path: str | None = None,
) -> None:
    init_db(db_path)
    with sqlite3.connect(db_path) as connection:
        _add_audit_log_with_connection(
            connection,
            plan_id=plan_id,
            action=action,
            status=status,
            message=message,
            source_path=source_path,
            destination_path=destination_path,
        )


def get_audit_log(db_path: Path, plan_id: str) -> list[dict]:
    init_db(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT id, plan_id, action, source_path, destination_path, status, message, timestamp
            FROM audit_log
            WHERE plan_id = ?
            ORDER BY id
            """,
            (plan_id,),
        ).fetchall()

    return [dict(row) for row in rows]


def _plan_exists(connection: sqlite3.Connection, plan_id: str) -> bool:
    row = connection.execute("SELECT 1 FROM plans WHERE id = ?", (plan_id,)).fetchone()
    return row is not None


def _add_column_if_missing(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_type: str,
) -> None:
    columns = {
        row[1]
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    }
    if column_name not in columns:
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


def _add_audit_log_with_connection(
    connection: sqlite3.Connection,
    plan_id: str,
    action: str,
    status: str,
    message: str = "",
    source_path: str | None = None,
    destination_path: str | None = None,
) -> None:
    connection.execute(
        """
        INSERT INTO audit_log (
            plan_id,
            action,
            source_path,
            destination_path,
            status,
            message,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            plan_id,
            action,
            source_path,
            destination_path,
            status,
            message,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
