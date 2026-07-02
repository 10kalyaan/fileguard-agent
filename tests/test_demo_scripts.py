from pathlib import Path
import sys


def test_reset_demo_creates_demo_files_and_removes_local_outputs(tmp_path, monkeypatch) -> None:
    scripts_path = Path(__file__).resolve().parents[1] / "scripts"
    sys.path.insert(0, str(scripts_path))
    try:
        import reset_demo

        monkeypatch.setattr(reset_demo, "PROJECT_ROOT", tmp_path)
        monkeypatch.setattr(reset_demo, "DEMO_FOLDER", tmp_path / "demo_files" / "messy_downloads")
        monkeypatch.setattr(reset_demo, "ORGANIZED_FOLDER", tmp_path / "Organized")
        monkeypatch.setattr(reset_demo, "DB_PATH", tmp_path / "fileguard.db")

        reset_demo.ORGANIZED_FOLDER.mkdir()
        (reset_demo.ORGANIZED_FOLDER / "moved.txt").write_text("moved")
        reset_demo.DB_PATH.write_text("db")

        reset_demo.reset_demo()

        names = {path.name for path in reset_demo.DEMO_FOLDER.iterdir()}
        assert set(reset_demo.DEMO_FILES) == names
        assert not reset_demo.ORGANIZED_FOLDER.exists()
        assert not reset_demo.DB_PATH.exists()
    finally:
        sys.path.remove(str(scripts_path))

