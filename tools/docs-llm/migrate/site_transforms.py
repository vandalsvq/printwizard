"""Трансформации Markdown для сайта (Jekyll → Astro Starlight).

В отличие от docs-llm (схлопывает оформление в плоский текст), здесь
разметка СОХРАНЯЕТСЯ — меняется только синтаксис:

* fenced-frontmatter баг (```` ``` ```` вокруг `---`) → чистый `---`;
* callouts `{: .note-title }` + blockquote → Starlight asides `:::note[…]`;
* `<img>` / `![]()` → markdown-картинка с абсолютным путём `/img/...`;
* внутренние `.html`-ссылки → новые slug'и Starlight + новые якоря.

Переиспользуются regexp'ы из `transform.callouts` и резолвер путей
`transform.links._split_url`.
"""

import os.path
import re
import sys
from urllib.parse import unquote

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transform.links import _split_url  # type: ignore  # noqa: E402
from transform.sections import find_h1  # type: ignore  # noqa: E402


# --- Fenced-frontmatter баг ---------------------------------------------------

_FENCED_FM_RE = re.compile(
    r"\A```[a-zA-Z]*\s*\r?\n(---\s*\r?\n.*?\r?\n---[ \t]*\r?\n)```[ \t]*\r?\n",
    re.DOTALL,
)


def fix_fenced_frontmatter(text: str) -> str:
    """Снимает обёртку из тройных кавычек вокруг frontmatter, если она есть."""
    m = _FENCED_FM_RE.match(text)
    if m:
        return m.group(1) + text[m.end():]
    return text


# --- Заголовки ----------------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,6})(\s+.+?)\s*$")


def _heading_lines(lines):
    """Индексы и уровни заголовков (код-блоки пропускаются)."""
    out = []
    in_fence = False
    fence = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not in_fence and (stripped.startswith("```") or stripped.startswith("~~~")):
            in_fence = True
            fence = stripped[:3]
            continue
        if in_fence:
            if stripped.startswith(fence):
                in_fence = False
            continue
        m = _HEADING_RE.match(line)
        if m:
            out.append((i, len(m.group(1))))
    return out


def extract_headings(body: str) -> list:
    """Тексты заголовков H1–H6 в порядке документа (код-блоки пропускаются)."""
    lines = body.splitlines()
    out = []
    for i, _ in _heading_lines(lines):
        m = _HEADING_RE.match(lines[i])
        out.append(m.group(2).strip())
    return out


def normalize_headings(body: str) -> str:
    """Единый H1 на странице (его рендерит Starlight из title).

    * 1 H1 в теле → удаляем (дубль title), H2+ остаются.
    * ≥2 H1 → это секции-братья; понижаем ВСЕ заголовки на уровень
      (H1→H2 … H5→H6), сохраняя вложенность и текст.
    """
    lines = body.split("\n")
    headings = _heading_lines(lines)
    h1_idx = [i for i, lvl in headings if lvl == 1]
    if len(h1_idx) == 1:
        lines[h1_idx[0]] = None
    elif len(h1_idx) >= 2:
        for i, lvl in headings:
            m = _HEADING_RE.match(lines[i])
            lines[i] = "#" * min(lvl + 1, 6) + m.group(2)
    return "\n".join(l for l in lines if l is not None).lstrip("\n")


def derive_title(meta: dict, body: str, rel: str) -> str:
    """title из frontmatter, иначе из H1, иначе из имени файла."""
    if meta.get("title"):
        return meta["title"]
    h1 = find_h1(body)
    if h1:
        return h1
    stem = rel.rsplit("/", 1)[-1]
    if stem.endswith(".md"):
        stem = stem[:-3]
    return stem.replace("_", " ").replace("-", " ").strip() or stem


# --- Callouts → Starlight asides ----------------------------------------------

# Типы Just-the-Docs callouts (см. _config.yml) → типы Starlight asides.
_ASIDE_TYPE = {
    "note": "note", "important": "caution", "warning": "danger",
    "new": "tip", "highlight": "tip",
}
_TYPES = "|".join(_ASIDE_TYPE)

# {: .note-title } + blockquote  (с заголовком)
_CALLOUT_TITLE_RE = re.compile(
    r"^[ \t]*\{:\s*\.(" + _TYPES + r")-title\s*\}\s*\r?\n((?:^[ \t]*>.*\r?\n?)+)",
    re.MULTILINE,
)
# {: .note } + blockquote  (без заголовка)
_CALLOUT_BQ_RE = re.compile(
    r"^[ \t]*\{:\s*\.(" + _TYPES + r")\s*\}\s*\r?\n((?:^[ \t]*>.*\r?\n?)+)",
    re.MULTILINE,
)
# {: .note } + следующий абзац  (без заголовка)
_CALLOUT_P_RE = re.compile(
    r"^[ \t]*\{:\s*\.(" + _TYPES + r")\s*\}\s*\r?\n((?:^(?![ \t]*$).+\r?\n?)+)",
    re.MULTILINE,
)
# Остаточные kramdown-IAL ({: .class } / {: #id }) — вычищаем.
_IAL_RE = re.compile(r"^[ \t]*\{:\s*[.#][^}]*\}[ \t]*\r?\n?", re.MULTILINE)


def _bq_body(block: str) -> list:
    lines = []
    for raw in block.splitlines():
        s = raw.lstrip()
        if not s.startswith(">"):
            continue
        content = s[1:]
        if content.startswith(" "):
            content = content[1:]
        lines.append(content)
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def _title_replace(m: re.Match) -> str:
    atype = _ASIDE_TYPE[m.group(1)]
    lines = _bq_body(m.group(2))
    if not lines:
        return ""
    title = lines[0].strip()
    rest = lines[1:]
    while rest and not rest[0].strip():
        rest.pop(0)
    body = "\n".join(rest).rstrip()
    if body:
        return f"\n:::{atype}[{title}]\n{body}\n:::\n"
    return f"\n:::{atype}\n{title}\n:::\n"


def _bq_replace(m: re.Match) -> str:
    atype = _ASIDE_TYPE[m.group(1)]
    body = "\n".join(_bq_body(m.group(2))).rstrip()
    return f"\n:::{atype}\n{body}\n:::\n" if body else ""


def _p_replace(m: re.Match) -> str:
    atype = _ASIDE_TYPE[m.group(1)]
    body = m.group(2).rstrip()
    return f"\n:::{atype}\n{body}\n:::\n"


def callouts_to_asides(text: str) -> str:
    """JtD callouts ({: .note-title } / {: .note }) → Starlight asides."""
    text = _CALLOUT_TITLE_RE.sub(_title_replace, text)
    text = _CALLOUT_BQ_RE.sub(_bq_replace, text)
    text = _CALLOUT_P_RE.sub(_p_replace, text)
    return text


def strip_kramdown_ial(text: str) -> str:
    """Удаляет остаточные kramdown-IAL ({: .class }) — в Astro они не нужны."""
    return _IAL_RE.sub("", text)


# --- Изображения --------------------------------------------------------------

_A_IMG_RE = re.compile(
    r"<a\b[^>]*>\s*(<img\b[^>]*?>)\s*</a>", re.IGNORECASE | re.DOTALL
)
_IMG_RE = re.compile(r"<img\b[^>]*?>", re.IGNORECASE)
_SRC_RE = re.compile(r'src\s*=\s*"([^"]*)"', re.IGNORECASE)
_ALT_RE = re.compile(r'alt\s*=\s*"([^"]*)"', re.IGNORECASE)
_MD_IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^()\s]+)\)")
_P_CENTER_RE = re.compile(r'<p\s+align\s*=\s*"center"\s*>', re.IGNORECASE)
_P_CLOSE_RE = re.compile(r"</p>", re.IGNORECASE)
_BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)
_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://")


def _is_external(url: str) -> bool:
    return (
        bool(_SCHEME_RE.match(url))
        or url.startswith("//")
        or url.startswith("mailto:")
        or url.startswith("tel:")
    )


def new_image_path(src: str, current_file: str) -> str:
    """Относительный путь картинки из исходника → абсолютный `/img/...`."""
    if src.startswith("/img/") or _is_external(src):
        return src
    base = os.path.dirname(current_file)
    norm = os.path.normpath(os.path.join(base, src)).replace(os.sep, "/")
    if norm.startswith("img/"):
        return "/" + norm
    return "/" + norm.lstrip("/")


def rewrite_images(text: str, current_file: str) -> str:
    """HTML/markdown картинки → markdown с путём `/img/...`; снять обёртки."""
    text = _A_IMG_RE.sub(lambda m: m.group(1), text)

    def img_repl(m: re.Match) -> str:
        tag = m.group(0)
        src_m = _SRC_RE.search(tag)
        if not src_m:
            return ""
        alt_m = _ALT_RE.search(tag)
        alt = alt_m.group(1).strip() if alt_m else ""
        return f"![{alt}]({new_image_path(src_m.group(1), current_file)})"

    text = _IMG_RE.sub(img_repl, text)

    def md_repl(m: re.Match) -> str:
        return f"![{m.group(1)}]({new_image_path(m.group(2), current_file)})"

    text = _MD_IMG_RE.sub(md_repl, text)
    text = _P_CENTER_RE.sub("", text)
    text = _P_CLOSE_RE.sub("", text)
    text = _BR_RE.sub("\n", text)
    return text


# --- Внутренние ссылки --------------------------------------------------------

_INLINE_LINK_RE = re.compile(r"(?<!\!)\[([^\[\]]+)\]\(([^()\s]+)\)")
_HTML_A_RE = re.compile(
    r'<a\s+[^>]*?href\s*=\s*"([^"]+)"[^>]*>(.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)
# Абсолютные ссылки на старый сайт документации → docs-относительный путь.
_OLD_SITE_RE = re.compile(
    r"^https?://(?:printwizard\.ru|vandalsvq\.github\.io/printwizard)/docs/(.+)$",
    re.IGNORECASE,
)


def rewrite_links(text, current_file, path_map, anchor_maps, warnings):
    """`.html`-ссылки → новые slug'и + новые якоря. Висячие → plain-текст."""

    def resolve(url):
        # Абсолютная ссылка на старый сайт → внутренний docs-путь.
        old = _OLD_SITE_RE.match(url)
        if old:
            url = "/" + old.group(1)
        elif _is_external(url):
            return url
        if url.startswith("#"):
            anchor = unquote(url[1:])
            amap = anchor_maps.get(current_file, {})
            return "#" + amap.get(anchor, anchor)
        # «Голый» относительный путь (`ch_02_17.html`) в Jekyll резолвится
        # относительно каталога текущего файла — подставляем `./`.
        norm_url = url if url.startswith(("/", "./", "../")) else "./" + url
        target, anchor = _split_url(norm_url, current_file)
        new_path = path_map.get(target)
        if new_path is None:
            warnings.append(f"{current_file}: висячая ссылка → {url}")
            return None
        if anchor:
            anchor = unquote(anchor)
            amap = anchor_maps.get(target, {})
            new_anchor = amap.get(anchor)
            if new_anchor is None:
                warnings.append(f"{current_file}: висячий якорь → {url}")
                new_anchor = anchor
            return f"{new_path}#{new_anchor}"
        return new_path

    def inline_repl(m):
        link_text, url = m.group(1), m.group(2)
        href = resolve(url)
        if href is None:
            return link_text
        if href == url:
            return m.group(0)
        return f"[{link_text}]({href})"

    def html_repl(m):
        url, inner = m.group(1), m.group(2).strip()
        if _is_external(url):
            return m.group(0)
        href = resolve(url)
        if href is None:
            return inner
        return f"[{inner}]({href})"

    text = _INLINE_LINK_RE.sub(inline_repl, text)
    text = _HTML_A_RE.sub(html_repl, text)
    return text


# --- Frontmatter --------------------------------------------------------------

def _yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_frontmatter(title: str, nav_order, hidden: bool) -> str:
    """Starlight-frontmatter: title (+ sidebar.order / sidebar.hidden)."""
    lines = ["---", f"title: {_yaml_quote(title)}"]
    sidebar = []
    if nav_order is not None:
        sidebar.append(f"  order: {nav_order}")
    if hidden:
        sidebar.append("  hidden: true")
    if sidebar:
        lines.append("sidebar:")
        lines.extend(sidebar)
    lines.append("---")
    return "\n".join(lines) + "\n\n"


_BLANKS_RE = re.compile(r"\n{3,}")


def normalize_blanks(text: str) -> str:
    return _BLANKS_RE.sub("\n\n", text).strip() + "\n"
