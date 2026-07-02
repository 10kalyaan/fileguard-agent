from pathlib import Path

from fileguard import claude_classifier
from fileguard.claude_classifier import ClaudeClassificationError
from fileguard.config import ALLOWED_SEMANTIC_FOLDERS, get_claude_config
from fileguard.extension_classifier import classify_extension
from fileguard.keyword_classifier import classify_keywords
from fileguard.models import FileItem, PlannedMove
from fileguard.safety import validate_file_for_planning


def create_plan(
    files: list[FileItem],
    output_root: Path,
    use_claude: bool = False,
    claude_config: dict | None = None,
) -> list[PlannedMove]:
    moves: list[PlannedMove] = []
    config = claude_config or get_claude_config()
    threshold = config.get("classify_if_confidence_below", 0.75)
    max_calls = config.get("max_api_calls_per_run", 50)
    claude_calls_used = 0

    for file_item in files:
        is_safe, _reason = validate_file_for_planning(Path(file_item.source_path))
        if not is_safe:
            continue

        extension_folder, extension_confidence, extension_reason = classify_extension(file_item.extension)
        semantic_folder, keyword_confidence, keyword_reason = classify_keywords(file_item.name, extension_folder)
        classifier = "rules"
        confidence = min(extension_confidence, keyword_confidence)
        reason = f"{extension_reason}; {keyword_reason}"

        if use_claude and keyword_confidence < threshold and claude_calls_used < max_calls:
            claude_calls_used += 1
            try:
                semantic_folder, claude_confidence, claude_reason = claude_classifier.classify_with_claude(
                    filename=file_item.name,
                    extension=file_item.extension,
                    top_level_folder=extension_folder,
                    allowed_categories=ALLOWED_SEMANTIC_FOLDERS,
                    api_key=config.get("api_key"),
                    model=config.get("model"),
                )
                classifier = "claude"
                confidence = min(extension_confidence, claude_confidence)
                reason = f"{extension_reason}; {claude_reason}"
            except ClaudeClassificationError:
                classifier = "rules_fallback"
                reason = f"Claude unavailable; fallback to rules. {reason}"

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
                reason=reason,
            )
        )

    return moves
