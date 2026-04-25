"""Резолвит Jekyll-ссылки в плейсхолдеры topic-keys.

Поддерживаемые формы:

* Markdown reference: `[текст][N]` + определение `[N]: ./path.html#anchor`
* Markdown inline: `[текст](./path.html#anchor)`
* HTML-ссылка: `<a href="./path.html#anchor">текст</a>`

Резолвер `(target_file, anchor) → topic_key | None` инъектируется снаружи.
`target_file` — относительный путь (как в href, например `./ch_02_05.html`)
или None для ссылок только с anchor (`#анкер`). Резолвер сам решает, как
сопоставить.

При успешном резолве: `текст (см. topic: <key>)`.
При неудаче: остаётся `текст`.
"""

import re
import os.path
from typing import Callable, Optional


LinkResolver = Callable[[Optional[str], Optional[str]], Optional[str]]


_REF_DEF_RE = re.compile(
    r"^\s*\[([^\]]+)\]:\s*(\S+)\s*$",
    re.MULTILINE,
)
_REF_USE_RE = re.compile(r"\[([^\[\]]+)\]\[([^\[\]]+)\]")
_INLINE_RE = re.compile(r"\[([^\[\]]+)\]\(([^()\s]+)\)")
_HTML_LINK_RE = re.compile(
    r"<a\s+[^>]*?href\s*=\s*\"([^\"]+)\"[^>]*>(.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)


def _split_url(url: str, current_file: str) -> tuple:
    """Разбивает url на (target_file_relative_to_docs, anchor).

    `current_file` — относительный путь обрабатываемого файла внутри /docs
    (например, "guide/ch_02_08.md"). Используется для резолва ссылок без
    file-части типа `#анкер`.
    """
    if "#" in url:
        path_part, anchor = url.split("#", 1)
    else:
        path_part, anchor = url, ""

    path_part = path_part.strip()
    anchor = anchor.strip() or None

    if not path_part:
        target_file = current_file
    else:
        path_part = path_part.replace(".html", ".md")
        if path_part.startswith("./") or path_part.startswith("../"):
            base_dir = os.path.dirname(current_file)
            target_file = os.path.normpath(os.path.join(base_dir, path_part))
        elif path_part.startswith("/"):
            target_file = path_part.lstrip("/")
        else:
            target_file = path_part

    target_file = target_file.replace(os.sep, "/")
    return target_file, anchor


def inline_references(text: str) -> str:
    """Заинлайнивает Markdown reference-ссылки до разбивки на секции.

    Находит все определения `[N]: url` (могут быть в конце файла),
    заменяет inline-использования `[text][N]` на `[text](url)`. Сами
    определения удаляет.

    Запускается до `split_h2_sections`, чтобы ссылки не терялись когда
    определения попадают в одну секцию, а использования — в другую.
    """
    refs = {}
    for match in _REF_DEF_RE.finditer(text):
        refs[match.group(1)] = match.group(2)
    if not refs:
        return text

    text = _REF_DEF_RE.sub("", text)

    def expand(match: re.Match) -> str:
        link_text = match.group(1)
        ref_id = match.group(2)
        url = refs.get(ref_id)
        if url is None:
            return match.group(0)
        return f"[{link_text}]({url})"

    return _REF_USE_RE.sub(expand, text)


def apply(text: str, current_file: str, resolver: LinkResolver) -> str:
    """Резолвит все ссылки в тексте через resolver."""

    refs = {}
    for match in _REF_DEF_RE.finditer(text):
        refs[match.group(1)] = match.group(2)
    text = _REF_DEF_RE.sub("", text)

    def replace_ref(match: re.Match) -> str:
        link_text = match.group(1)
        ref_id = match.group(2)
        url = refs.get(ref_id)
        if not url:
            return link_text
        target_file, anchor = _split_url(url, current_file)
        topic = resolver(target_file, anchor)
        if topic:
            return f"{link_text} (см. topic: {topic})"
        return link_text

    def replace_inline(match: re.Match) -> str:
        link_text = match.group(1)
        url = match.group(2)
        target_file, anchor = _split_url(url, current_file)
        if target_file == current_file and anchor is None and not url.startswith("#"):
            return link_text
        topic = resolver(target_file, anchor)
        if topic:
            return f"{link_text} (см. topic: {topic})"
        return link_text

    def replace_html(match: re.Match) -> str:
        url = match.group(1)
        link_text = match.group(2).strip()
        target_file, anchor = _split_url(url, current_file)
        topic = resolver(target_file, anchor)
        if topic:
            return f"{link_text} (см. topic: {topic})"
        return link_text

    text = _REF_USE_RE.sub(replace_ref, text)
    text = _INLINE_RE.sub(replace_inline, text)
    text = _HTML_LINK_RE.sub(replace_html, text)

    return text
