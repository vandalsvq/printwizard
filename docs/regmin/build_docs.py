#!/usr/bin/env python3
"""
Сборка PDF-комплекта документации PrintWizard для подачи в Минцифру.

Собирает три markdown-документа в PDF и кладёт их в корень `docs/regmin/`:

    01 install guide/printwizard_docs/printwizard_install.md
        -> docs/regmin/PrintWizard_Install_Guide.pdf
    02 user guide/user_manual.md
        -> docs/regmin/PrintWizard_User_Manual.pdf
    03 lifecycle/lifecycle_processes.md
        -> docs/regmin/PrintWizard_Lifecycle_Processes.pdf

Запуск:
    python3 docs/regmin/build_docs.py            # собрать все три
    python3 docs/regmin/build_docs.py --only user-manual
    python3 docs/regmin/build_docs.py --keep-html

Требуется:
    - Python 3.9+
    - python-markdown (ставится автоматически через pip --user, если нет)
    - Google Chrome / Chromium / Microsoft Edge для headless-рендеринга PDF.

Картинки подключаются по относительным путям из исходников — промежуточный
HTML кладётся рядом с MD, чтобы пути не ломались.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


HERE = Path(__file__).resolve().parent  # docs/regmin/


@dataclass(frozen=True)
class DocSpec:
    key: str                # короткий ключ для --only
    md_path: Path           # исходный markdown
    pdf_name: str           # имя результирующего PDF (в HERE)
    html_name: str          # имя промежуточного HTML (рядом с MD)
    title: str              # title HTML-документа

    @property
    def html_path(self) -> Path:
        return self.md_path.parent / self.html_name

    @property
    def pdf_path(self) -> Path:
        return HERE / self.pdf_name


DOCS: list[DocSpec] = [
    DocSpec(
        key="install",
        md_path=HERE / "01 install guide" / "printwizard_docs" / "printwizard_install.md",
        pdf_name="PrintWizard_Install_Guide.pdf",
        html_name="printwizard_install.html",
        title="Руководство по установке Infostart PrintWizard",
    ),
    DocSpec(
        key="user-manual",
        md_path=HERE / "02 user guide" / "user_manual.md",
        pdf_name="PrintWizard_User_Manual.pdf",
        html_name="user_manual.html",
        title="Руководство пользователя Infostart PrintWizard",
    ),
    DocSpec(
        key="lifecycle",
        md_path=HERE / "03 lifecycle" / "lifecycle_processes.md",
        pdf_name="PrintWizard_Lifecycle_Processes.pdf",
        html_name="lifecycle_processes.html",
        title="Описание процессов жизненного цикла Infostart PrintWizard",
    ),
]


CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "microsoft-edge",
]


PRINT_CSS = r"""
@page {
    size: A4;
    margin: 22mm 18mm 22mm 22mm;
    @bottom-center {
        content: counter(page) " / " counter(pages);
        font-family: "Times New Roman", serif;
        font-size: 10pt;
        color: #555;
    }
}

html, body {
    font-family: "Times New Roman", "Liberation Serif", serif;
    font-size: 11pt;
    line-height: 1.45;
    color: #111;
    background: #fff;
}

body {
    max-width: 100%;
    margin: 0;
    padding: 0;
}

h1, h2, h3, h4, h5 {
    font-family: "Arial", "Liberation Sans", sans-serif;
    color: #111;
    page-break-after: avoid;
    break-after: avoid;
}
h1 { font-size: 22pt; margin: 0 0 12pt 0; }
h2 { font-size: 16pt; margin: 18pt 0 8pt 0; border-bottom: 1px solid #999; padding-bottom: 4pt; }
h3 { font-size: 13pt; margin: 14pt 0 6pt 0; }
h4 { font-size: 11.5pt; margin: 10pt 0 4pt 0; font-style: italic; }

h2 { page-break-before: auto; }
h1 + * { page-break-before: avoid; }

p { margin: 0 0 8pt 0; text-align: justify; }

ul, ol { margin: 0 0 8pt 1.2em; padding: 0; }
li { margin: 0 0 3pt 0; }

a { color: #1a4f8a; text-decoration: none; }
a:hover { text-decoration: underline; }

img { max-width: 100%; height: auto; }

code {
    font-family: "Courier New", "Liberation Mono", monospace;
    font-size: 10pt;
    background: #f3f3f3;
    padding: 0 3px;
    border-radius: 2px;
}
pre {
    font-family: "Courier New", "Liberation Mono", monospace;
    font-size: 9.5pt;
    background: #f6f6f6;
    border: 1px solid #ddd;
    padding: 8pt 10pt;
    border-radius: 3px;
    overflow-x: auto;
    page-break-inside: avoid;
}
pre code { background: transparent; padding: 0; }

table {
    border-collapse: collapse;
    width: 100%;
    margin: 8pt 0;
    font-size: 10pt;
    page-break-inside: avoid;
}
th, td {
    border: 1px solid #888;
    padding: 4pt 6pt;
    text-align: left;
    vertical-align: top;
}
th { background: #eaeaea; font-weight: bold; }

blockquote {
    border-left: 3px solid #888;
    margin: 8pt 0 8pt 0;
    padding: 4pt 12pt;
    color: #333;
    background: #f7f7f7;
}

hr {
    border: none;
    border-top: 1px solid #bbb;
    margin: 14pt 0;
}

h1:first-of-type {
    text-align: center;
    margin-top: 30mm;
    font-size: 26pt;
}
"""


def ensure_markdown_module() -> None:
    """Импортировать python-markdown, при отсутствии — установить локально."""
    try:
        import markdown  # noqa: F401
        return
    except ImportError:
        pass

    print("[build_docs] устанавливается python-markdown через pip --user ...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--user", "--quiet", "markdown"]
    )
    import site
    user_site = site.getusersitepackages()
    if user_site not in sys.path:
        sys.path.insert(0, user_site)


def find_chrome() -> str | None:
    for cand in CHROME_CANDIDATES:
        if os.path.sep in cand:
            if Path(cand).exists():
                return cand
        else:
            path = shutil.which(cand)
            if path:
                return path
    return None


def md_to_html(md_text: str) -> str:
    import markdown
    md = markdown.Markdown(
        extensions=["extra", "toc", "sane_lists", "tables"],
        output_format="html5",
    )
    return md.convert(md_text)


def wrap_html(body: str, css: str, title: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def render_pdf(chrome: str, html_path: Path, pdf_path: Path) -> None:
    file_url = "file://" + str(html_path.resolve())
    cmd = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--no-sandbox",
        f"--print-to-pdf={pdf_path}",
        "--print-to-pdf-no-header",
        "--virtual-time-budget=5000",
        file_url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not pdf_path.exists():
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise SystemExit(
            f"[build_docs] Chrome завершился с кодом {result.returncode} "
            f"для {html_path}"
        )


def build_doc(spec: DocSpec, chrome: str, keep_html: bool) -> None:
    if not spec.md_path.exists():
        raise SystemExit(f"[build_docs] не найден исходник: {spec.md_path}")

    print(f"[build_docs] === {spec.key} ===")
    print(f"[build_docs]   читается:  {spec.md_path.relative_to(HERE)}")
    md_text = spec.md_path.read_text(encoding="utf-8")

    body = md_to_html(md_text)
    html = wrap_html(body, PRINT_CSS, spec.title)
    spec.html_path.write_text(html, encoding="utf-8")
    print(f"[build_docs]   html:      {spec.html_path.relative_to(HERE)}")

    render_pdf(chrome, spec.html_path, spec.pdf_path)
    print(f"[build_docs]   pdf:       {spec.pdf_path.relative_to(HERE)}")

    if not keep_html:
        try:
            spec.html_path.unlink()
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--only",
        choices=[d.key for d in DOCS],
        action="append",
        help="Собрать только указанный документ (можно повторять). "
             "По умолчанию — собрать все.",
    )
    parser.add_argument(
        "--keep-html",
        action="store_true",
        help="Не удалять промежуточные HTML-файлы рядом с MD-исходниками.",
    )
    args = parser.parse_args()

    targets = [d for d in DOCS if not args.only or d.key in args.only]
    if not targets:
        print("[build_docs] нечего собирать.")
        return 0

    ensure_markdown_module()

    chrome = find_chrome()
    if not chrome:
        raise SystemExit(
            "[build_docs] не найден браузер на базе Chromium. "
            "Установите Google Chrome или добавьте путь в CHROME_CANDIDATES."
        )
    print(f"[build_docs] используется браузер: {chrome}")

    for spec in targets:
        build_doc(spec, chrome, args.keep_html)

    print()
    print("[build_docs] готово. Результаты:")
    for spec in targets:
        size_kb = spec.pdf_path.stat().st_size // 1024
        print(f"  {spec.pdf_path.name:42}  {size_kb:>6} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
