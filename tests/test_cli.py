from pathlib import Path
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
    audit = _run_cli("audit", plan_id, "--db", str(db_path))

    assert f"Plan approved: {plan_id}" in approve.stdout
    assert "Moved: 1" in execute.stdout
    assert not source_file.exists()
    assert (output_root / "Documents" / "PDFs" / "Resumes" / "resume.pdf").exists()
    assert "plan_approved" in audit.stdout
    assert "file_moved" in audit.stdout
    assert "plan_executed" in audit.stdout


def _run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "fileguard.main", *args],
        check=True,
        capture_output=True,
        text=True,
    )
