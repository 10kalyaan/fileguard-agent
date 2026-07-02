from pathlib import Path
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

