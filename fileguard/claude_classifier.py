import json
import os

from fileguard.config import ALLOWED_SEMANTIC_FOLDERS


class ClaudeClassificationError(Exception):
    pass


def build_claude_prompt(
    filename: str,
    extension: str,
    top_level_folder: str,
    allowed_categories: list[str],
) -> str:
    categories = "\n".join(f"* {category}" for category in allowed_categories)
    return f"""You are classifying the semantic subfolder only for a safe local file organizer.

The top-level folder has already been decided by deterministic extension rules.
Do not change or reinterpret the top-level folder.

File metadata:

* filename: {filename}
* extension: {extension}
* top_level_folder: {top_level_folder}

Allowed semantic categories:

{categories}

Rules:

* Choose exactly one semantic folder from the allowed categories.
* Do not invent categories.
* If unsure, choose Misc.
* Return valid JSON only.
* Do not include markdown.

Output format:
{{
"category": "Job Applications",
"confidence": 0.86,
"reason": "Filename suggests a backend take-home assignment.",
"needs_review": false
}}"""


def parse_claude_response(text: str, allowed_categories: list[str]) -> tuple[str, float, str, bool]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ClaudeClassificationError("Claude returned invalid JSON") from exc

    category = parsed.get("category")
    confidence = parsed.get("confidence")
    reason = parsed.get("reason")
    needs_review = parsed.get("needs_review")

    if category not in allowed_categories:
        raise ClaudeClassificationError(f"Claude returned invalid category: {category}")

    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise ClaudeClassificationError("Claude confidence must be a number between 0 and 1")

    if not isinstance(reason, str):
        raise ClaudeClassificationError("Claude reason must be a string")

    if not isinstance(needs_review, bool):
        raise ClaudeClassificationError("Claude needs_review must be a boolean")

    return category, float(confidence), reason, needs_review


def classify_with_claude(
    filename: str,
    extension: str,
    top_level_folder: str,
    allowed_categories: list[str] | None = None,
    api_key: str | None = None,
    model: str | None = None,
) -> tuple[str, float, str]:
    categories = allowed_categories or ALLOWED_SEMANTIC_FOLDERS
    selected_api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    if not selected_api_key:
        raise ClaudeClassificationError("ANTHROPIC_API_KEY is missing; Claude classification is unavailable")

    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise ClaudeClassificationError("anthropic package is not installed; run pip install -r requirements.txt") from exc

    selected_model = model or os.getenv("FILEGUARD_CLAUDE_MODEL", "claude-haiku-4-5-20251001")
    prompt = build_claude_prompt(filename, extension, top_level_folder, categories)
    client = Anthropic(api_key=selected_api_key)
    response = client.messages.create(
        model=selected_model,
        max_tokens=250,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    text = _extract_text(response)
    semantic_folder, confidence, reason, _needs_review = parse_claude_response(text, categories)
    return semantic_folder, confidence, f"Claude: {reason}"


def _extract_text(response: object) -> str:
    content = getattr(response, "content", None)
    if not content:
        raise ClaudeClassificationError("Claude returned an empty response")

    first_block = content[0]
    text = getattr(first_block, "text", None)
    if not isinstance(text, str):
        raise ClaudeClassificationError("Claude response did not contain text")

    return text
