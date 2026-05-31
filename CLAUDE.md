# CLAUDE.md

Этот файл — руководство для Claude Code (claude.ai/code) при работе с кодом в этом репозитории.

## Что это за репозиторий

`pw_public` — **публичный репозиторий документации** PrintWizard (Конструктор печатных форм), расширения 1С:Предприятия для разработки печатных форм. Здесь лежит **только документация и инструменты её преобразования**. Сам продукт (код 1С/BSL) — в отдельном приватном репозитории `pw_edt`; упоминаемые здесь спецификации (например, `specs/pw-217/spec.md`) ссылаются туда.

Единственный источник истины пользовательской документации — [`src/content/docs`](src/content/docs/) (Astro Starlight). Всё остальное — производные артефакты или инструменты сборки. Правообладатель: ООО «Энспейс».

## Три конвейера документации

### 1. Astro Starlight-сайт → printwizard.ru

Публичный сайт (маркетинговый лендинг на `/` + документация внутри) собирается из `src/content/docs`, `src/pages/`, `astro.config.mjs` через Astro Starlight. Навигация — ручной `src/sidebar.mjs`, картинки — `public/img` (+ `public/draw_io`), редирект-заглушки старых URL — `public/docs`.

```bash
npm install
npm run dev      # превью (лендинг + документация) на localhost
npm run build    # прод-сборка в dist/
```

Боевой деплой — [.github/workflows/deploy-site.yml](.github/workflows/deploy-site.yml): на push в `master` собирает Astro (`npm ci && npm run build` → `dist/`), заливает в Yandex Object Storage (`s3 sync` на `printwizard.ru` + сброс CDN) и публикует redirect-заглушку `gh-pages-stub/` на GitHub Pages (старый адрес документации ведёт на printwizard.ru). Прежний Jekyll-конвейер удалён.

### 2. `/docs-llm` — машиночитаемая документация для встроенного AI-ассистента

[`tools/docs-llm/`](tools/docs-llm/) — генератор на Python (только stdlib, 3.9+), который компилирует `src/content/docs` в [`/docs-llm`](docs-llm/). Результат питает AI-ассистента **внутри продукта 1С**: `bundle.txt` импортируется в pw_edt как `CommonTemplate pw_АссистентДокументация` и отдаётся в рантайме через `PW_GetDocs(topic)`.

```bash
python3 tools/docs-llm/build.py             # полная пересборка /docs-llm
python3 tools/docs-llm/build.py --check     # сборка во временную папку + проверка синхронности /docs-llm (exit 1 при расхождении)
python3 tools/docs-llm/build.py --output /tmp/x   # сборка в другое место
cd tools/docs-llm && python3 -m unittest discover tests   # все тесты
cd tools/docs-llm && python3 -m unittest tests.test_build # один тестовый модуль
```

**`/docs-llm` — сгенерированный артефакт, руками не править.** Ручные правки перезаписываются при следующей сборке. В feature-ветках `/docs-llm` может отставать от `/docs` — это нормально; синхронизация происходит только после merge в `master`.

### 3. `docs/regmin/` — PDF-комплект для Минцифры (подача в реестр)

**Отдельная, независимая** сборка ([docs/regmin/build_docs.py](docs/regmin/build_docs.py)), которая рендерит три markdown-руководства (install guide / user manual / lifecycle) в PDF через headless Chrome. Не часть конвейеров сайта или docs-llm.

```bash
python3 docs/regmin/build_docs.py                 # собрать все три PDF
python3 docs/regmin/build_docs.py --only user-manual
```

## Архитектура сборки docs-llm (то, для чего нужно прочесть несколько файлов)

Генератор — детерминированный трёхпроходный компилятор. Ядро — [tools/docs-llm/builder.py](tools/docs-llm/builder.py):

- **Проход 1 `build_topics`** — для каждого `.md`: применить шаги `transform/` по порядку (`frontmatter` → `toc` → `callouts` → `images` → `links.inline_references`), разбить тело по заголовкам H2 и создать один **topic** на каждую H2-секцию. Строит `anchor_index` вида `(файл, якорь) → topic_key` (включая якоря H3 и запись `None` для первого topic'а файла) — нужен для резолва ссылок.
- **Проход 2 `resolve_links`** — переписывает внутренние ссылки в `(см. topic: <key>)` через anchor-индекс и извлекает `see_also`.
- **Проход 3 `write_outputs`** — пишет `topics/{key}.md` (полное тело, для review в PR), `bundle.txt` (склеенные тела с маркерами `### TOPIC: <key> ###`, артефакт рантайма), `index.json` (`key → {file, anchor, summary, see_also}`) и `listing.txt` (плоский индекс для `PW_GetDocs("список")`). `remove_orphan_topics` удаляет устаревшие `topics/*.md`.

Ключевые инварианты:

- **Topic-keys** иерархические, с точкой-разделителем: lower-case префикс + хвост в PascalCase из заголовка H2 (`heading_to_topic_name`), например `макрос.ПередИнициализацией`, `api.схема.Загрузить`. Кириллица — ожидаема (`TOPIC_KEY_RE`).
- **`RESPONSE_CAP = 3000`** здесь информационный — cap применяется только в BSL-рантайме в `PW_GetDocs`. `bundle.txt` и `topics/*.md` хранят **полное** тело.
- В заголовке `bundle.txt` лежат `pw_public_commit_sha` и `build_timestamp`; они недетерминированы и исключаются из сравнения синхронности в `--check`.

### Конфигурация покрытия — каждый `src/content/docs/*.md` должен быть классифицирован

[tools/docs-llm/config.py](tools/docs-llm/config.py) загружает два файла:

- [topics.json](tools/docs-llm/topics.json) — явный маппинг `файл → {prefix, explicit_topics, exclude_h2, ...}` для файлов, которые ИНДЕКСИРУЮТСЯ.
- [excluded.json](tools/docs-llm/excluded.json) — пути / префиксы директорий / `fnmatch`-globs, которые НЕ индексируются.

Файл, не упомянутый **ни там, ни там**, валит сборку (`Uncovered file:` в `validators.py`). Если файл в обоих — побеждает `topics.json`. **Добавляя новый файл в `src/content/docs`, зарегистрируйте его в одном из двух** (ключи — slug-пути вида `guide/ch-01-01.md`), затем пересоберите и прогоните тесты.

## CI / работа с ветками

- Правьте `src/content/docs` (или `tools/docs-llm/**`) → открывайте PR. Workflow [docs-llm-build.yml](.github/workflows/docs-llm-build.yml) на PR гоняет unit-тесты и неблокирующую проверку сборки.
- На push в `master` тот же workflow пересобирает `/docs-llm` и, если он изменился, открывает **авто-мержащийся** бот-PR (`bot/docs-llm-auto-update`), который вливается за пару минут. То есть изменения `/docs-llm` приезжают автоматически — не коммитьте их руками вместе с правками `src/content/docs`, если только это не намеренно.
- Основная ветка для PR — `master`. В сообщениях коммитов ссылайтесь на issue (`#NNN`).

## Редизайн на Astro Starlight (ветка `feature/site-redesign`)

Ветка переводит публичный сайт с Jekyll на **Astro Starlight** (лендинг на `/` + документация внутри). План — [plans/pw-263/plan.md](plans/pw-263/plan.md), трекер ревизии — [plans/pw-263/docs-review.md](plans/pw-263/docs-review.md).

**Сделано:** каркас Astro, миграция документации, брендинг, лендинг, редиректы (фазы 0–4) и **единое хранение** (Фаза 6) — `src/content/docs` стал единственным источником; `/docs` (кроме `regmin/`) и миграционный скрипт удалены; `docs-llm` переключён на новый источник; навигация/редиректы/картинки закоммичены (`src/sidebar.mjs`, `public/`).

**Фаза 5 (боевой деплой) — подготовлена:** `deploy-site.yml` (Astro → Yandex + GH Pages-заглушка) заменил `jekyll.yml`; `_config.yml`/`Gemfile`/`index.md` удалены. Боевой деплой запускается автоматически после merge `feature/site-redesign` → `master`. После этого все фазы редизайна (0–6) выполнены.
