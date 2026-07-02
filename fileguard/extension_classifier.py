EXTENSION_MAP: dict[str, tuple[str, str]] = {
    ".pdf": ("Documents", "PDFs"),
    ".docx": ("Documents", "Word"),
    ".doc": ("Documents", "Word"),
    ".txt": ("Documents", "Text"),
    ".md": ("Documents", "Markdown"),
    ".png": ("Images", "PNG"),
    ".jpg": ("Images", "JPG"),
    ".jpeg": ("Images", "JPG"),
    ".webp": ("Images", "WEBP"),
    ".zip": ("Archives", "ZIP"),
    ".rar": ("Archives", "RAR"),
    ".7z": ("Archives", "7Z"),
    ".py": ("Code", "Python"),
    ".js": ("Code", "JavaScript"),
    ".ts": ("Code", "TypeScript"),
    ".java": ("Code", "Java"),
    ".cpp": ("Code", "CPP"),
    ".c": ("Code", "C"),
    ".csv": ("Documents", "Spreadsheets"),
    ".xlsx": ("Documents", "Spreadsheets"),
    ".mp4": ("Videos", "MP4"),
    ".mov": ("Videos", "MOV"),
    ".mkv": ("Videos", "MKV"),
    ".mp3": ("Audio", "MP3"),
    ".wav": ("Audio", "WAV"),
}


def classify_extension(extension: str) -> tuple[str, float, str]:
    normalized = extension.lower()
    match = EXTENSION_MAP.get(normalized)

    if match is None:
        return "Review Needed", 0.3, f"Unknown extension: {normalized or '(none)'}"

    top_level_folder, extension_folder = match
    return (
        f"{top_level_folder}/{extension_folder}",
        1.0,
        f"Matched extension {normalized} to {top_level_folder}/{extension_folder}",
    )

