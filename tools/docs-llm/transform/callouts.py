"""Преобразует Starlight asides в plain-текстовые параграфы для LLM-бандла.

Формат в исходнике (src/content/docs, Starlight):

    :::note[Информация]
    Текст замечания.
    :::

Преобразуется в:

    Замечание (Информация): Текст замечания.

Без заголовка (`:::note` … `:::`) → префикс без скобок: `Замечание: текст.`.
Типы asides → префиксы: note→Замечание, tip→Совет, caution→Важно, danger→Внимание.
"""

import re


_ASIDE_RE = re.compile(
    r"^:::(note|tip|caution|danger)(?:\[([^\]]*)\])?[ \t]*\r?\n(.*?)\r?\n:::[ \t]*$",
    re.MULTILINE | re.DOTALL,
)

_PREFIX = {
    "note": "Замечание",
    "tip": "Совет",
    "caution": "Важно",
    "danger": "Внимание",
}


def _replace(match: re.Match) -> str:
    kind = match.group(1)
    title = (match.group(2) or "").strip()
    body = match.group(3).strip()
    prefix = _PREFIX[kind]
    if title and body:
        return f"{prefix} ({title}): {body}"
    if title:
        return f"{prefix}: {title}"
    if body:
        return f"{prefix}: {body}"
    return prefix


def apply(text: str) -> str:
    """Заменить Starlight-asides plain-параграфами."""
    return _ASIDE_RE.sub(_replace, text)
