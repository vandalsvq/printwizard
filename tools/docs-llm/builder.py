"""Двухпроходная сборка `/docs-llm` из `/docs`.

Pass 1 (build_topics):
    Прочитать .md → frontmatter/toc/callouts/images → разбить на H2 →
    создать topic-entry для каждой H2-секции. Построить anchor-индекс
    (file, anchor) → topic_key — нужен для резолва ссылок.

Pass 2 (resolve_links):
    Для каждого topic — резолвить ссылки через anchor-индекс. Извлечь
    see_also.

Pass 3 (write_outputs):
    Записать topics/{key}.md, index.json, bundle.txt.
"""

import datetime
import json
import os
import os.path
import re
import subprocess
from typing import Dict, List, Optional, Tuple

from config import TopicsConfig  # type: ignore
from transform import callouts, frontmatter, images, links, sections, toc  # type: ignore


BUNDLE_VERSION = "v1"
TOPIC_MARKER_TEMPLATE = "### TOPIC: {key} ###"
TOPIC_KEY_RE = re.compile(r"^[а-яёa-z]+(?:\.[а-яёА-ЯЁA-Za-z0-9_\*]+)*$")
RESPONSE_CAP = 3000
TRUNCATE_MARKER = "\n\n... [truncated, используйте более узкий topic]"


def heading_to_topic_name(heading: str) -> str:
    """Преобразует H2-заголовок в хвост topic-key.

    Разделяет по пробелам и не-словесным символам, капитализирует первую
    букву каждого фрагмента, склеивает. `Список наборов` → `СписокНаборов`,
    `ПередИнициализацией` → `ПередИнициализацией`, `Сборка/Обработки` →
    `СборкаОбработки`.
    """
    parts = re.split(r"[^\w]+", heading.strip(), flags=re.UNICODE)
    return "".join(
        (p[0].upper() + p[1:]) if p else "" for p in parts if p
    )


def iterate_md_files(docs_dir: str) -> List[str]:
    """Список .md-файлов внутри docs_dir, отсортированный, относительные пути."""
    result = []
    for root, _, files in os.walk(docs_dir):
        for name in files:
            if name.endswith(".md"):
                full = os.path.join(root, name)
                rel = os.path.relpath(full, docs_dir).replace(os.sep, "/")
                result.append(rel)
    result.sort()
    return result


def _extract_summary(body: str) -> str:
    body = body.strip()
    if not body:
        return ""
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    if not paragraphs:
        return ""
    first = paragraphs[0].replace("\n", " ")
    if len(first) > 200:
        first = first[:197] + "..."
    return first


def _normalize_blank_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def build_topics(
    docs_dir: str,
    config: TopicsConfig,
) -> Tuple[List[dict], Dict[Tuple[str, Optional[str]], str], List[str]]:
    """Pass 1. Возвращает (topics, anchor_index, uncovered_files).

    `anchor_index` маппит (file_rel, anchor) → topic_key. Anchor может быть
    None — тогда указывает на первый topic файла.

    `uncovered_files` — файлы, которые не покрыты ни topics, ни excluded.
    Сборка должна упасть на этом этапе (валидатор), но мы возвращаем
    список целиком, чтобы видеть всё что не покрыто.
    """
    topics: List[dict] = []
    anchor_index: Dict[Tuple[str, Optional[str]], str] = {}
    uncovered: List[str] = []

    for file_rel in iterate_md_files(docs_dir):
        settings = config.file_settings(file_rel)
        if settings is None:
            if config.is_excluded(file_rel):
                continue
            uncovered.append(file_rel)
            continue

        full_path = os.path.join(docs_dir, file_rel)
        with open(full_path, "r", encoding="utf-8") as f:
            text = f.read()

        text = frontmatter.apply(text)
        text = toc.apply(text)
        text = callouts.apply(text)
        text = images.apply(text)
        text = links.inline_references(text)

        prefix = settings["prefix"]
        explicit_map = settings.get("explicit_topics", {})
        exclude_h2 = set(settings.get("exclude_h2", []))

        h2_sections = sections.split_h2_sections(text)
        first_topic_key: Optional[str] = None

        for sec in h2_sections:
            heading = sec["heading"]
            if heading in exclude_h2:
                continue
            if heading in explicit_map:
                key = explicit_map[heading]
            else:
                key = f"{prefix}.{heading_to_topic_name(heading)}"

            entry = {
                "key": key,
                "file": file_rel,
                "anchor": sec["anchor"],
                "heading": heading,
                "body_raw": _normalize_blank_lines(sec["body"]),
                "body": "",
                "summary": _extract_summary(sec["body"]),
                "see_also": [],
            }
            topics.append(entry)
            anchor_index[(file_rel, sec["anchor"])] = key
            for h3 in sec["h3"]:
                anchor_index[(file_rel, h3["anchor"])] = key

            if first_topic_key is None:
                first_topic_key = key
                anchor_index[(file_rel, None)] = key

    return topics, anchor_index, uncovered


def resolve_links(
    topics: List[dict],
    anchor_index: Dict[Tuple[str, Optional[str]], str],
) -> None:
    """Pass 2. Резолвит ссылки в body каждого topic, заполняет see_also."""
    see_also_re = re.compile(r"\(см\.\s*topic:\s*([^)]+?)\)")

    for entry in topics:
        def make_resolver(self_key: str, self_file: str):
            def resolver(target_file: Optional[str], anchor: Optional[str]) -> Optional[str]:
                if target_file is None:
                    return None
                key = anchor_index.get((target_file, anchor))
                if key is None and anchor is not None:
                    key = anchor_index.get((target_file, None))
                if key == self_key:
                    return None
                return key
            return resolver

        resolved = links.apply(
            entry["body_raw"],
            entry["file"],
            make_resolver(entry["key"], entry["file"]),
        )
        entry["body"] = _normalize_blank_lines(resolved)

        seen = []
        for match in see_also_re.finditer(entry["body"]):
            ref = match.group(1).strip()
            if ref and ref not in seen and ref != entry["key"]:
                seen.append(ref)
        entry["see_also"] = seen


def render_topic(entry: dict) -> str:
    """Финальный текст для PW_GetDocs(topic) — заголовок + body + see_also."""
    parts = [f"# {entry['heading']}", "", entry["body"]]
    if entry["see_also"]:
        parts.append("")
        parts.append("См. также: " + ", ".join(entry["see_also"]))
    text = "\n".join(parts).strip() + "\n"
    if len(text) > RESPONSE_CAP:
        text = text[: RESPONSE_CAP - len(TRUNCATE_MARKER)] + TRUNCATE_MARKER
    return text


def get_pw_public_sha(repo_dir: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", repo_dir, "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def render_bundle(topics: List[dict], commit_sha: str, build_timestamp: str) -> str:
    """Bundle для CommonTemplate — header + concat(маркеры + bodies)."""
    header_lines = [
        f"# pw-llm-bundle {BUNDLE_VERSION}",
        f"# pw_public_commit_sha: {commit_sha}",
        f"# build_timestamp: {build_timestamp}",
        f"# topics_count: {len(topics)}",
        "",
    ]
    parts = ["\n".join(header_lines), ""]
    for entry in topics:
        marker = TOPIC_MARKER_TEMPLATE.format(key=entry["key"])
        parts.append(marker)
        parts.append("")
        parts.append(entry["body"])
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def render_index(topics: List[dict]) -> dict:
    """index.json — для review и тестов; runtime его не читает."""
    return {
        entry["key"]: {
            "file": entry["file"],
            "anchor": entry["anchor"],
            "summary": entry["summary"],
            "see_also": entry["see_also"],
        }
        for entry in topics
    }


def render_listing(topics: List[dict]) -> str:
    """Возвращает текст для PW_GetDocs("список") — плоский индекс ≤ 2000 chars.

    Каждая строка: `<topic-key> — <summary, обрезано>`.
    При превышении лимита агрегируется до префиксов.
    """
    lines = []
    for entry in topics:
        summary = entry["summary"].split("\n")[0]
        if len(summary) > 80:
            summary = summary[:77] + "..."
        lines.append(f"{entry['key']} — {summary}" if summary else entry["key"])
    listing = "\n".join(lines)
    if len(listing) <= RESPONSE_CAP:
        return listing
    prefixes: Dict[str, int] = {}
    for entry in topics:
        prefix = entry["key"].split(".", 1)[0]
        prefixes[prefix] = prefixes.get(prefix, 0) + 1
    return "\n".join(f"{p}.* ({n} тем)" for p, n in sorted(prefixes.items()))


def write_outputs(
    topics: List[dict],
    output_dir: str,
    commit_sha: str,
) -> dict:
    """Pass 3. Возвращает summary { bundle_size, topics_count, ... }."""
    os.makedirs(output_dir, exist_ok=True)
    topics_subdir = os.path.join(output_dir, "topics")
    os.makedirs(topics_subdir, exist_ok=True)

    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    for entry in topics:
        rendered = render_topic(entry)
        path = os.path.join(topics_subdir, f"{entry['key']}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(rendered)

    bundle_text = render_bundle(topics, commit_sha, timestamp)
    bundle_path = os.path.join(output_dir, "bundle.txt")
    with open(bundle_path, "w", encoding="utf-8") as f:
        f.write(bundle_text)

    index = render_index(topics)
    index_path = os.path.join(output_dir, "index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2, sort_keys=True)

    listing = render_listing(topics)
    listing_path = os.path.join(output_dir, "listing.txt")
    with open(listing_path, "w", encoding="utf-8") as f:
        f.write(listing + "\n")

    return {
        "bundle_size": len(bundle_text.encode("utf-8")),
        "topics_count": len(topics),
        "listing_size": len(listing),
        "timestamp": timestamp,
    }


def remove_orphan_topics(output_dir: str, current_keys: List[str]) -> List[str]:
    """Удаляет файлы topics/*.md, которые больше не соответствуют ни одному topic."""
    topics_dir = os.path.join(output_dir, "topics")
    if not os.path.isdir(topics_dir):
        return []
    expected = {f"{k}.md" for k in current_keys}
    removed = []
    for name in os.listdir(topics_dir):
        if name not in expected and name.endswith(".md"):
            os.remove(os.path.join(topics_dir, name))
            removed.append(name)
    return removed
