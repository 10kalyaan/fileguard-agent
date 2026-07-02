from pathlib import Path

from fileguard import claude_classifier
from fileguard.config import (
    ALLOWED_SEMANTIC_FOLDERS,
    DEFAULT_CLASSIFICATION_MODE,
    CLASSIFICATION_MODES,
    claude_is_available,
    get_claude_config,
)
from fileguard.extension_classifier import classify_extension
from fileguard.keyword_classifier import classify_keywords
from fileguard.models import FileItem, PlannedMove
from fileguard.safety import validate_file_for_planning


def create_plan(
    files: list[FileItem],
    output_root: Path,
    classification_mode: str = DEFAULT_CLASSIFICATION_MODE,
    claude_config: dict | None = None,
    use_claude: bool | None = None,
) -> list[PlannedMove]:
    moves, _summary = create_plan_with_summary(
        files,
        output_root,
        classification_mode=classification_mode,
        claude_config=claude_config,
        use_claude=use_claude,
    )
    return moves


def create_plan_with_summary(
    files: list[FileItem],
    output_root: Path,
    classification_mode: str = DEFAULT_CLASSIFICATION_MODE,
    claude_config: dict | None = None,
    use_claude: bool | None = None,
) -> tuple[list[PlannedMove], dict]:
    config = claude_config or get_claude_config()
    mode = _resolve_mode(classification_mode, use_claude)
    max_calls = max(0, int(config.get("max_api_calls_per_run", 50)))
    summary = {
        "classification_mode": mode,
        "claude_available": claude_is_available(config),
        "claude_calls_used": 0,
        "max_claude_calls": max_calls,
        "claude_classifications": 0,
        "rule_classifications": 0,
        "rule_fallbacks": 0,
        "skipped_files": 0,
    }
    moves: list[PlannedMove] = []

    for file_item in files:
        is_safe, _reason = validate_file_for_planning(Path(file_item.source_path))
        if not is_safe:
            summary["skipped_files"] += 1
            continue

        extension_folder, extension_confidence, extension_reason = classify_extension(file_item.extension)
        semantic_folder, confidence, classifier, semantic_reason = _classify_semantic_folder(
            file_item=file_item,
            extension_confidence=extension_confidence,
            extension_folder=extension_folder,
            mode=mode,
            config=config,
            summary=summary,
        )
        destination_path = output_root / extension_folder / semantic_folder / file_item.name

        moves.append(
            PlannedMove(
                source_path=file_item.source_path,
                destination_path=str(destination_path),
                filename=file_item.name,
                extension=file_item.extension,
                top_level_folder=extension_folder,
                semantic_folder=semantic_folder,
                classifier=classifier,
                confidence=confidence,
                reason=f"{extension_reason}; {semantic_reason}",
            )
        )

    return moves, summary


def _classify_semantic_folder(
    file_item: FileItem,
    extension_confidence: float,
    extension_folder: str,
    mode: str,
    config: dict,
    summary: dict,
) -> tuple[str, float, str, str]:
    rule_folder, rule_confidence, rule_reason = classify_keywords(file_item.name, extension_folder)
    rule_combined_confidence = min(extension_confidence, rule_confidence)

    if mode == "rules-only":
        summary["rule_classifications"] += 1
        return rule_folder, rule_combined_confidence, "rules", rule_reason

    if mode == "low-confidence":
        threshold = config.get("classify_if_confidence_below", 0.75)
        if rule_confidence >= threshold:
            summary["rule_classifications"] += 1
            return rule_folder, rule_combined_confidence, "rules", rule_reason

        if not _can_call_claude(config, summary):
            summary["rule_classifications"] += 1
            return rule_folder, rule_combined_confidence, "rules", rule_reason

        return _try_claude_or_fallback(
            file_item=file_item,
            extension_folder=extension_folder,
            rule_folder=rule_folder,
            rule_confidence=rule_combined_confidence,
            rule_reason=rule_reason,
            config=config,
            summary=summary,
            fallback_prefix="Claude unavailable, fallback to rules",
        )

    if _can_call_claude(config, summary):
        return _try_claude_or_fallback(
            file_item=file_item,
            extension_folder=extension_folder,
            rule_folder=rule_folder,
            rule_confidence=rule_combined_confidence,
            rule_reason=rule_reason,
            config=config,
            summary=summary,
            fallback_prefix="Claude failed, fallback to rules",
        )

    summary["rule_fallbacks"] += 1
    return (
        rule_folder,
        rule_combined_confidence,
        "rules_fallback",
        f"Claude unavailable or max calls reached, fallback to rules: {rule_reason}",
    )


def _try_claude_or_fallback(
    file_item: FileItem,
    extension_folder: str,
    rule_folder: str,
    rule_confidence: float,
    rule_reason: str,
    config: dict,
    summary: dict,
    fallback_prefix: str,
) -> tuple[str, float, str, str]:
    summary["claude_calls_used"] += 1
    try:
        semantic_folder, confidence, reason = claude_classifier.classify_with_claude(
            filename=file_item.name,
            extension=file_item.extension,
            top_level_folder=extension_folder,
            allowed_categories=ALLOWED_SEMANTIC_FOLDERS,
            api_key=config.get("api_key"),
            model=config.get("model"),
        )
    except Exception:
        summary["rule_fallbacks"] += 1
        return rule_folder, rule_confidence, "rules_fallback", f"{fallback_prefix}: {rule_reason}"

    summary["claude_classifications"] += 1
    return semantic_folder, confidence, "claude", reason


def _can_call_claude(config: dict, summary: dict) -> bool:
    return claude_is_available(config) and summary["claude_calls_used"] < summary["max_claude_calls"]


def _resolve_mode(classification_mode: str, use_claude: bool | None) -> str:
    if use_claude is True:
        return "low-confidence"

    if use_claude is False and classification_mode == DEFAULT_CLASSIFICATION_MODE:
        return "rules-only"

    if classification_mode not in CLASSIFICATION_MODES:
        return DEFAULT_CLASSIFICATION_MODE

    return classification_mode
