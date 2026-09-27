"""Golden-тест на полную сборку для главы макрос-событий.

Проверяет, что сборка из реального источника `src/content/docs` выдаёт
ожидаемые topic-keys с непустым body, без HTML-тегов в результате.
"""

import json
import os
import sys
import tempfile
import unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(THIS_DIR)
PUBLIC_ROOT = os.path.dirname(os.path.dirname(TOOLS_DIR))
DOCS_DIR = os.path.join(PUBLIC_ROOT, "src", "content", "docs")

sys.path.insert(0, TOOLS_DIR)

import builder  # noqa: E402
import validators  # noqa: E402
from config import TopicsConfig  # noqa: E402


EXPECTED_MACROS_KEYS = {
    "макрос.ПередИнициализацией",
    "макрос.ПриПолученииДанных",
    "макрос.ПередФормированием",
    "макрос.ПередВыводомСтраницы",
    "макрос.ПередВыводомОбласти",
    "макрос.ПослеВыводаОбласти",
    "макрос.ПослеВыводаСтраницы",
    "макрос.ПослеФормирования",
    "макрос.ОбщиеПараметры",
}


class BuildIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.isdir(DOCS_DIR):
            raise unittest.SkipTest(f"docs не найдены: {DOCS_DIR}")
        cls.config = TopicsConfig.load(TOOLS_DIR)
        cls.topics, cls.anchor_index, cls.uncovered = builder.build_topics(
            DOCS_DIR, cls.config
        )
        cls.unresolved = builder.resolve_links(cls.topics, cls.anchor_index)

    def test_no_uncovered_at_stage_1(self):
        self.assertEqual(
            self.uncovered,
            [],
            f"Файлы без покрытия (нужно добавить в excluded.json или topics.json): {self.uncovered}",
        )

    def test_macros_topics_present(self):
        keys = {t["key"] for t in self.topics}
        missing = EXPECTED_MACROS_KEYS - keys
        self.assertFalse(
            missing,
            f"Отсутствуют ожидаемые topic-keys: {missing}",
        )

    def test_no_html_in_topic_bodies(self):
        errors = validators.validate_no_html_in_output(self.topics)
        self.assertEqual(errors, [], "В выводе остались HTML-теги:\n" + "\n".join(errors))

    def test_unique_topic_keys(self):
        errors = validators.validate_topic_keys_unique(self.topics)
        self.assertEqual(errors, [], "\n".join(errors))

    def test_topic_key_format(self):
        errors = validators.validate_topic_keys_format(self.topics)
        self.assertEqual(errors, [], "\n".join(errors))

    def test_see_also_refs_resolve(self):
        errors = validators.validate_see_also_refs(self.topics)
        self.assertEqual(errors, [], "\n".join(errors))

    def test_render_topic_returns_full_body(self):
        # render_topic больше не применяет cap (он применяется только в
        # BSL-runtime). Проверяем, что file-level рендер содержит
        # полное body без обрезки.
        for entry in self.topics:
            rendered = builder.render_topic(entry)
            self.assertNotIn(
                builder.TRUNCATE_MARKER.strip(),
                rendered,
                f"Topic '{entry['key']}' содержит truncate-маркер — render_topic не должен обрезать",
            )
            self.assertIn(entry["body"], rendered)

    def test_macros_pered_inicializaciei_content(self):
        entry = next(
            (t for t in self.topics if t["key"] == "макрос.ПередИнициализацией"),
            None,
        )
        self.assertIsNotNone(entry)
        self.assertIn("инициализацией макета", entry["body"].lower())
        self.assertIn("МассивОбъектов", entry["body"])

    def test_obshie_parametry_resolves_back_links(self):
        entry = next(
            (t for t in self.topics if t["key"] == "макрос.ОбщиеПараметры"),
            None,
        )
        self.assertIsNotNone(entry)
        self.assertIn("(см. topic: макрос.ПередВыводомОбласти)", entry["body"])
        self.assertIn("(см. topic: макрос.ПослеВыводаОбласти)", entry["body"])

    def test_no_unresolved_anchors(self):
        """Ссылка на несуществующий якорь молча уезжает в первую тему файла.

        Так «см. перечисление» из главы про области приводило читателя во
        вводный абзац схемы вместо таблицы значений.
        """
        errors = validators.validate_unresolved_anchors(self.unresolved)
        self.assertEqual(errors, [], "\n".join(errors))

    def test_enum_links_point_at_enum_topic(self):
        entry = next(
            (t for t in self.topics if t["key"] == "xml.AreasОбластиШаблона"),
            None,
        )
        self.assertIsNotNone(entry)
        self.assertIn(
            "Способ вывода — см. перечисление (см. topic: xml.Area.Method)",
            entry["body"],
        )

    def test_no_topic_over_cap(self):
        """Хвост темы длиннее лимита ассистент не видит (сессия f53ccd94)."""
        errors = validators.validate_topic_size(self.topics)
        self.assertEqual(errors, [], "\n".join(errors))

    def test_no_unused_split_sections(self):
        unused = builder.unused_split_sections(self.topics, self.config)
        self.assertEqual(unused, [])

    def test_output_rules_is_own_topic(self):
        entry = next(
            (t for t in self.topics if t["key"] == "макет.УсловияВыводаОбласти"),
            None,
        )
        self.assertIsNotNone(entry)
        self.assertIn("Семантика исполнения", entry["body"])
        self.assertEqual(
            self.anchor_index[("guide/ch-02-07.md", "условия-вывода-области")],
            "макет.УсловияВыводаОбласти",
        )

    def test_write_outputs_under_size_cap(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = builder.write_outputs(self.topics, tmpdir, "test-sha")
            errors = validators.validate_bundle_size(summary["bundle_size"])
            self.assertEqual(errors, [], "\n".join(errors))
            with open(os.path.join(tmpdir, "index.json"), encoding="utf-8") as f:
                index = json.load(f)
            self.assertEqual(set(index.keys()), {t["key"] for t in self.topics})


class UnresolvedAnchorTests(unittest.TestCase):
    """Откат «якорь не найден → первая тема файла» должен быть слышен."""

    @staticmethod
    def _topics():
        return [
            {
                "key": "x.Первая",
                "file": "a.md",
                "body_raw": "см. [перечисление](#нет-такого-якоря)",
                "body": "",
                "see_also": [],
            },
        ]

    def test_missing_anchor_is_reported(self):
        index = {("a.md", None): "x.Первая", ("a.md", "есть-якорь"): "x.Вторая"}
        unresolved = builder.resolve_links(self._topics(), index)
        self.assertEqual(unresolved, [("x.Первая", "a.md", "нет-такого-якоря")])
        self.assertTrue(validators.validate_unresolved_anchors(unresolved))

    def test_existing_anchor_is_silent(self):
        topics = self._topics()
        topics[0]["body_raw"] = "см. [перечисление](#есть-якорь)"
        index = {("a.md", None): "x.Первая", ("a.md", "есть-якорь"): "x.Вторая"}
        unresolved = builder.resolve_links(topics, index)
        self.assertEqual(unresolved, [])
        self.assertIn("(см. topic: x.Вторая)", topics[0]["body"])


class SplitSectionsTests(unittest.TestCase):
    """`split_sections`: подразделы крупной секции — отдельными темами."""

    DOC = (
        "---\ntitle: \"Глава\"\n---\n\n"
        "## Области\n\nВводный абзац про области.\n\n"
        "### Настройка вывода\n\nТекст настройки.\n\n"
        "#### Как работает проверка\n\nДетали проверки.\n\n"
        "### Типы полей\n\n"
        "#### Поле источника\n\nТекст поля источника.\n\n"
        "#### Поле алгоритма\n\nТекст поля алгоритма.\n\n"
        "## Другое\n\nСм. [проверку](#как-работает-проверка).\n"
    )

    def _build(self, settings):
        with tempfile.TemporaryDirectory() as docs:
            with open(os.path.join(docs, "a.md"), "w", encoding="utf-8") as f:
                f.write(self.DOC)
            config = TopicsConfig(topics={"a.md": settings}, excluded=[])
            topics, index, _ = builder.build_topics(docs, config)
        unresolved = builder.resolve_links(topics, index)
        self.assertEqual(unresolved, [])
        return {t["key"]: t for t in topics}, index, config

    def test_without_split_section_is_one_topic(self):
        topics, _, _ = self._build({"prefix": "x"})
        self.assertEqual(list(topics), ["x.Области", "x.Другое"])

    def test_split_makes_subtopics(self):
        topics, index, config = self._build({
            "prefix": "x",
            "split_sections": ["Области", "Типы полей"],
            "explicit_topics": {"Поле алгоритма": "x.АлгоритмическоеПоле"},
        })
        self.assertEqual(list(topics), [
            "x.Области", "x.НастройкаВывода", "x.ТипыПолей",
            "x.ПолеИсточника", "x.АлгоритмическоеПоле", "x.Другое",
        ])
        parent = topics["x.Области"]["body"]
        self.assertIn("Вводный абзац про области.", parent)
        self.assertIn("- Настройка вывода (см. topic: x.НастройкаВывода)", parent)
        self.assertNotIn("Текст настройки", parent)

        child = topics["x.НастройкаВывода"]["body"]
        self.assertTrue(child.startswith(
            "Подраздел темы «Области» (см. topic: x.Области)."
        ))
        self.assertIn("Детали проверки.", child)
        self.assertEqual(topics["x.НастройкаВывода"]["summary"], "Текст настройки.")

        # Якорь заголовка внутри подтемы ведёт в подтему, а не в родителя.
        self.assertEqual(index[("a.md", "как-работает-проверка")], "x.НастройкаВывода")
        self.assertIn("(см. topic: x.НастройкаВывода)", topics["x.Другое"]["body"])

        # Раздел без вводной части аннотирован перечнем подтем.
        self.assertEqual(
            topics["x.ТипыПолей"]["summary"],
            "Типы полей: Поле источника, Поле алгоритма.",
        )
        self.assertEqual(builder.unused_split_sections(list(topics.values()), config), [])

    def test_unused_split_is_reported(self):
        topics, _, config = self._build({
            "prefix": "x",
            "split_sections": ["Области", "Нет такого"],
        })
        unused = builder.unused_split_sections(list(topics.values()), config)
        self.assertEqual(unused, [("a.md", "Нет такого")])
        self.assertTrue(validators.validate_split_sections(unused))

    def test_lead_and_summary_label(self):
        topics, _, _ = self._build({
            "prefix": "x",
            "lead": "Это формат файла.",
            "summary_label": "Формат",
        })
        entry = topics["x.Области"]
        self.assertTrue(entry["body"].startswith("Это формат файла."))
        self.assertEqual(entry["summary"], "Вводный абзац про области.")
        self.assertEqual(
            builder.short_summary(entry), "Формат: Вводный абзац про области."
        )


class TopicSizeTests(unittest.TestCase):
    def test_topic_over_cap_is_reported(self):
        topics = [{
            "key": "x.Большая", "file": "a.md", "heading": "Большая",
            "body": "а" * (builder.TOPIC_CAP + 1),
        }]
        errors = validators.validate_topic_size(topics)
        self.assertEqual(len(errors), 1)
        self.assertIn("split_sections", errors[0])

    def test_topic_at_cap_is_silent(self):
        topics = [{
            "key": "x.Ровно", "file": "a.md", "heading": "Ровно",
            "body": "а" * builder.TOPIC_CAP,
        }]
        self.assertEqual(validators.validate_topic_size(topics), [])


class SummaryTests(unittest.TestCase):
    def test_illustration_and_caption_skipped(self):
        body = "[Иллюстрация]\n    \nФорматирование булево\n\nЗначения булево выводятся строкой."
        self.assertEqual(builder._extract_summary(body), "Значения булево выводятся строкой.")

    def test_sentence_after_illustration_is_not_caption(self):
        body = "[Иллюстрация]\n\nФорма открывается кнопкой на панели."
        self.assertEqual(builder._extract_summary(body), "Форма открывается кнопкой на панели.")

    def test_markdown_link_reduced_to_text(self):
        body = "[Ассистент](/guide/ch-01-08/) работает через провайдера."
        self.assertEqual(builder._extract_summary(body), "Ассистент работает через провайдера.")

    def test_code_block_with_blank_line_skipped(self):
        body = "```bsl\nА = 1;\n\nБ = 2;\n```\n\nИнициализация выполняется сама."
        self.assertEqual(builder._extract_summary(body), "Инициализация выполняется сама.")

    def test_bold_start_is_not_list(self):
        body = "* пункт списка\n\n**Модель** — идентификатор модели."
        self.assertEqual(builder._extract_summary(body), "**Модель** — идентификатор модели.")

    def test_table_only_topic_falls_back_to_heading(self):
        entry = {
            "key": "xml.Area.Settings",
            "heading": "Area.Settings — настройка вывода",
            "summary": "| Значение | Описание |\n|--|--|",
            "summary_prefix": "Объектная модель и API",
        }
        self.assertEqual(builder.short_summary(entry), "Area.Settings — настройка вывода")


if __name__ == "__main__":
    unittest.main()
