"""Преобразует Jekyll callout-блоки в plain-текстовые параграфы.

Формат в исходнике:

    {: .note-title }
    > Информация
    >
    > Текст замечания.

Преобразуется в:

    Замечание (Информация): Текст замечания.

`{: .important-title }` → префикс `Важно`.
Если в blockquote только одна строка — без скобок: `Замечание: текст.`.
"""

import re
from typing import List, Tuple


_CALLOUT_RE = re.compile(
    r"^[ \t]*\{:\s*\.(note|important)-title\s*\}\s*\r?\n"
    r"((?:^[ \t]*>.*\r?\n?)+)",
    re.MULTILINE,
)

_PREFIX = {
    "note": "Замечание",
    "important": "Важно",
}


def _strip_quote(block: str) -> List[str]:
    """Возвращает строки blockquote без префикса `>`, без пустых краёв."""
    lines = []
    for raw in block.splitlines():
        stripped = raw.lstrip()
        if not stripped.startswith(">"):
            continue
        content = stripped[1:].lstrip()
        lines.append(content)
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return lines


def _split_title_body(lines: List[str]) -> Tuple[str, str]:
    if not lines:
        return "", ""
    title = lines[0]
    rest = lines[1:]
    while rest and not rest[0]:
        rest.pop(0)
    body = " ".join(rest).strip()
    return title.strip(), body


def _replace(match: re.Match) -> str:
    kind = match.group(1)
    block = match.group(2)
    prefix = _PREFIX[kind]
    lines = _strip_quote(block)
    title, body = _split_title_body(lines)
    if title and body:
        return f"{prefix} ({title}): {body}\n"
    if title:
        return f"{prefix}: {title}\n"
    return ""


def apply(text: str) -> str:
    """Заменить Jekyll-callouts plain-параграфами."""
    return _CALLOUT_RE.sub(_replace, text)
