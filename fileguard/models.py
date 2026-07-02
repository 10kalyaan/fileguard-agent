from dataclasses import dataclass


@dataclass(frozen=True)
class FileItem:
    name: str
    source_path: str
    extension: str
    size_bytes: int
    modified_time: str


@dataclass(frozen=True)
class ClassificationResult:
    top_level_folder: str
    semantic_folder: str
    classifier: str
    confidence: float
    reason: str


@dataclass(frozen=True)
class PlannedMove:
    source_path: str
    destination_path: str
    filename: str
    extension: str
    top_level_folder: str
    semantic_folder: str
    classifier: str
    confidence: float
    reason: str

