"""Юнит-тесты для transform-модулей."""

import os
import sys
import unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, TOOLS_DIR)

from transform import callouts, frontmatter, images, links, sections, toc  # noqa: E402


class FrontmatterTests(unittest.TestCase):
    def test_strip_basic(self):
        text = "---\nlayout: default\ntitle: Foo\n---\n\nbody"
        meta, body = frontmatter.strip_frontmatter(text)
        self.assertEqual(meta, {"layout": "default", "title": "Foo"})
        self.assertEqual(body.strip(), "body")

    def test_strip_quoted_value(self):
        text = '---\ntitle: "Foo Bar"\n---\nbody'
        meta, body = frontmatter.strip_frontmatter(text)
        self.assertEqual(meta["title"], "Foo Bar")

    def test_no_frontmatter(self):
        text = "# Heading\nbody"
        meta, body = frontmatter.strip_frontmatter(text)
        self.assertEqual(meta, {})
        self.assertEqual(body, text)

    def test_ensure_h1_when_missing(self):
        text = "## Subheading"
        result = frontmatter.ensure_h1(text, {"title": "Глава"})
        self.assertTrue(result.startswith("# Глава"))

    def test_ensure_h1_when_present(self):
        text = "# Already\ncontent"
        result = frontmatter.ensure_h1(text, {"title": "Other"})
        self.assertEqual(result, text)

    def test_apply_full(self):
        text = "---\ntitle: T\n---\n\nbody"
        result = frontmatter.apply(text)
        self.assertTrue(result.startswith("# T"))
        self.assertIn("body", result)


class TocTests(unittest.TestCase):
    def test_remove_details_block(self):
        text = (
            "before\n\n"
            '<details open markdown="block">\n'
            "  <summary>Содержание</summary>\n"
            "  {: .text-delta }\n"
            "1. TOC\n"
            "{:toc}\n"
            "</details>\n\n"
            "after"
        )
        result = toc.apply(text)
        self.assertNotIn("<details", result)
        self.assertNotIn("{:toc}", result)
        self.assertIn("before", result)
        self.assertIn("after", result)

    def test_remove_no_toc_marker(self):
        text = "# Heading\n{: .no_toc }\n\nbody"
        result = toc.apply(text)
        self.assertNotIn(".no_toc", result)
        self.assertIn("# Heading", result)
        self.assertIn("body", result)


class CalloutsTests(unittest.TestCase):
    def test_note_with_title_and_body(self):
        text = (
            "{: .note-title }\n"
            "> Информация\n"
            "> \n"
            "> Текст замечания.\n"
        )
        result = callouts.apply(text)
        self.assertIn("Замечание (Информация): Текст замечания.", result)
        self.assertNotIn(">", result)

    def test_important(self):
        text = "{: .important-title }\n> Важно\n> \n> Не делайте этого.\n"
        result = callouts.apply(text)
        self.assertIn("Важно (Важно): Не делайте этого.", result)

    def test_note_without_body(self):
        text = "{: .note-title }\n> Только заголовок\n"
        result = callouts.apply(text)
        self.assertIn("Замечание: Только заголовок", result)


class ImagesTests(unittest.TestCase):
    def test_html_img_with_alt(self):
        text = '<img src="./../img/foo.png" alt="Схема">'
        result = images.apply(text)
        self.assertEqual(result, "[Иллюстрация: Схема]")

    def test_html_img_without_alt(self):
        text = '<img src="./../img/foo.png">'
        result = images.apply(text)
        self.assertEqual(result, "[Иллюстрация]")

    def test_md_image(self):
        text = "![alt text](./img/foo.png)"
        result = images.apply(text)
        self.assertEqual(result, "[Иллюстрация: alt text]")

    def test_p_center_unwrap(self):
        text = '<p align="center">\n<img src="x.png">\nText\n</p>'
        result = images.apply(text)
        self.assertNotIn("<p", result)
        self.assertNotIn("</p>", result)
        self.assertIn("Text", result)


class LinksTests(unittest.TestCase):
    def test_inline_reference_expansion(self):
        text = "Look at [target][1].\n\n[1]: ./other.html#anchor\n"
        result = links.inline_references(text)
        self.assertIn("[target](./other.html#anchor)", result)
        self.assertNotIn("[1]:", result)

    def test_resolve_inline_with_resolver(self):
        def resolver(target_file, anchor):
            if target_file == "guide/other.md":
                return "topic.bar"
            return None

        text = "[ref text](./other.html#anchor)"
        result = links.apply(text, "guide/cur.md", resolver)
        self.assertEqual(result, "ref text (см. topic: topic.bar)")

    def test_unresolved_link_keeps_text(self):
        def resolver(target_file, anchor):
            return None

        text = "[ref text](./missing.html)"
        result = links.apply(text, "guide/cur.md", resolver)
        self.assertEqual(result, "ref text")


class SectionsTests(unittest.TestCase):
    def test_split_h2(self):
        text = "# H1\n\nintro\n\n## A\n\nbody-a\n\n## B\n\nbody-b\n"
        result = sections.split_h2_sections(text)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["heading"], "A")
        self.assertEqual(result[0]["body"].strip(), "body-a")
        self.assertEqual(result[1]["heading"], "B")
        self.assertEqual(result[1]["body"].strip(), "body-b")

    def test_slugify_cyrillic(self):
        self.assertEqual(sections.slugify("ПередИнициализацией"), "перединициализацией")

    def test_slugify_with_spaces(self):
        self.assertEqual(sections.slugify("Структура ДанныеМакета"), "структура-данныемакета")

    def test_h3_inside_section(self):
        text = "## Sec\n\n### Sub1\n\n### Sub2\n"
        result = sections.split_h2_sections(text)
        self.assertEqual(len(result[0]["h3"]), 2)
        self.assertEqual(result[0]["h3"][0]["heading"], "Sub1")
        self.assertEqual(result[0]["h3"][0]["anchor"], "sub1")


if __name__ == "__main__":
    unittest.main()
