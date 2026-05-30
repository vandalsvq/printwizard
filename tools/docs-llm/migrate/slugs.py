"""Slug'и страниц и якорей для миграции Jekyll → Astro Starlight.

Два независимых slug-алгоритма:

* `slug_for_relpath` — превращает путь файла в /docs (например
  `guide/ch_01_01.md`) в slug страницы Starlight (`guide/ch-01-01`).
  Кириллица транслитерируется, разделители → `-`. Верхнеуровневые файлы
  теряют числовой префикс сортировки (`01_guide.md` → `guide`).

* Якоря заголовков. Внутренние ссылки в исходниках указывают на
  Jekyll/kramdown-якоря (`#очередность-подготовки-полей`). Starlight
  использует github-slugger (rehype-slug), который для части заголовков
  даёт другой результат. Поэтому для каждого файла строим карту
  «старый якорь → новый якорь», прогоняя один и тот же список заголовков
  через оба алгоритма (`Slugger`).
"""

import os.path
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transform.sections import slugify as jekyll_slugify  # type: ignore  # noqa: E402


# --- Транслитерация кириллицы -------------------------------------------------

_TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def transliterate(text: str) -> str:
    """Кириллица → латиница (для slug'ов имён файлов)."""
    return "".join(_TRANSLIT.get(ch, ch) for ch in text)


def normalize_segment(segment: str) -> str:
    """Один сегмент пути → ascii-slug: lowercase, translit, non-alnum → `-`."""
    s = transliterate(segment.strip().lower())
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


_TOP_LEVEL_ORDER_PREFIX = re.compile(r"^\d+[_-]+")


def slug_for_relpath(rel: str) -> str:
    """`guide/ch_01_01.md` → `guide/ch-01-01`; `01_guide.md` → `guide`."""
    stem = rel[:-3] if rel.endswith(".md") else rel
    parts = stem.split("/")
    out = []
    for i, part in enumerate(parts):
        is_top_level_file = len(parts) == 1
        if is_top_level_file:
            part = _TOP_LEVEL_ORDER_PREFIX.sub("", part)
        out.append(normalize_segment(part))
    return "/".join(p for p in out if p)


# --- Якоря заголовков ---------------------------------------------------------

# github-slugger (rehype-slug в Starlight): lowercase, удалить набор
# пунктуации, пробелы → `-`. НЕ трогает `-`, `_`, цифры и буквы (в т.ч.
# кириллицу), НЕ схлопывает и НЕ обрезает дефисы.
_GH_PUNCT = set("\\'!\"#$%&()*+,./:;<=>?@[]^`{|}~")


def _gh_removed(ch: str) -> bool:
    """True для символов, которые github-slugger вырезает."""
    cp = ord(ch)
    return (0x2000 <= cp <= 0x206F) or (0x2E00 <= cp <= 0x2E7F) or ch in _GH_PUNCT


def github_base(value: str) -> str:
    """github-slugger без дедупликации."""
    s = value.strip().lower()
    s = "".join(ch for ch in s if not _gh_removed(ch))
    return s.replace(" ", "-")


class Slugger:
    """Slug с дедупликацией дубликатов (`-1`, `-2`, …) — как github-slugger.

    `base_fn` задаёт базовый алгоритм (github или jekyll). Счётчик
    дубликатов общий в пределах одного документа.
    """

    def __init__(self, base_fn):
        self.base_fn = base_fn
        self.seen = {}

    def slug(self, value: str) -> str:
        s = self.base_fn(value)
        if s in self.seen:
            self.seen[s] += 1
            cand = f"{s}-{self.seen[s]}"
            while cand in self.seen:
                self.seen[s] += 1
                cand = f"{s}-{self.seen[s]}"
            s = cand
        self.seen[s] = 0
        return s


def build_anchor_map(heading_texts) -> dict:
    """Карта `старый-jekyll-якорь → новый-starlight-якорь` для одного файла.

    Прогоняет список заголовков (в порядке документа, включая ведущий H1)
    через оба алгоритма синхронно — счётчики дубликатов совпадают, поэтому
    соответствие точное. Новые якоря также маппятся сами на себя, чтобы
    ссылки, уже записанные в новом формате, тоже резолвились.
    """
    old_slugger = Slugger(jekyll_slugify)
    new_slugger = Slugger(github_base)
    amap = {}
    for heading in heading_texts:
        old = old_slugger.slug(heading)
        new = new_slugger.slug(heading)
        amap[old] = new
        amap.setdefault(new, new)
    return amap
