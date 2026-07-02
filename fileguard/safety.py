from pathlib import Path


PROTECTED_PATH_KEYWORDS = (
    ".ssh",
    ".aws",
    ".gnupg",
    ".git",
    "node_modules",
    "__pycache__",
    "**pycache**",
    ".venv",
    "venv",
)

PROTECTED_FILENAMES = (
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_rsa.pub",
    "credentials",
    "credentials.json",
    "config.json",
)

PROTECTED_WINDOWS_PATHS = (
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
)

PROTECTED_UNIX_PATHS = (
    "/etc",
    "/usr",
    "/bin",
    "/sbin",
    "/var",
)


def is_protected_path(path: Path) -> tuple[bool, str]:
    normalized = _normalize_path(path)
    parts = [part.lower() for part in path.parts]
    filename = path.name.lower()

    for protected_path in PROTECTED_WINDOWS_PATHS + PROTECTED_UNIX_PATHS:
        protected_normalized = _normalize_path(Path(protected_path))
        if normalized == protected_normalized or normalized.startswith(f"{protected_normalized}/"):
            return True, f"Path is inside protected system location: {protected_path}"

    for keyword in PROTECTED_PATH_KEYWORDS:
        keyword_lower = keyword.lower()
        if any(keyword_lower in part for part in parts):
            return True, f"Path contains protected folder keyword: {keyword}"

    if filename in PROTECTED_FILENAMES:
        return True, f"Filename is protected: {path.name}"

    return False, ""


def validate_source_folder(path: Path) -> None:
    if not path.exists():
        raise ValueError(f"Source folder does not exist: {path}")

    if not path.is_dir():
        raise ValueError(f"Source path is not a directory: {path}")

    is_protected, reason = is_protected_path(path)
    if is_protected:
        raise ValueError(reason)


def validate_file_for_planning(path: Path) -> tuple[bool, str]:
    is_protected, reason = is_protected_path(path)
    if is_protected:
        return False, reason

    if path.name.startswith("."):
        return False, f"Hidden or sensitive file is skipped: {path.name}"

    return True, ""


def validate_move_operation(source_path: Path, destination_path: Path, output_root: Path) -> None:
    source_protected, source_reason = is_protected_path(source_path)
    if source_protected:
        raise ValueError(source_reason)

    destination_protected, destination_reason = is_protected_path(destination_path)
    if destination_protected:
        raise ValueError(destination_reason)

    if not source_path.exists():
        raise ValueError(f"Source file does not exist: {source_path}")

    if not source_path.is_file():
        raise ValueError(f"Source path is not a file: {source_path}")

    resolved_source = source_path.resolve()
    resolved_destination = destination_path.resolve(strict=False)
    resolved_output_root = output_root.resolve(strict=False)

    if resolved_source == resolved_destination:
        raise ValueError("Source and destination paths are the same")

    if not _is_relative_to(resolved_destination, resolved_output_root):
        raise ValueError(f"Destination is outside output root: {destination_path}")


def _normalize_path(path: Path) -> str:
    return str(path).replace("\\", "/").rstrip("/").lower()


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False

    return True

