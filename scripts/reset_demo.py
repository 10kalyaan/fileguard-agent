from pathlib import Path
import shutil


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_FOLDER = PROJECT_ROOT / "demo_files" / "messy_downloads"
ORGANIZED_FOLDER = PROJECT_ROOT / "Organized"
DB_PATH = PROJECT_ROOT / "fileguard.db"

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


def reset_demo() -> None:
    if ORGANIZED_FOLDER.exists():
        shutil.rmtree(ORGANIZED_FOLDER)

    if DB_PATH.exists():
        DB_PATH.unlink()

    DEMO_FOLDER.mkdir(parents=True, exist_ok=True)
    for path in DEMO_FOLDER.iterdir():
        if path.is_file():
            path.unlink()

    for filename in DEMO_FILES:
        (DEMO_FOLDER / filename).touch()


def main() -> None:
    reset_demo()
    print(f"Demo reset complete: {DEMO_FOLDER}")


if __name__ == "__main__":
    main()

