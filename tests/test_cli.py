from pathlib import Path
import os
import re
import subprocess
import sys


def test_preview_command_runs_on_demo_files(tmp_path: Path) -> None:
    db_path = tmp_path / "fileguard.db"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "fileguard.main",
            "preview",
            "--path",
            "./demo_files/messy_downloads",
            "--db",
            str(db_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Plan ID: plan_" in result.stdout
    assert "Files scanned: 10" in result.stdout
    assert "Classification mode: claude-first" in result.stdout
    assert "Claude-first mode selected, but Claude is unavailable." in result.stdout
    assert "Dry run only. No files were moved." in result.stdout
    assert db_path.exists()


def test_approve_execute_and_audit_commands_work(tmp_path: Path) -> None:
    source_folder = tmp_path / "messy"
    source_folder.mkdir()
    source_file = source_folder / "resume.pdf"
    source_file.write_text("resume")
    output_root = tmp_path / "Organized"
    db_path = tmp_path / "fileguard.db"

    preview = _run_cli(
        "preview",
        "--path",
        str(source_folder),
        "--output-root",
        str(output_root),
        "--db",
        str(db_path),
    )
    plan_id = re.search(r"Plan ID: (plan_\d{8}_\d{6}(?:_\d+)?)", preview.stdout).group(1)

    approve = _run_cli("approve", plan_id, "--db", str(db_path))
    execute = _run_cli("execute", plan_id, "--db", str(db_path))
    rollback = _run_cli("rollback", plan_id, "--db", str(db_path))
    audit = _run_cli("audit", plan_id, "--db", str(db_path))

    assert f"Plan approved: {plan_id}" in approve.stdout
    assert "Moved: 1" in execute.stdout
    assert "Restored: 1" in rollback.stdout
    assert source_file.exists()
    assert not (output_root / "Documents" / "PDFs" / "Resumes" / "resume.pdf").exists()
    assert "plan_approved" in audit.stdout
    assert "file_moved" in audit.stdout
    assert "plan_executed" in audit.stdout
    assert "rollback_started" in audit.stdout
    assert "file_restored" in audit.stdout
    assert "plan_rolled_back" in audit.stdout


def test_rollback_command_refuses_unexecuted_plan(tmp_path: Path) -> None:
    source_folder = tmp_path / "messy"
    source_folder.mkdir()
    (source_folder / "resume.pdf").write_text("resume")
    db_path = tmp_path / "fileguard.db"

    preview = _run_cli(
        "preview",
        "--path",
        str(source_folder),
        "--output-root",
        str(tmp_path / "Organized"),
        "--db",
        str(db_path),
    )
    plan_id = re.search(r"Plan ID: (plan_\d{8}_\d{6}(?:_\d+)?)", preview.stdout).group(1)

    result = subprocess.run(
        [sys.executable, "-m", "fileguard.main", "rollback", plan_id, "--db", str(db_path)],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "must be executed" in result.stderr


def test_rules_only_preview_never_uses_claude(tmp_path: Path) -> None:
    db_path = tmp_path / "fileguard.db"
    env = os.environ.copy()
    env["FILEGUARD_CLAUDE_ENABLED"] = "true"
    env.pop("ANTHROPIC_API_KEY", None)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "fileguard.main",
            "preview",
            "--path",
            "./demo_files/messy_downloads",
            "--db",
            str(db_path),
            "--rules-only",
        ],
        check=True,
        capture_output=True,
        env=env,
        text=True,
    )

    assert "Classification mode: rules-only" in result.stdout
    assert "Claude calls used: 0 / 50" in result.stdout
    assert "classifier: rules" in result.stdout
    assert "Dry run only. No files were moved." in result.stdout


def test_low_confidence_preview_mode_works(tmp_path: Path) -> None:
    db_path = tmp_path / "fileguard.db"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "fileguard.main",
            "preview",
            "--path",
            "./demo_files/messy_downloads",
            "--db",
            str(db_path),
            "--low-confidence",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Classification mode: low-confidence" in result.stdout
    assert "Claude calls used: 0 / 50" in result.stdout
    assert "Dry run only. No files were moved." in result.stdout


def test_smart_preview_alias_works(tmp_path: Path) -> None:
    db_path = tmp_path / "fileguard.db"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "fileguard.main",
            "preview",
            "--path",
            "./demo_files/messy_downloads",
            "--db",
            str(db_path),
            "--smart",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Classification mode: low-confidence" in result.stdout
    assert "Plan ID: plan_" in result.stdout
    assert "Dry run only. No files were moved." in result.stdout


def test_version_command_works() -> None:
    result = _run_cli("version")

    assert "FileGuard Agent 0.7.0" in result.stdout


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "fileguard.main", *args],
        check=True,
        capture_output=True,
        text=True,
    )
