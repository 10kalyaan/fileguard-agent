from fileguard.config import ALLOWED_SEMANTIC_FOLDERS


KEYWORD_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("resume", "cv", "curriculum"), "Resumes"),
    (("invoice", "receipt", "bill", "statement", "rent", "bank"), "Finance"),
    (("sarvam", "toddle", "takehome", "interview", "job", "application", "assignment"), "Job Applications"),
    (("certificate", "certification"), "Certificates"),
    (("screenshot", "screen shot"), "Screenshots"),
    (("notes", "exam", "course", "pes", "iisc", "college", "university"), "Academic"),
    (("project", "repo", "source"), "Projects"),
    (("setup", "installer", "install"), "Installers"),
    (("log", "error", "debug"), "Logs"),
)


def classify_keywords(filename: str, top_level_folder: str) -> tuple[str, float, str]:
    normalized = filename.lower()

    for keywords, semantic_folder in KEYWORD_RULES:
        for keyword in keywords:
            if keyword in normalized:
                return (
                    semantic_folder,
                    0.9,
                    f"Matched keyword '{keyword}' for {semantic_folder}",
                )

    return "Misc", 0.5, f"No filename keyword matched within {top_level_folder}"
