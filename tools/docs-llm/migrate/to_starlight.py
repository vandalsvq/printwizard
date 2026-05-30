#!/usr/bin/env python3
"""Миграция документации `/docs` (Jekyll + Just-the-Docs) → Astro Starlight.

Генерирует:
    src/content/docs/**          — трансформированный markdown (slug-имена)
    src/sidebar.generated.mjs    — дерево навигации из parent/grand_parent/nav_order
    src/redirects.generated.mjs  — карта старых /docs/*.html → новые slug-URL
    public/img/**                — копия docs/img (картинки документации)

Использование (из корня pw_public):
    python tools/docs-llm/migrate/to_starlight.py            # генерация
    python tools/docs-llm/migrate/to_starlight.py --check    # проверка детерминизма

`--check` собирает во временную директорию и сравнивает сгенерированный
markdown + .mjs с закоммиченными (картинки не проверяются — gitignored).
"""

import argparse
import filecmp
import json
import os
import os.path
import shutil
import sys
import tempfile
from collections import defaultdict

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, TOOLS_DIR)

from transform import frontmatter, toc, links  # type: ignore  # noqa: E402
from migrate import slugs, site_transforms as st  # type: ignore  # noqa: E402


# Каталоги /docs, которые НЕ переносятся на сайт.
EXCLUDE_DIRS = ("regmin/", "draw_io/")
# Висячие parent-узлы (нет файла с таким title) → синтетическая группа.
# Значение: (под каким title разместить, порядок среди детей).
SYNTHETIC_PARENTS = {"Сериализатор": ("Интеграция", 5)}
KEEP_IN_DOCS = {"index.mdx"}  # не трогаем при очистке src/content/docs


def _project_paths(start: str) -> dict:
    cur = os.path.abspath(start)
    while cur != os.path.dirname(cur):
        if os.path.isdir(os.path.join(cur, "docs")) and os.path.isdir(
            os.path.join(cur, "tools", "docs-llm")
        ):
            return {"root": cur, "docs": os.path.join(cur, "docs")}
        cur = os.path.dirname(cur)
    raise SystemExit("Не найден корень pw_public (ожидаются /docs и /tools/docs-llm).")


def _iter_md(docs_dir: str):
    result = []
    for root, _, files in os.walk(docs_dir):
        for name in files:
            if not name.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(root, name), docs_dir).replace(os.sep, "/")
            if any(rel.startswith(d) for d in EXCLUDE_DIRS):
                continue
            result.append(rel)
    result.sort()
    return result


def _to_int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


class Node:
    __slots__ = ("title", "slug", "order", "child_desc", "is_page", "children")

    def __init__(self, title, slug, order, child_desc, is_page):
        self.title = title
        self.slug = slug
        self.order = order
        self.child_desc = child_desc
        self.is_page = is_page
        self.children = []


def build_records(docs_dir, warnings):
    """Pass 1: прочитать и трансформировать каждый файл (без резолва ссылок)."""
    records = []
    seen_slugs = {}
    for rel in _iter_md(docs_dir):
        with open(os.path.join(docs_dir, rel), encoding="utf-8") as f:
            raw = f.read()
        raw = st.fix_fenced_frontmatter(raw)
        meta, body = frontmatter.strip_frontmatter(raw)

        slug = slugs.slug_for_relpath(rel)
        if slug in seen_slugs:
            raise SystemExit(
                f"Коллизия slug '{slug}': {rel} и {seen_slugs[slug]}"
            )
        seen_slugs[slug] = rel

        title = st.derive_title(meta, body, rel)
        has_fm_title = bool(meta.get("title"))
        nav_excluded = str(meta.get("nav_exclude", "")).strip().lower() == "true"
        # В сайдбар попадают только файлы с явным title и без nav_exclude.
        in_nav = has_fm_title and not nav_excluded
        hidden = nav_excluded or not has_fm_title

        body = toc.apply(body)
        heading_seq = st.extract_headings(body)
        anchor_map = slugs.build_anchor_map(heading_seq)

        body = st.normalize_headings(body)
        body = links.inline_references(body)
        body = st.callouts_to_asides(body)
        body = st.strip_kramdown_ial(body)
        body = st.rewrite_images(body, rel)

        records.append({
            "rel": rel,
            "slug": slug,
            "url": "/" + slug + "/",
            "title": title,
            "nav_order": _to_int(meta.get("nav_order")),
            "parent": meta.get("parent"),
            "child_desc": str(meta.get("child_nav_order", "")).strip().lower() == "desc",
            "hidden": hidden,
            "in_nav": in_nav,
            "anchor_map": anchor_map,
            "body": body,
        })
    return records


def build_sidebar(records, warnings):
    """Дерево Starlight-sidebar из parent / nav_order / child_nav_order."""
    nav = [r for r in records if r["in_nav"]]
    by_title = {}
    for r in nav:
        if r["title"] in by_title:
            warnings.append(f"дубликат title '{r['title']}' ({r['rel']})")
        by_title[r["title"]] = r

    children = defaultdict(list)
    roots = []
    for r in nav:
        if r["parent"]:
            children[r["parent"]].append(r)
        else:
            roots.append(r)

    nodes = {
        r["title"]: Node(r["title"], r["slug"], r["nav_order"], r["child_desc"], True)
        for r in nav
    }
    synth_attach = {}  # synthetic title -> under title
    for ptitle in list(children):
        if ptitle in nodes:
            continue
        under, order = SYNTHETIC_PARENTS.get(ptitle, (None, 999))
        if ptitle not in SYNTHETIC_PARENTS:
            warnings.append(f"висячий parent '{ptitle}' → размещён в корне")
        nodes[ptitle] = Node(ptitle, None, order, False, False)
        synth_attach[ptitle] = under

    for ptitle, recs in children.items():
        for r in recs:
            nodes[ptitle].children.append(nodes[r["title"]])

    root_nodes = [nodes[r["title"]] for r in roots]
    for stitle, under in synth_attach.items():
        if under and under in nodes:
            nodes[under].children.append(nodes[stitle])
        else:
            root_nodes.append(nodes[stitle])

    def sort_children(node):
        ch = node.children
        if node.child_desc:
            if any(c.order is not None for c in ch):
                return sorted(ch, key=lambda c: (-(c.order or 0), c.title))
            return sorted(ch, key=lambda c: c.title, reverse=True)
        return sorted(ch, key=lambda c: (c.order if c.order is not None else 9999, c.slug or c.title))

    def serialize(node):
        ch = sort_children(node)
        if not ch:
            return node.slug
        items = []
        if node.is_page and node.slug:
            items.append({"label": "Обзор", "slug": node.slug})
        for c in ch:
            items.append(serialize(c))
        return {"label": node.title, "items": items}

    root_nodes.sort(key=lambda n: (n.order if n.order is not None else 9999, n.title))
    return [serialize(n) for n in root_nodes]


def build_redirects(records):
    """Старые Jekyll-URL (`/docs/<rel>.html`) → новые slug-URL."""
    redirects = {}
    for r in records:
        old = "/docs/" + r["rel"][:-3] + ".html"
        redirects[old] = r["url"]
    return dict(sorted(redirects.items()))


def _redirect_stub(new_url: str) -> str:
    """meta-refresh HTML-заглушка для старого URL → новый slug."""
    return (
        "<!doctype html>\n<html lang=\"ru\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<meta http-equiv=\"refresh\" content=\"0; url={new_url}\">"
        f"<link rel=\"canonical\" href=\"{new_url}\"><meta name=\"robots\" content=\"noindex\">"
        "<title>Страница переехала — PrintWizard</title></head>"
        "<body style=\"font-family:system-ui,sans-serif;padding:2rem\">"
        f"<p>Эта страница переехала: <a href=\"{new_url}\">{new_url}</a></p>"
        "</body></html>\n"
    )


def write_outputs(records, sidebar, redirects, out_root, warnings, copy_images, docs_dir):
    docs_out = os.path.join(out_root, "src", "content", "docs")
    src_out = os.path.join(out_root, "src")
    os.makedirs(docs_out, exist_ok=True)
    os.makedirs(src_out, exist_ok=True)

    # Очистка ранее сгенерированного (кроме index.mdx).
    if os.path.isdir(docs_out):
        for root, _, files in os.walk(docs_out, topdown=False):
            for f in files:
                rel = os.path.relpath(os.path.join(root, f), docs_out).replace(os.sep, "/")
                if rel in KEEP_IN_DOCS:
                    continue
                os.remove(os.path.join(root, f))
            if root != docs_out and not os.listdir(root):
                os.rmdir(root)

    path_map = {r["rel"]: r["url"] for r in records}
    anchor_maps = {r["rel"]: r["anchor_map"] for r in records}

    for r in records:
        body = st.rewrite_links(r["body"], r["rel"], path_map, anchor_maps, warnings)
        fm = st.build_frontmatter(r["title"], r["nav_order"], r["hidden"])
        content = st.normalize_blanks(fm + body)
        dest = os.path.join(docs_out, *r["slug"].split("/")) + ".md"
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)

    sidebar_js = "// Сгенерировано tools/docs-llm/migrate/to_starlight.py — не редактировать вручную.\n"
    sidebar_js += "export default " + json.dumps(sidebar, ensure_ascii=False, indent=2) + ";\n"
    with open(os.path.join(src_out, "sidebar.generated.mjs"), "w", encoding="utf-8") as f:
        f.write(sidebar_js)

    redirects_js = "// Сгенерировано tools/docs-llm/migrate/to_starlight.py — не редактировать вручную.\n"
    redirects_js += "export default " + json.dumps(redirects, ensure_ascii=False, indent=2) + ";\n"
    with open(os.path.join(src_out, "redirects.generated.mjs"), "w", encoding="utf-8") as f:
        f.write(redirects_js)

    if copy_images:
        img_src = os.path.join(docs_dir, "img")
        img_out = os.path.join(out_root, "public", "img")
        if os.path.isdir(img_out):
            shutil.rmtree(img_out)
        if os.path.isdir(img_src):
            shutil.copytree(img_src, img_out)

        # Схемы из docs/draw_io (на них есть ссылки в доках) → public/draw_io.
        draw_src = os.path.join(docs_dir, "draw_io")
        draw_out = os.path.join(out_root, "public", "draw_io")
        if os.path.isdir(draw_out):
            shutil.rmtree(draw_out)
        if os.path.isdir(draw_src):
            os.makedirs(draw_out, exist_ok=True)
            for name in os.listdir(draw_src):
                if name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg")):
                    shutil.copy2(os.path.join(draw_src, name), os.path.join(draw_out, name))

        # Редирект-заглушки старых /docs/*.html → новые slug'и, как реальные
        # файлы в public/docs/ (Astro копирует их в dist/ с точным ключом).
        docs_redir = os.path.join(out_root, "public", "docs")
        if os.path.isdir(docs_redir):
            shutil.rmtree(docs_redir)
        for old_url, new_url in redirects.items():
            rel = old_url.lstrip("/")  # docs/guide/ch_01_01.html
            dest = os.path.join(out_root, "public", *rel.split("/"))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8") as f:
                f.write(_redirect_stub(new_url))


def run(out_root, copy_images, docs_dir):
    warnings = []
    records = build_records(docs_dir, warnings)
    sidebar = build_sidebar(records, warnings)
    redirects = build_redirects(records)
    write_outputs(records, sidebar, redirects, out_root, warnings, copy_images, docs_dir)
    return records, sidebar, redirects, warnings


def _diff_dirs(a, b, ignore):
    cmp = filecmp.dircmp(a, b, ignore=list(ignore))
    out = []
    for f in cmp.left_only:
        out.append(f"только в ожидаемом: {f}")
    for f in cmp.right_only:
        out.append(f"только в сгенерированном: {f}")
    for f in cmp.diff_files:
        out.append(f"различие: {f}")
    for sub in cmp.common_dirs:
        out.extend(f"{sub}/{d}" for d in _diff_dirs(os.path.join(a, sub), os.path.join(b, sub), ignore))
    return out


def main():
    parser = argparse.ArgumentParser(description="Миграция /docs → Astro Starlight")
    parser.add_argument("--check", action="store_true", help="Проверка детерминизма без записи в репозиторий.")
    args = parser.parse_args()

    paths = _project_paths(os.getcwd())
    root, docs_dir = paths["root"], paths["docs"]

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            records, sidebar, redirects, warnings = run(tmp, copy_images=False, docs_dir=docs_dir)
            diffs = _diff_dirs(
                os.path.join(root, "src", "content", "docs"),
                os.path.join(tmp, "src", "content", "docs"),
                ignore=KEEP_IN_DOCS,
            )
            for name in ("sidebar.generated.mjs", "redirects.generated.mjs"):
                a = os.path.join(root, "src", name)
                b = os.path.join(tmp, "src", name)
                if not os.path.isfile(a) or not filecmp.cmp(a, b, shallow=False):
                    diffs.append(f"различие: src/{name}")
            print(f"[check] файлов обработано: {len(records)}, предупреждений: {len(warnings)}")
            if diffs:
                print("[check] FAIL: сгенерированное не совпадает с закоммиченным:")
                for d in diffs:
                    print(f"  - {d}")
                print("Запустите `python tools/docs-llm/migrate/to_starlight.py` и закоммитьте.")
                return 1
            print("[check] OK")
            return 0

    records, sidebar, redirects, warnings = run(root, copy_images=True, docs_dir=docs_dir)
    print(f"Перенесено файлов: {len(records)}")
    print(f"Редиректов: {len(redirects)}")
    print(f"Топ-уровень сайдбара: {len(sidebar)}")
    if warnings:
        print(f"\nПРЕДУПРЕЖДЕНИЯ ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
