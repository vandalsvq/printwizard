# /docs-llm — машиночитаемая документация для AI-агента PrintWizard

Производный артефакт, генерируется автоматически из [`/docs`](../docs/)
скриптом [`tools/docs-llm/build.py`](../tools/docs-llm/build.py). **Не
редактируйте файлы здесь руками** — любые ручные правки будут
перезаписаны при следующей сборке.

## Как обновляется

При merge правок `/docs` в `master` срабатывает GitHub Action
[`docs-llm build`](../.github/workflows/docs-llm-build.yml):

1. Запускает unit-тесты `tools/docs-llm/tests/`.
2. Запускает `python3 tools/docs-llm/build.py`.
3. Если `/docs-llm` изменился — коммитит результат от
   `docs-llm-bot` с маркером `[skip ci]` и пушит в `master`.

В feature-ветках `/docs-llm` может отставать от `/docs` — это
нормально. Финальная синхронизация происходит после merge.

## Запуск локально (опционально)

Если хотите увидеть результат до PR:

```bash
python3 tools/docs-llm/build.py
```

## Состав

| Файл | Назначение |
| --- | --- |
| `bundle.txt` | Concatenated topic bodies — импортируется в pw_edt как `CommonTemplate pw_АссистентДокументация` (BinaryData) |
| `index.json` | `topic-key → {file, anchor, summary, see_also}` — для review diff'ов в PR и тестов |
| `listing.txt` | Текст для `PW_GetDocs("список")` — плоский индекс с однострочными аннотациями (cap 3000 chars) |
| `topics/*.md` | Per-topic Markdown-файлы — для удобства review в PR. Содержат **полный** body topic'а синхронно с bundle (cap `RESPONSE_CAP=3000` применяется только в BSL-runtime при ответе `PW_GetDocs`) |

## Формат `bundle.txt`

Заголовок (заканчивается пустой строкой):

```text
# pw-llm-bundle v1
# pw_public_commit_sha: <40-hex>
# build_timestamp: <ISO-8601>
# topics_count: <N>
```

Далее — concatenated topic bodies. Маркер начала каждой секции —
`### TOPIC: <key> ###` на отдельной строке. Тело секции — до следующего
маркера или до конца файла.

Парсер в BSL находит маркер по точному совпадению строки и возвращает
текст между маркерами. Полный текст секции может превышать cap ответа
`PW_GetDocs` (3000 символов) — BSL применяет cap при возврате
пользователю с маркером `... [truncated, используйте более узкий topic]`.

**Bundle и `topics/*.md` хранят полный body без cap.** Cap — только
runtime-поведение `PW_GetDocs` в BSL.

## Topic-keys

Иерархические, с точкой-разделителем. Префиксы lower-case, хвост в
PascalCase из исходного H2-заголовка:

```text
макрос.ПередИнициализацией
макрос.ПриПолученииДанных
api.схема.Загрузить
api.исполнитель.Сформировать
xml.Template
наборы.СписокНаборов
```

Полный список — в `index.json` или через `PW_GetDocs("список")` из
агента.

## Что делать при расхождении

1. Если правили `/docs` — запустите `python3 tools/docs-llm/build.py`.
2. Если случайно изменили `/docs-llm` руками — `git checkout docs-llm/`,
   затем правьте `/docs` и пересобирайте.
3. Если изменили `tools/docs-llm/topics.json` или `excluded.json` —
   тоже пересоберите.

## Спецификация

Источник истины формата и контракта `PW_GetDocs(topic)`:
[`pw_edt/specs/pw-217/spec.md`](https://github.com/vandalsvq/printwizard/issues/217).
