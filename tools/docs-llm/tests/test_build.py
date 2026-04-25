"""Golden-тест на полную сборку для главы 02_08 (макрос-события).

Проверяет, что сборка из реальной /docs выдаёт ожидаемые topic-keys
с непустым body, без HTML-тегов в результате.
"""

import json
import os
import sys
import tempfile
import unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(THIS_DIR)
PUBLIC_ROOT = os.path.dirname(os.path.dirname(TOOLS_DIR))
DOCS_DIR = os.path.join(PUBLIC_ROOT, "docs")

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
        builder.resolve_links(cls.topics, cls.anchor_index)

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

    def test_render_topic_under_cap(self):
        for entry in self.topics:
            rendered = builder.render_topic(entry)
            self.assertLessEqual(
                len(rendered),
                builder.RESPONSE_CAP,
                f"Topic '{entry['key']}' превышает RESPONSE_CAP",
            )

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

    def test_write_outputs_under_size_cap(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = builder.write_outputs(self.topics, tmpdir, "test-sha")
            errors = validators.validate_bundle_size(summary["bundle_size"])
            self.assertEqual(errors, [], "\n".join(errors))
            with open(os.path.join(tmpdir, "index.json"), encoding="utf-8") as f:
                index = json.load(f)
            self.assertEqual(set(index.keys()), {t["key"] for t in self.topics})


if __name__ == "__main__":
    unittest.main()
