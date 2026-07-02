from pathlib import Path

from fileguard.extension_classifier import classify_extension
from fileguard.keyword_classifier import classify_keywords
from fileguard.models import FileItem, PlannedMove


def create_plan(files: list[FileItem], output_root: Path) -> list[PlannedMove]:
    moves: list[PlannedMove] = []

    for file_item in files:
        extension_folder, extension_confidence, extension_reason = classify_extension(file_item.extension)
        semantic_folder, keyword_confidence, keyword_reason = classify_keywords(file_item.name, extension_folder)
        destination_path = output_root / extension_folder / semantic_folder / file_item.name

        moves.append(
            PlannedMove(
                source_path=file_item.source_path,
                destination_path=str(destination_path),
                filename=file_item.name,
                extension=file_item.extension,
                top_level_folder=extension_folder,
                semantic_folder=semantic_folder,
                classifier="extension+keyword",
                confidence=min(extension_confidence, keyword_confidence),
                reason=f"{extension_reason}; {keyword_reason}",
            )
        )

    return moves

