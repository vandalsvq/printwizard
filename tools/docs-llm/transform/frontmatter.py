"""Парсит и удаляет Jekyll frontmatter.

Frontmatter — блок между двумя строками `---` в начале файла. Внутри —
key: value пары (значения могут быть в кавычках). Других конструкций
(списки, вложенные мапы) у нас в /docs не встречается.

Если в теле файла нет H1 (`# ...`), но во frontmatter есть `title` —
prepend `# {title}` как H1.
"""

import re
from typing import Tuple, Dict


_FRONTMATTER_RE = re.compile(
    r"\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n",
    re.DOTALL,
)
_KV_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*?)\s*$")
_H1_RE = re.compile(r"^#\s+\S", re.MULTILINE)


def strip_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    """Возвращает (meta, body_without_frontmatter).

    meta — словарь key→value. Кавычки вокруг значений снимаются.
    Если frontmatter отсутствует — meta пустой, body == text.
    """
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text

    raw = match.group(1)
    body = text[match.end():]
    meta: Dict[str, str] = {}
    for line in raw.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        m = _KV_RE.match(line)
        if not m:
            continue
        key, value = m.group(1), m.group(2)
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        meta[key] = value
    return meta, body


def ensure_h1(body: str, meta: Dict[str, str]) -> str:
    """Если в body нет H1, prepend `# {title}` из meta."""
    if _H1_RE.search(body):
        return body
    title = meta.get("title")
    if not title:
        return body
    return f"# {title}\n\n{body.lstrip()}"


def apply(text: str) -> str:
    """Полная трансформация: снять frontmatter, гарантировать H1."""
    meta, body = strip_frontmatter(text)
    return ensure_h1(body, meta)
