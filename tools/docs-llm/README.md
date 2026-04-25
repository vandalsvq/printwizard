# tools/docs-llm — генератор машиночитаемой документации для AI-агента

Скрипт сборки `/docs-llm` из `/docs`. В норме запускается **только в
CI** (`.github/workflows/docs-llm-build.yml`) на push в `master`.
Контрибьюторы локально его не запускают.

## Использование

```bash
# Полная пересборка /docs-llm (используется CI)
python3 tools/docs-llm/build.py

# Проверка без записи (используется при отладке локально)
python3 tools/docs-llm/build.py --check

# Запись в произвольную директорию
python3 tools/docs-llm/build.py --output /tmp/docs-llm
```

Запускается из корня pw_public. Поиск корня — по наличию `/docs` и
`/tools/docs-llm` в текущей или родительских директориях.

## Зависимости

Только stdlib Python 3.9+. Никаких `pip install` не требуется.

## Тесты

```bash
cd tools/docs-llm
python3 -m unittest discover tests
```

32 теста: юниты для transform-модулей + интеграционный golden-тест на
`guide/ch_02_08.md` (макро-события).

## Структура

```text
tools/docs-llm/
  build.py                # CLI entrypoint
  builder.py              # двухпроходная сборка + bundle/index/listing
  validators.py           # валидаторы (HTML-теги, broken refs, размер)
  config.py               # загрузка topics.json + excluded.json
  topics.json             # explicit-mapping file → {prefix, ...}
  excluded.json           # файлы вне индекса
  README.md
  transform/
    __init__.py
    frontmatter.py        # снять Jekyll frontmatter
    toc.py                # удалить TOC details-блоки и метки
    callouts.py           # `{: .note-title }` → `Замечание: ...`
    images.py             # <img>, <p align="center">, ![]() → плейсхолдеры
    links.py              # резолв ссылок в (см. topic: <key>)
    sections.py           # split body по H2 + slugify anchor
  tests/
    __init__.py
    test_transforms.py    # юниты на каждый transform
    test_build.py         # интеграционный golden-тест
```

## Конвенции topics.json

```json
{
  "guide/ch_02_08.md": {
    "prefix": "макрос",
    "summary_prefix": "Макро-событие",
    "explicit_topics": {
      "Общие параметры событий": "макрос.ОбщиеПараметры"
    },
    "exclude_h2": ["Заголовок секции, которую не включать в индекс"]
  }
}
```

| Поле | Назначение |
| --- | --- |
| `prefix` | Префикс topic-key. Может содержать точки (`api.схема`). |
| `summary_prefix` | Сейчас не используется — задел для будущего обогащения index.json. |
| `explicit_topics` | Override для конкретных H2-заголовков, у которых auto-imя topic-key неудачно. |
| `exclude_h2` | H2-секции, не попадающие в topic-keys. |

Если файл не упомянут ни в `topics.json`, ни в `excluded.json` — сборка
падает с `Uncovered file:` (валидатор `validate_uncovered_files`).

## Конвенции excluded.json

Список путей, не индексируемых:

```json
[
  "guide/ch_03_01.md",       // конкретный файл
  "convert/",                // вся директория (любой файл с этим префиксом)
  "*.md"                     // wildcard fnmatch
]
```

Файлы из `topics.json` приоритетнее `excluded.json` — если файл
упомянут в обоих, он включается в индекс.

## Когда расширять покрытие

После каждого MVP-этапа:

1. Добавить новые файлы в `topics.json` с подходящим префиксом.
2. Удалить их из `excluded.json` (если были там).
3. `python3 tools/docs-llm/build.py` — проверить, что все валидаторы
   зелёные.
4. Прогнать тесты `python3 -m unittest discover tests`.
5. Закоммитить изменения `topics.json`, `excluded.json` и `/docs-llm/`
   одним коммитом.

## Контакт

Спецификация и архитектура — в pw_edt:
`specs/pw-217/spec.md`.
