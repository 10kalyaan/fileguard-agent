from datetime import datetime
from pathlib import Path

from fileguard.models import FileItem
from fileguard.safety import validate_file_for_planning, validate_source_folder


def scan_folder(path: Path) -> list[FileItem]:
    folder = path.expanduser()
    validate_source_folder(folder)

    files: list[FileItem] = []
    for entry in sorted(folder.iterdir(), key=lambda item: item.name.lower()):
        if not entry.is_file():
            continue

        is_safe, _reason = validate_file_for_planning(entry)
        if not is_safe:
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
