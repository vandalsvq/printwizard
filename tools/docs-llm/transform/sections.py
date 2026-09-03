"""Разбивает body документа на секции по H2-заголовкам.

Также строит anchor-slug для каждого H2 и для вложенных заголовков H3–H6 —
по ним резолвятся внутристраничные ссылки вида `[текст](#анкер)`.

Slug должен совпадать с тем, что проставляет на сайте Starlight (rehype-slug
поверх github-slugger): lower-case, пунктуация выбрасывается, пробел и дефис
дают `-`. Подряд идущие дефисы НЕ схлопываются и с краёв НЕ срезаются — иначе
заголовок `Area.Method — способ вывода` даёт `areamethod-способ-вывода`
вместо `areamethod--способ-вывода` (точка выброшена, а два пробела вокруг
тире дали два дефиса), ссылка на него не находится в anchor-индексе и молча
уезжает в первую тему файла.

Кириллица сохраняется. Для русских заголовков типа `ПередИнициализацией`
slug = `перединициализацией`. Для `Структура ДанныеМакета` —
`структура-данныемакета`.
"""

import re
from typing import List, Dict, Optional


# Минимальная длина пролога главы, при которой он становится темой.
PROLOGUE_MIN_CHARS = 400

_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_SUBHEADING_RE = re.compile(r"^#{3,6}\s+(.+?)\s*$", re.MULTILINE)


def slugify(heading: str) -> str:
    """Slug как у github-slugger: lowercase, пунктуация прочь, пробел → `-`.

    Без схлопывания и без trim дефисов — см. docstring модуля.
    """
    out = []
    for ch in heading.strip().lower():
        if ch.isalnum() or ch == "_":
            out.append(ch)
        elif ch in (" ", "\t", "-"):
            out.append("-")
    return "".join(out)


def find_h1(body: str) -> str:
    """Возвращает текст H1 или пустую строку."""
    match = _H1_RE.search(body)
    return match.group(1).strip() if match else ""


def split_h2_sections(body: str) -> List[Dict]:
    """Возвращает список секций. Каждая: {heading, anchor, body, subheadings}.

    Короткие главы без единого H2 (QR-код, сумма прописью, пакетная печать и
    т.п.) иначе не дали бы ни одной темы и выпадали бы из корпуса — для них
    вся глава возвращается одной секцией с заголовком из H1.

    Содержательный пролог (текст между H1 и первым H2) становится отдельной
    секцией с заголовком из H1. Иначе теряется объяснение механизма: в главе
    «Перенос строки» единственный H2 — заключительное «Подведём итоги», а всё
    описание лежит выше и в корпус не попадало. Пролог короче
    PROLOGUE_MIN_CHARS — это вводная фраза перед оглавлением, отдельной темы
    не заслуживает.
    """
    h2_matches = list(_H2_RE.finditer(body))
    if not h2_matches:
        return _whole_body_section(body)

    sections: List[Dict] = []

    prologue = _prologue_section(body[:h2_matches[0].start()])
    if prologue:
        sections.append(prologue)

    for i, m in enumerate(h2_matches):
        heading = m.group(1).strip()
        start = m.end()
        end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(body)
        section_body = body[start:end].strip("\n")
        sections.append({
            "heading": heading,
            "anchor": slugify(heading),
            "body": section_body,
            "subheadings": _extract_subheadings(section_body),
        })

    return sections


def _prologue_section(prologue: str) -> Optional[Dict]:
    """Пролог главы как отдельная секция; None, если он короткий или пустой."""
    heading = find_h1(prologue)
    if not heading:
        return None

    section_body = _H1_RE.sub("", prologue, count=1).strip("\n")
    if len(section_body.strip()) < PROLOGUE_MIN_CHARS:
        return None

    return {
        "heading": heading,
        "anchor": slugify(heading),
        "body": section_body,
        "subheadings": _extract_subheadings(section_body),
    }


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
        "subheadings": _extract_subheadings(section_body),
    }]


def _extract_subheadings(section_body: str) -> List[Dict]:
    """Внутри секции находит заголовки H3–H6 — для anchor-резолва ссылок.

    Не только H3: в главе про наборы данных типы полей описаны на уровне H4
    (`#### Поле свойства`), и ссылки из соседних глав ведут именно туда.
    """
    found = []
    for m in _SUBHEADING_RE.finditer(section_body):
        heading = m.group(1).strip()
        found.append({
            "heading": heading,
            "anchor": slugify(heading),
        })
    return found
