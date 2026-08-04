"""Разбивает body документа на секции по H2-заголовкам.

Также строит anchor-slug для каждого H2 и H3 (Jekyll-совместимо).

Jekyll использует slug = lower-case + non-word → `-` + collapse `-`.
Кириллица сохраняется. Для русских заголовков типа `ПередИнициализацией`
slug = `перединициализацией`. Для `Структура ДанныеМакета` —
`структура-данныемакета`.
"""

import re
from typing import List, Dict


_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_H3_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)


def slugify(heading: str) -> str:
    """Jekyll-style slug: lowercase, non-word→`-`, collapse и trim `-`."""
    s = heading.strip().lower()
    out = []
    for ch in s:
        if ch.isalnum() or ch == "_":
            out.append(ch)
        elif ch in (" ", "\t", "-"):
            out.append("-")
    slug = "".join(out)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def find_h1(body: str) -> str:
    """Возвращает текст H1 или пустую строку."""
    match = _H1_RE.search(body)
    return match.group(1).strip() if match else ""


def split_h2_sections(body: str) -> List[Dict]:
    """Возвращает список секций. Каждая: {heading, anchor, body, h3}.

    Содержимое до первого H2 (и сам H1) отбрасывается из секций — оно
    считается «прологом» главы и в topic-keys не попадает.

    Короткие главы без единого H2 (QR-код, сумма прописью, пакетная печать и
    т.п.) иначе не дали бы ни одной темы и выпадали бы из корпуса — для них
    вся глава возвращается одной секцией с заголовком из H1.
    """
    h2_matches = list(_H2_RE.finditer(body))
    if not h2_matches:
        return _whole_body_section(body)

    sections: List[Dict] = []

    for i, m in enumerate(h2_matches):
        heading = m.group(1).strip()
        start = m.end()
        end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(body)
        section_body = body[start:end].strip("\n")
        sections.append({
            "heading": heading,
            "anchor": slugify(heading),
            "body": section_body,
            "h3": _extract_h3(section_body),
        })

    return sections


def _whole_body_section(body: str) -> List[Dict]:
    """Глава без H2 — одна секция: заголовок из H1, тело без строки H1."""
    heading = find_h1(body)
    if not heading:
        return []

    section_body = _H1_RE.sub("", body, count=1).strip("\n")
    if not section_body.strip():
        return []

    return [{
        "heading": heading,
        "anchor": slugify(heading),
        "body": section_body,
        "h3": _extract_h3(section_body),
    }]


def _extract_h3(section_body: str) -> List[Dict]:
    """Внутри секции находит H3 — для anchor-резолва ссылок."""
    h3 = []
    for m in _H3_RE.finditer(section_body):
        heading = m.group(1).strip()
        h3.append({
            "heading": heading,
            "anchor": slugify(heading),
        })
    return h3
