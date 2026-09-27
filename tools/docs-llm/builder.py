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
# Однострочная аннотация темы. Пишется сразу после маркера темы и
# используется рантаймом (`pw_АссистентСервер`) для индекса разделов и
# выдачи поиска: по одному имени ключа модель не понимает, что внутри.
TOPIC_SUMMARY_TEMPLATE = "### SUMMARY: {summary} ###"
SUMMARY_MAX_CHARS = 160
TOPIC_KEY_RE = re.compile(r"^[а-яёa-z]+(?:\.[а-яёА-ЯЁA-Za-z0-9_\*]+)*$")
RESPONSE_CAP = 3000  # информационный — лимит перечня (список тем, выдача поиска) в BSL-рантайме
# Лимит одиночной выдачи темы в панели ассистента
# (`pw_АссистентМодельКлиентСервер.ЛимитыОтветаПанели`). Всё, что дальше,
# модель не видит: подраздел «Условия вывода области» начинался на 6145-м
# символе своей темы, и ассистент, прочитав верную тему, ответа в ней не
# нашёл. Тема длиннее лимита валит сборку — её делят `split_sections`.
TOPIC_CAP = 6000
TRUNCATE_MARKER = "\n\n... [truncated, используйте более узкий topic]"  # для BSL-runtime


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


_CALLOUT_PREFIX_RE = re.compile(r"^(?:Замечание|Совет|Важно|Внимание)\b\s*[(:]")
_NUMBERED_ITEM_RE = re.compile(r"^\d+\.\s")
_ILLUSTRATION_PREFIX = "[Иллюстрация"
# Абзацы разделяет пустая строка или строка из одних пробелов: под картинкой
# в главах стоит строка с отступом, и без этого картинка склеивалась с
# подписью в один абзац — аннотацией становилось «[Иллюстрация] Формат булево».
_PARAGRAPH_SPLIT_RE = re.compile(r"\n[ \t]*\n")
_MD_LINK_RE = re.compile(r"\[([^\[\]]+)\]\([^()\s]+\)")
# Абзац из одного жирного ярлыка («**Debian / Ubuntu:**») — подпись к блоку
# ниже, а не описание темы.
_BOLD_LABEL_RE = re.compile(r"^\*\*[^*\n]+\*\*:?$")
# Блок кода вырезается до деления на абзацы: пустая строка внутри блока
# рвала его на куски, и кусок без ``` становился аннотацией.
_CODE_FENCE_RE = re.compile(r"^```.*?^```[^\n]*$", re.MULTILINE | re.DOTALL)


def _is_wrapper_paragraph(paragraph: str) -> bool:
    """Абзац-обёртка: callout, цитата, заголовок, таблица, список, картинка."""
    head = paragraph.lstrip()
    if not head:
        return True
    if head[0] in ">#|" or head.startswith(_ILLUSTRATION_PREFIX):
        return True
    # Список и разделитель — да, а жирное начало абзаца («**Модель** — …») нет:
    # иначе тема, где каждый абзац открывается термином, аннотировалась
    # первым попавшимся абзацем без термина.
    if head.startswith(("* ", "- ", "+ ", "---", "***")):
        return True
    if _BOLD_LABEL_RE.match(head):
        return True
    return bool(_CALLOUT_PREFIX_RE.match(head) or _NUMBERED_ITEM_RE.match(head))


def _extract_summary(body: str) -> str:
    """Первый содержательный абзац темы — он идёт в маркер SUMMARY.

    Абзацы-обёртки (callout из aside, цитата, таблица, список, заголовок,
    картинка) пропускаются: аннотация «Важно (ВАЖНО): с версии 2025.2.5…»
    не объясняет модели, о чём тема, а по аннотации она выбирает, какую
    секцию читать. Однострочный абзац без точки в конце сразу за картинкой —
    её подпись, он пропускается вместе с ней. Markdown-ссылки сводятся к
    тексту: адрес страницы сайта в аннотации модели ничего не говорит.
    """
    body = _CODE_FENCE_RE.sub("", body).strip()
    if not body:
        return ""
    paragraphs = [p.strip() for p in _PARAGRAPH_SPLIT_RE.split(body) if p.strip()]
    if not paragraphs:
        return ""

    meaningful = None
    after_illustration = False
    for paragraph in paragraphs:
        is_caption = (
            after_illustration
            and "\n" not in paragraph
            and not paragraph.endswith((".", ":", "!", "?"))
        )
        after_illustration = paragraph.startswith(_ILLUSTRATION_PREFIX)
        if is_caption or _is_wrapper_paragraph(paragraph):
            continue
        meaningful = paragraph
        break
    if meaningful is None:
        meaningful = paragraphs[0]

    first = _MD_LINK_RE.sub(r"\1", meaningful).replace("\n", " ")
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

    `anchor_index` маппит (file_rel, anchor) → topic_key. В индекс попадают
    якорь самой H2-секции, якоря всех её подзаголовков (H3–H6) и None —
    последний указывает на первый topic файла.

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

        exclude_h2 = set(settings.get("exclude_h2", []))
        lead = settings.get("lead", "").strip()

        h2_sections = sections.split_h2_sections(text)
        first_topic_key: Optional[str] = None

        for sec in h2_sections:
            if sec["heading"] in exclude_h2:
                continue

            for part in _section_parts(sec, 3, settings, None):
                key = part["key"]
                body_parts = [lead] if lead else []
                if part["parent"]:
                    parent_key, parent_heading = part["parent"]
                    body_parts.append(
                        f"Подраздел темы «{parent_heading}» (см. topic: {parent_key})."
                    )
                body_parts.append(part["body"])

                entry = {
                    "key": key,
                    "file": file_rel,
                    "anchor": part["anchor"],
                    "heading": part["heading"],
                    "body_raw": _normalize_blank_lines("\n\n".join(body_parts)),
                    "body": "",
                    "summary": _extract_summary(part["summary_source"]),
                    "summary_prefix": settings.get("summary_prefix", ""),
                    "summary_label": settings.get("summary_label", ""),
                    "split": part["split"],
                    "see_also": [],
                }
                topics.append(entry)
                anchor_index[(file_rel, part["anchor"])] = key
                for sub in part["subheadings"]:
                    anchor_index[(file_rel, sub["anchor"])] = key

                if first_topic_key is None:
                    first_topic_key = key
                    anchor_index[(file_rel, None)] = key

    return topics, anchor_index, uncovered


def _topic_key(heading: str, settings: dict) -> str:
    explicit_map = settings.get("explicit_topics", {})
    if heading in explicit_map:
        return explicit_map[heading]
    return f"{settings['prefix']}.{heading_to_topic_name(heading)}"


def _section_parts(
    sec: dict,
    child_level: int,
    settings: dict,
    parent: Optional[Tuple[str, str]],
) -> List[dict]:
    """Раскладывает секцию на темы.

    Обычная секция — одна тема. Секция, заголовок которой перечислен в
    `split_sections`, делится: каждый её подраздел уровня `child_level`
    становится отдельной темой (и сам может быть поделен дальше), а у
    секции остаются вводная часть и перечень подтем со ссылками. Подтема
    начинается строкой со ссылкой на родительскую тему — без неё модель,
    прочитав «Пример» или «Страницу "Журнал"», не знает, к чему они.

    Ключ подтемы строится из её собственного заголовка (`<префикс>.<Хвост>`),
    без родительского: поиск ассистента сильно взвешивает слова ключа и
    долю слов запроса в нём, и длинный составной ключ размывал бы попадание.
    """
    key = _topic_key(sec["heading"], settings)
    part = {
        "key": key,
        "heading": sec["heading"],
        "anchor": sec["anchor"],
        "body": sec["body"],
        "summary_source": sec["body"],
        "subheadings": sec["subheadings"],
        "parent": parent,
        "split": False,
    }
    if sec["heading"] not in settings.get("split_sections", []):
        return [part]

    intro, children = sections.split_subsections(sec["body"], child_level)
    if not children:
        return [part]

    child_parts: List[dict] = []
    listing = []
    for child in children:
        nested = _section_parts(child, child_level + 1, settings, (key, sec["heading"]))
        child_parts.extend(nested)
        listing.append(f"- {child['heading']} (см. topic: {nested[0]['key']})")

    part["body"] = "\n\n".join(
        [p for p in (intro, "Подробности — в отдельных темах:\n" + "\n".join(listing)) if p]
    )
    # Без вводной части аннотацией служит перечень подтем: «Типы полей
    # набора» иначе аннотировались бы подписью раздела «Наборы данных».
    part["summary_source"] = intro or "{}: {}.".format(
        sec["heading"], ", ".join(child["heading"] for child in children)
    )
    part["subheadings"] = sections.extract_subheadings(intro)
    part["split"] = True
    return [part] + child_parts


def unused_split_sections(topics: List[dict], config: TopicsConfig) -> List[Tuple[str, str]]:
    """Заголовки из `split_sections`, которые ничего не поделили.

    Заголовок переименовали или убрали подразделы — и тема молча вернулась
    к прежнему размеру. Возвращает (файл, заголовок) для каждого такого.
    """
    done = {(t["file"], t["heading"]) for t in topics if t.get("split")}
    unused = []
    for file_rel, settings in sorted(config.topics.items()):
        for heading in settings.get("split_sections", []):
            if (file_rel, heading) not in done:
                unused.append((file_rel, heading))
    return unused


def resolve_links(
    topics: List[dict],
    anchor_index: Dict[Tuple[str, Optional[str]], str],
) -> List[Tuple[str, str, str]]:
    """Pass 2. Резолвит ссылки в body каждого topic, заполняет see_also.

    Возвращает список нерезолвнутых якорей — (topic_key, target_file, anchor)
    для ссылок, у которых файл в корпусе есть, а такого якоря в нём нет.
    Такая ссылка откатывается на первую тему файла, и это молчаливое
    враньё: ссылка «см. перечисление» приводила читателя во вводный абзац
    главы. Валидатор `unresolved_anchors` валит на этом сборку.
    """
    see_also_re = re.compile(r"\(см\.\s*topic:\s*([^)]+?)\)")
    unresolved: List[Tuple[str, str, str]] = []

    for entry in topics:
        def make_resolver(self_key: str, self_file: str):
            def resolver(target_file: Optional[str], anchor: Optional[str]) -> Optional[str]:
                if target_file is None:
                    return None
                key = anchor_index.get((target_file, anchor))
                if key is None and anchor is not None:
                    key = anchor_index.get((target_file, None))
                    if key is not None:
                        unresolved.append((self_key, target_file, anchor))
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

    return unresolved


def render_topic(entry: dict) -> str:
    """Полный текст topic'а для review-файла `topics/{key}.md`.

    Cap (`RESPONSE_CAP`) здесь намеренно НЕ применяется: review-файлы
    должны быть синхронны с bundle.txt, чтобы diff в PR показывал
    реальные правки в полном объёме. Cap — это runtime-поведение
    `PW_GetDocs` в BSL (`pw_АссистентСервер` при чтении секции из
    bundle обрезает ответ до `RESPONSE_CAP` символов).
    """
    parts = [f"# {entry['heading']}", "", entry["body"]]
    if entry["see_also"]:
        parts.append("")
        parts.append("См. также: " + ", ".join(entry["see_also"]))
    return "\n".join(parts).strip() + "\n"


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


def section_titles(topics: List[dict]) -> Dict[str, str]:
    """Раздел (первый сегмент ключа) → человекочитаемое название.

    Берётся `summary_prefix` первой темы раздела: файлы одного раздела
    задают его одинаковым (см. topics.json).
    """
    titles: Dict[str, str] = {}
    for entry in topics:
        prefix = entry["key"].split(".", 1)[0]
        if prefix in titles:
            continue
        title = (entry.get("summary_prefix") or "").strip()
        if title:
            titles[prefix] = title
    return titles


def render_bundle(topics: List[dict], commit_sha: str, build_timestamp: str) -> str:
    """Bundle рантайма — header + concat(маркеры + bodies)."""
    header_lines = [
        f"# pw-llm-bundle {BUNDLE_VERSION}",
        f"# pw_public_commit_sha: {commit_sha}",
        f"# build_timestamp: {build_timestamp}",
        f"# topics_count: {len(topics)}",
    ]
    # Названия разделов: рантайм показывает их в индексе `PW_GetDocs("список")`.
    # Иначе раздел пришлось бы подписывать аннотацией случайной первой темы.
    for prefix, title in sorted(section_titles(topics).items()):
        header_lines.append(f"# section: {prefix} = {title}")
    header_lines.append("")
    parts = ["\n".join(header_lines), ""]
    for entry in topics:
        marker = TOPIC_MARKER_TEMPLATE.format(key=entry["key"])
        parts.append(marker)
        parts.append(TOPIC_SUMMARY_TEMPLATE.format(summary=short_summary(entry)))
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


def short_summary(entry: dict, limit: int = SUMMARY_MAX_CHARS) -> str:
    """Однострочная аннотация темы для bundle, индекса и выдачи поиска.

    Берётся первая непустая строка summary; markdown-заголовки и таблицы
    схлопываются, длина ограничивается `limit`. Метка файла (`summary_label`)
    ставится впереди: по одной аннотации «Область соответствует диапазону
    строк…» модель принимала тему XML-схемы за описание интерфейса.
    """
    raw = (entry.get("summary") or "").strip()
    line = ""
    for candidate in raw.split("\n"):
        candidate = candidate.strip().lstrip("#").strip()
        if candidate and not candidate.startswith("|"):
            line = candidate
            break
    if not line:
        # Тема из одной таблицы: заголовок («Area.Settings — настройка
        # вывода») говорит о ней больше, чем общая подпись раздела.
        line = entry.get("heading") or entry.get("summary_prefix") or entry["key"]
    label = (entry.get("summary_label") or "").strip()
    if label:
        line = f"{label}: {line}"
    line = " ".join(line.split())
    if len(line) > limit:
        line = line[: limit - 3].rstrip() + "..."
    return line


def render_listing(topics: List[dict]) -> str:
    """Текст для PW_GetDocs("список") — индекс разделов, не плоский список тем.

    Плоский список из ~200 тем с аннотациями не влезает в лимит ответа
    (`RESPONSE_CAP`), а без аннотаций бесполезен: по одному ключу модель не
    понимает, что внутри. Поэтому индекс двухуровневый — здесь разделы
    (`<префикс>.* (N тем) — <о чём раздел>`), а темы раздела с аннотациями
    рантайм отдаёт по запросу `PW_GetDocs("<префикс>.*")`.
    """
    sections: Dict[str, Dict[str, object]] = {}
    for entry in topics:
        prefix = entry["key"].split(".", 1)[0]
        section = sections.setdefault(prefix, {"count": 0, "title": ""})
        section["count"] = int(section["count"]) + 1
        if not section["title"]:
            section["title"] = entry.get("summary_prefix") or ""

    lines = []
    for prefix in sorted(sections):
        section = sections[prefix]
        title = str(section["title"]).strip()
        head = f"{prefix}.* ({section['count']} тем)"
        lines.append(f"{head} — {title}" if title else head)
    return "\n".join(lines)


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
