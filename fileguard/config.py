import os


CLASSIFICATION_MODES = ("claude-first", "rules-only", "low-confidence")
DEFAULT_CLASSIFICATION_MODE = "claude-first"

ALLOWED_SEMANTIC_FOLDERS = [
    "Resumes",
    "Job Applications",
    "Finance",
    "Academic",
    "Certificates",
    "Screenshots",
    "Projects",
    "Installers",
    "Logs",
    "Misc",
]


def get_claude_config() -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    enabled_setting = os.getenv("FILEGUARD_CLAUDE_ENABLED", "auto").strip().lower()
    if enabled_setting not in {"true", "false", "auto"}:
        enabled_setting = "auto"

    return {
        "classification_mode": _get_classification_mode(),
        "enabled": _resolve_claude_enabled(enabled_setting, api_key),
        "enabled_setting": enabled_setting,
        "api_key": api_key,
        "model": os.getenv("FILEGUARD_CLAUDE_MODEL", "claude-haiku-4-5-20251001"),
        "classify_if_confidence_below": _get_float_env("FILEGUARD_CLAUDE_THRESHOLD", 0.75),
        "max_api_calls_per_run": _get_int_env("FILEGUARD_MAX_CLAUDE_CALLS", 50),
        "max_estimated_cost_usd": _get_float_env("FILEGUARD_MAX_ESTIMATED_COST_USD", 0.25),
    }


def claude_is_available(config: dict) -> bool:
    return bool(config.get("enabled") and config.get("api_key"))


def _resolve_claude_enabled(enabled_setting: str, api_key: str | None) -> bool:
    if enabled_setting == "false":
        return False

    if enabled_setting == "true":
        return True

    return bool(api_key)


def _get_classification_mode() -> str:
    mode = os.getenv("FILEGUARD_CLASSIFICATION_MODE", DEFAULT_CLASSIFICATION_MODE).strip().lower()
    if mode not in CLASSIFICATION_MODES:
        return DEFAULT_CLASSIFICATION_MODE

    return mode


def _get_float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _get_int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default
