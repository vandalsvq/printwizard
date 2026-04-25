"""Удаляет TOC-блоки и Jekyll-метки оформления заголовков.

TOC-блок:
    <details open markdown="block">
      <summary>...</summary>
      {: .text-delta }
    1. TOC
    {:toc}
    </details>

Метки заголовков:
    # Заголовок
    {: .no_toc }
    # Заголовок
    {: .text-delta }

После удаления маркеров, заголовок остаётся.
"""

import re


_DETAILS_BLOCK_RE = re.compile(
    r"<details\b[^>]*>.*?</details>\s*",
    re.DOTALL | re.IGNORECASE,
)
_TOC_MARKER_RE = re.compile(r"^\s*\{:toc\}\s*$", re.MULTILINE)
_NO_TOC_RE = re.compile(r"^\s*\{:\s*\.no_toc\s*\}\s*$", re.MULTILINE)
_TEXT_DELTA_RE = re.compile(r"^\s*\{:\s*\.text-delta\s*\}\s*$", re.MULTILINE)


def apply(text: str) -> str:
    """Удалить details-блоки и Jekyll-метки заголовков."""
    text = _DETAILS_BLOCK_RE.sub("", text)
    text = _TOC_MARKER_RE.sub("", text)
    text = _NO_TOC_RE.sub("", text)
    text = _TEXT_DELTA_RE.sub("", text)
    return text
