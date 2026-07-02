import os


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
    return {
        "enabled": _is_truthy(os.getenv("FILEGUARD_CLAUDE_ENABLED", "false")),
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "model": os.getenv("FILEGUARD_CLAUDE_MODEL", "claude-3-5-haiku-latest"),
        "classify_if_confidence_below": _get_float_env("FILEGUARD_CLAUDE_THRESHOLD", 0.75),
        "max_api_calls_per_run": _get_int_env("FILEGUARD_MAX_CLAUDE_CALLS", 50),
        "max_estimated_cost_usd": _get_float_env("FILEGUARD_MAX_ESTIMATED_COST_USD", 0.25),
    }


def _is_truthy(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


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

