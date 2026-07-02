from datetime import datetime
from pathlib import Path

from fileguard.models import FileItem


def scan_folder(path: Path) -> list[FileItem]:
    folder = path.expanduser()

    if not folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {folder}")

    if not folder.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {folder}")

    files: list[FileItem] = []
    for entry in sorted(folder.iterdir(), key=lambda item: item.name.lower()):
        if not entry.is_file():
            continue

        stat = entry.stat()
        files.append(
            FileItem(
                name=entry.name,
                source_path=str(entry.resolve()),
                extension=entry.suffix.lower(),
                size_bytes=stat.st_size,
                modified_time=datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
            )
        )

    return files

