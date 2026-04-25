"""Валидаторы сборки.

Каждый валидатор возвращает list[str] ошибок. Пустой list — все хорошо.
build.py агрегирует ошибки и завершается non-zero exit при любых.
"""

import re
from typing import Dict, List, Tuple

from builder import TOPIC_KEY_RE  # type: ignore


HTML_TAG_RE = re.compile(r"<(?!/?(?:code|pre|details|summary|br)\b)([a-z][a-z0-9]*)\b[^>]*>")
SEE_TOPIC_RE = re.compile(r"\(см\.\s*topic:\s*([^)]+?)\)")
MAX_BUNDLE_BYTES = 500 * 1024


def validate_topic_keys_unique(topics: List[dict]) -> List[str]:
    seen: Dict[str, str] = {}
    errors = []
    for entry in topics:
        key = entry["key"]
        if key in seen:
            errors.append(
                f"Duplicate topic-key: {key} в {entry['file']} "
                f"(уже занят файлом {seen[key]})"
            )
        else:
            seen[key] = entry["file"]
    return errors


def validate_topic_keys_format(topics: List[dict]) -> List[str]:
    errors = []
    for entry in topics:
        if not TOPIC_KEY_RE.match(entry["key"]):
            errors.append(
                f"Invalid topic-key format: {entry['key']} "
                f"(в {entry['file']}); должен соответствовать "
                "[а-яёa-z]+(\\.[а-яёА-ЯЁA-Za-z0-9_*]+)*"
            )
    return errors


def validate_no_html_in_output(topics: List[dict]) -> List[str]:
    errors = []
    for entry in topics:
        for match in HTML_TAG_RE.finditer(entry["body"]):
            tag = match.group(1)
            errors.append(
                f"Unknown HTML tag <{tag}> в topic '{entry['key']}' "
                f"(файл {entry['file']})"
            )
    return errors


def validate_see_also_refs(topics: List[dict]) -> List[str]:
    keys = {entry["key"] for entry in topics}
    errors = []
    for entry in topics:
        for match in SEE_TOPIC_RE.finditer(entry["body"]):
            ref = match.group(1).strip()
            if ref not in keys:
                errors.append(
                    f"Broken ref `(см. topic: {ref})` в '{entry['key']}' "
                    f"(файл {entry['file']})"
                )
    return errors


def validate_uncovered_files(uncovered: List[str]) -> List[str]:
    return [
        f"Uncovered file: {path} (добавьте в topics.json или excluded.json)"
        for path in uncovered
    ]


def validate_bundle_size(bundle_size: int) -> List[str]:
    if bundle_size > MAX_BUNDLE_BYTES:
        return [
            f"Bundle too large: {bundle_size} байт "
            f"(лимит {MAX_BUNDLE_BYTES})"
        ]
    return []


def run_all(
    topics: List[dict],
    uncovered: List[str],
    bundle_size: int,
) -> Tuple[List[str], Dict[str, int]]:
    """Запускает все валидаторы. Возвращает (errors, counts_by_validator)."""
    results = {
        "topic_keys_unique": validate_topic_keys_unique(topics),
        "topic_keys_format": validate_topic_keys_format(topics),
        "no_html_in_output": validate_no_html_in_output(topics),
        "see_also_refs": validate_see_also_refs(topics),
        "uncovered_files": validate_uncovered_files(uncovered),
        "bundle_size": validate_bundle_size(bundle_size),
    }
    errors = []
    counts = {}
    for name, errs in results.items():
        counts[name] = len(errs)
        errors.extend(errs)
    return errors, counts
