"""Юнит-тесты миграции Jekyll → Astro Starlight (tools/docs-llm/migrate)."""

import os
import sys
import unittest

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(THIS_DIR)
sys.path.insert(0, TOOLS_DIR)

from migrate import slugs  # noqa: E402
from migrate import site_transforms as st  # noqa: E402


class SlugTests(unittest.TestCase):
    def test_guide_file(self):
        self.assertEqual(slugs.slug_for_relpath("guide/ch_01_01.md"), "guide/ch-01-01")

    def test_top_level_strips_order_prefix(self):
        self.assertEqual(slugs.slug_for_relpath("01_guide.md"), "guide")
        self.assertEqual(slugs.slug_for_relpath("19_licensing_faq.md"), "licensing-faq")

    def test_cyrillic_and_spaces(self):
        self.assertEqual(slugs.slug_for_relpath("query/Работа-с-запросами.md"), "query/rabota-s-zaprosami")
        self.assertEqual(slugs.slug_for_relpath("history/2023 - 1.1.2.х .md"), "history/2023-1-1-2-h")

    def test_hash_in_stem(self):
        self.assertEqual(slugs.slug_for_relpath("convert/pw_template.md"), "convert/pw-template")


class AnchorTests(unittest.TestCase):
    def test_simple_match(self):
        amap = slugs.build_anchor_map(["Очередность подготовки полей"])
        self.assertEqual(amap["очередность-подготовки-полей"], "очередность-подготовки-полей")

    def test_em_dash_divergence(self):
        # jekyll схлопывает дефисы, github — нет.
        amap = slugs.build_anchor_map(["A — B"])
        self.assertEqual(amap["a-b"], "a--b")

    def test_duplicate_headings_dedup(self):
        amap = slugs.build_anchor_map(["Заголовок", "Заголовок"])
        self.assertEqual(amap["заголовок"], "заголовок")
        self.assertEqual(amap["заголовок-1"], "заголовок-1")

    def test_hash_heading(self):
        amap = slugs.build_anchor_map(["pw#template#about"])
        self.assertEqual(amap["pwtemplateabout"], "pwtemplateabout")


class FencedFrontmatterTests(unittest.TestCase):
    def test_unwrap(self):
        text = "```\n---\ntitle: Foo\n---\n```\n\nbody"
        fixed = st.fix_fenced_frontmatter(text)
        self.assertTrue(fixed.startswith("---\ntitle: Foo"))
        self.assertNotIn("```", fixed)

    def test_plain_untouched(self):
        text = "---\ntitle: Foo\n---\n\nbody"
        self.assertEqual(st.fix_fenced_frontmatter(text), text)


class CalloutAsideTests(unittest.TestCase):
    def test_note_with_body(self):
        text = "{: .note-title }\n> Информация\n>\n> Текст замечания.\n"
        result = st.callouts_to_asides(text)
        self.assertIn(":::note[Информация]", result)
        self.assertIn("Текст замечания.", result)
        self.assertTrue(result.strip().endswith(":::"))

    def test_important_becomes_caution(self):
        text = "{: .important-title }\n> Важно\n>\n> Не делайте этого.\n"
        result = st.callouts_to_asides(text)
        self.assertIn(":::caution[Важно]", result)

    def test_multiline_list_preserved(self):
        text = "{: .note-title }\n> Заголовок\n>\n> * пункт 1\n> * пункт 2\n"
        result = st.callouts_to_asides(text)
        self.assertIn("* пункт 1", result)
        self.assertIn("* пункт 2", result)

    def test_title_only(self):
        text = "{: .note-title }\n> Только заголовок\n"
        result = st.callouts_to_asides(text)
        self.assertIn(":::note\nТолько заголовок\n:::", result)


class ImageTests(unittest.TestCase):
    def test_html_img_relative_path(self):
        text = '<img src="./../img/ch_02/12.png">'
        result = st.rewrite_images(text, "guide/ch_02_07.md")
        self.assertEqual(result.strip(), "![](/img/ch_02/12.png)")

    def test_anchor_wrapped_img(self):
        text = '<a href="./../img/x.png"><img src="./../img/x.png" alt="Схема"></a>'
        result = st.rewrite_images(text, "guide/ch_01_02.md")
        self.assertEqual(result.strip(), "![Схема](/img/x.png)")

    def test_markdown_image_path(self):
        text = "![подпись](./../img/foo.png)"
        result = st.rewrite_images(text, "guide/ch_01_02.md")
        self.assertEqual(result.strip(), "![подпись](/img/foo.png)")

    def test_p_center_unwrapped(self):
        text = '<p align="center"><img src="./../img/x.png"></p>'
        result = st.rewrite_images(text, "guide/ch_01_02.md")
        self.assertNotIn("<p", result)
        self.assertIn("![](/img/x.png)", result)


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.path_map = {
            "guide/ch_02_05.md": "/guide/ch-02-05/",
            "guide/ch_02_07.md": "/guide/ch-02-07/",
        }
        self.anchor_maps = {
            "guide/ch_02_05.md": {"наборы": "наборы"},
        }
        self.warnings = []

    def _rewrite(self, text, current="guide/ch_01_02.md"):
        return st.rewrite_links(text, current, self.path_map, self.anchor_maps, self.warnings)

    def test_internal_with_anchor(self):
        out = self._rewrite("см. [тут](ch_02_05.html#наборы)")
        self.assertIn("[тут](/guide/ch-02-05/#наборы)", out)

    def test_bare_relative_resolves_to_current_dir(self):
        out = self._rewrite("[ссылка](ch_02_07.html)")
        self.assertIn("[ссылка](/guide/ch-02-07/)", out)

    def test_dangling_drops_to_text(self):
        out = self._rewrite("[битая](no_such.html)")
        self.assertEqual(out.strip(), "битая")
        self.assertTrue(self.warnings)

    def test_external_untouched(self):
        out = self._rewrite("[infostart](https://infostart.ru/x/)")
        self.assertIn("[infostart](https://infostart.ru/x/)", out)

    def test_same_page_anchor(self):
        out = st.rewrite_links("[туда](#наборы)", "guide/ch_02_05.md", self.path_map, self.anchor_maps, self.warnings)
        self.assertIn("[туда](#наборы)", out)

    def test_image_markdown_not_treated_as_link(self):
        out = self._rewrite("![alt](/img/x.png)")
        self.assertEqual(out.strip(), "![alt](/img/x.png)")


class FrontmatterTests(unittest.TestCase):
    def test_quotes_special_title(self):
        fm = st.build_frontmatter('pw#template', 1, False)
        self.assertIn('title: "pw#template"', fm)
        self.assertIn("order: 1", fm)
        self.assertNotIn("hidden", fm)

    def test_hidden_without_order(self):
        fm = st.build_frontmatter("Политика", None, True)
        self.assertIn("hidden: true", fm)
        self.assertNotIn("order:", fm)

    def test_derive_title_from_h1(self):
        self.assertEqual(st.derive_title({}, "# Работа с запросами\n\ntext", "query/x.md"), "Работа с запросами")


class StripH1Tests(unittest.TestCase):
    def test_removes_leading_h1(self):
        body = "# Заголовок\n\n## Подраздел\n\ntext"
        out = st.strip_leading_h1(body)
        self.assertFalse(out.startswith("# Заголовок"))
        self.assertIn("## Подраздел", out)


if __name__ == "__main__":
    unittest.main()
