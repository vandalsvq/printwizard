"""Заменяет HTML-изображения и центрирующие обёртки на плейсхолдеры.

`<img src="..." alt="A">` → `[Иллюстрация: A]` (или `[Иллюстрация]` без alt).
`<p align="center"> ... </p>` → внутреннее содержимое без обёртки.
Markdown-изображения `![alt](url)` тоже преобразуются в плейсхолдер.
"""

import re


_IMG_TAG_RE = re.compile(r"<img\b[^>]*?/?>", re.IGNORECASE)
_ALT_RE = re.compile(r'alt\s*=\s*"([^"]*)"', re.IGNORECASE)
_MD_IMG_RE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
_P_CENTER_OPEN_RE = re.compile(r"<p\s+align\s*=\s*\"center\"\s*>", re.IGNORECASE)
_P_CLOSE_RE = re.compile(r"</p>", re.IGNORECASE)
_BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)


def _img_replace(match: re.Match) -> str:
    alt_match = _ALT_RE.search(match.group(0))
    alt = (alt_match.group(1).strip() if alt_match else "")
    return f"[Иллюстрация: {alt}]" if alt else "[Иллюстрация]"


def _md_img_replace(match: re.Match) -> str:
    alt = (match.group(1) or "").strip()
    return f"[Иллюстрация: {alt}]" if alt else "[Иллюстрация]"


def apply(text: str) -> str:
    """Заменить теги изображений и удалить центрирующие p-wrappers."""
    text = _IMG_TAG_RE.sub(_img_replace, text)
    text = _MD_IMG_RE.sub(_md_img_replace, text)
    text = _P_CENTER_OPEN_RE.sub("", text)
    text = _P_CLOSE_RE.sub("", text)
    text = _BR_RE.sub(" ", text)
    return text
