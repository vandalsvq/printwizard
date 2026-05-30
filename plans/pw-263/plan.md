# Редизайн сайта PrintWizard: лендинг + документация на Astro Starlight

> GitHub-задача: [#263](https://github.com/vandalsvq/printwizard/issues/263) · Ветка: `feature/site-redesign`

## Context

Сейчас на `printwizard.ru` планируется деплоить **только документацию** (Jekyll + Just-the-Docs → Yandex Object Storage + CDN). Владелец хочет, чтобы у сайта был **маркетинговый лендинг на корне `/`**, а документация жила **внутри** того же сайта. Пока готовится домен, делаем редизайн.

Принятые решения (с владельцем):

- **Движок:** Astro Starlight (статика, нативный «лендинг + доки», офлайн-поиск Pagefind).
- **Стиль лендинга:** чистый корпоративный SaaS — светлый, много воздуха, один акцентный цвет из бренда, крупный скриншот.
- **Документация:** полный рестайл под новый бренд.
- **Бренд:** палитра из логотипа-пазла — лайм `#8CC63F`, голубой `#7FB9DC`, лавандовый `#A89AC9`, серый `#929292`; метафора «форма собирается как пазл»; тон дружелюбный.
- Работаем на ветке **`feature/site-redesign`**.

## Объём ЭТОЙ итерации: фазы 0–4 (без боевого деплоя)

Делаем: каркас Starlight → полная миграция доков → брендинг/сайдбар/поиск → лендинг → локальное/staging-превью + редиректы. **Боевой `printwizard.ru`, `master`, текущий Jekyll-деплой и `docs-llm` НЕ трогаем.** `/docs` остаётся источником правды; `src/content/docs/` — генерируемое из него зеркало.

**Отложено до готовности домена / выхода новой версии ПО (фазы 5–6):** переключение CI/CD на Astro (`deploy-site.yml` вместо `jekyll.yml`), удаление `_config.yml`/`Gemfile`, GitHub Pages → страница-заглушка с переходом на `printwizard.ru`, адаптация `docs-llm` на новый источник, удаление `/docs`.

## Шаг 0 — Трекинг и хранение плана ✅

1. ✅ Создана задача в GitHub: [#263](https://github.com/vandalsvq/printwizard/issues/263).
2. ✅ Заведён каталог `plans/pw-263/`; план — `plans/pw-263/plan.md`. Сопутствующая документация (карта миграции файлов, список редиректов, заметки по кириллическим якорям, дизайн-решения лендинга, WARN-логи) складывается сюда же.
3. Коммиты связывать с задачей (`#263` в сообщениях).

## Целевая структура (в корне репозитория)

```text
pw_public/
├─ package.json, package-lock.json, astro.config.mjs, tsconfig.json
├─ src/
│  ├─ content.config.ts            # коллекция docs (схема Starlight)
│  ├─ content/docs/                # ГЕНЕРИРУЕТСЯ из /docs (трансформированный markdown)
│  │  ├─ guide/index.md            # бывш. docs/01_guide.md — оглавление раздела (/guide/)
│  │  ├─ guide/ch-01-01.md … ch-02-30.md, model/, history/, licensing/, convert/, http/, query/, llm/
│  ├─ pages/index.astro            # МАРКЕТИНГОВЫЙ ЛЕНДИНГ (корень /)
│  ├─ components/                  # Hero, Features, HowItWorks, CTA (.astro)
│  ├─ assets/                      # logo*.png + отобранные скриншоты (astro:assets)
│  └─ styles/custom.css            # брендинг (переменные Starlight) + стили лендинга
├─ public/
│  ├─ img/                         # копия docs/img/** (картинки документации) → /img/...
│  └─ fonts/                       # self-hosted Inter/Manrope
├─ tools/docs-llm/migrate/         # НОВЫЙ Python-пакет миграции (переиспользует transform/*)
├─ docs/, tools/docs-llm/, docs-llm/   # ОСТАЮТСЯ без изменений в этой итерации
└─ gh-pages-stub/index.html        # готовый артефакт заглушки (деплой отложен)
```

Жёсткие факты-ловушки, которые скрипт миграции обязан учесть (проверено в репозитории):

- **Fenced-frontmatter баг:** в `docs/licensing/*.md`, `docs/17_objects.md`, всех `docs/convert/*.md` frontmatter обёрнут в ```` ``` ```` вокруг `---`. Astro это не распарсит → снимать обёртку перед парсингом.
- **Висячий `parent: Сериализатор`** в `convert/*.md` (нет узла с таким title) → подвесить под синтетическую группу «Сериализатор» внутри «Интеграции».
- **Заголовки `pw#template` / `pw#field#…`** в `convert/*` → slug без `#` (`pw-template`), label в сайдбаре оставить читаемым.
- **Имена `history/*` с пробелами, смешением `х`/`x` и висячим пробелом** (`2023 - 1.1.2.х .md`) → ASCII-slug по явному словарю; нет `nav_order` → сортировка по убыванию (`child_nav_order: desc`).
- **Битые ссылки уже сейчас** (`16_xml.html`, `ch_02_20.html`) → WARN-лог, не падать.
- **Кириллические якоря Jekyll ≠ Starlight** → строить явную `anchor_map` (старый→новый якорь) из заголовков, а не угадывать.
- `regmin/` (материалы Минцифры) и `draw_io/` (SVG-исходники) — **в Starlight не тащим**.

## Фаза 0 — Окружение + каркас (риск низкий)

- `brew install node` (Node 20). Зафиксировать `engines`/`.nvmrc` = 20 (как в будущем CI).
- Создать `package.json`, `astro.config.mjs`, `content.config.ts`, `tsconfig.json` (шаблон `@astrojs/starlight`), `npm install`.
- Базовый конфиг: `site: 'https://printwizard.ru'`, `defaultLocale: 'root'`, `locales.root = { label:'Русский', lang:'ru' }`, `customCss: ['./src/styles/custom.css']`, `logo`.
- **Проверка:** `npm run dev` поднимает пустой Starlight на `localhost`.

## Фаза 1 — Скрипт миграции контента (риск средний)

Пакет `tools/docs-llm/migrate/to_starlight.py` (по образцу `build.py`, режим `--check` для детерминизма). **Переиспользует** `tools/docs-llm/transform/`:

- `frontmatter.strip_frontmatter`, `toc.apply` — напрямую.
- `links._split_url`, `links.inline_references` — напрямую (резолв путей/якорей, инлайн reference-ссылок).
- `sections.slugify` + H2/H3-regex — для вычисления **старых** Jekyll-якорей в `anchor_map`.
- `callouts._CALLOUT_RE`, `images.*_RE` — regex переиспользуем, **замены пишем заново** (сохраняем разметку, не схлопываем в текст как docs-llm).

Алгоритм (2 прохода):

1. **Индекс:** `path_map` (старый `guide/ch_02_05.md` → новый slug `/guide/ch-02-05/`) и `anchor_map` ((файл, старый-якорь) → новый-якорь).
2. **На каждый файл:** снять fenced-обёртку → распарсить frontmatter → собрать Starlight-frontmatter (`title`; `sidebar.order`←`nav_order`; `nav_exclude`→`sidebar.hidden:true`; снять дублирующий H1) → `toc.apply` → callouts `{: .note-title }`→`:::note[Заголовок]`, `{: .important-title }`→`:::caution[…]` → `<img src="./../img/…">`→`![](/img/…)` (+ снять `style/width`, `<p align=center>`, `<br>`-подписи) → переписать `.html`-ссылки на slug+новый-якорь (dangling → WARN, текст без href).
3. **Запись** в `src/content/docs/**`; копия `docs/img/**`→`public/img/**` (кроме `logo*.png`); печать готовых фрагментов `sidebar` и `redirects`.

- Юнит-тесты по образцу `tools/docs-llm/tests/test_transforms.py` (fenced-баг, asides, anchor-map, dangling, переименования).
- **Проверка:** `astro build` без ошибок схемы; в `astro dev` страницы открываются, картинки видны, внутренние ссылки/якоря резолвятся; WARN-список просмотрен; выборочно 5–10 якорных ссылок.

## Фаза 2 — Сайдбар, брендинг, поиск (риск низкий)

- **Сайдбар:** скрипт генерирует явный `sidebar`-массив из `parent`/`grand_parent`/`nav_order` (autogenerate по папкам не подходит — файлы плоские). Группы: Документация (Про PrintWizard, Настройка макета, Примеры разработки, Установка/Регистрация/Требования), Настройка, Объекты расширения, Интеграция (Объектная модель + синтетическая «Сериализатор»), Лицензирование, История версий (desc), План развития. `nav_exclude`→`hidden`.
- **Брендинг** (`src/styles/custom.css`): акцент для интерактива — затемнённый бренд-голубой `#2E6E96` (проходит WCAG AA; светлый `#7FB9DC` для текста не годится), исходные бренд-цвета — только декор/иконки/чипы-пазлы. Переопределить `--sl-color-accent{,-low,-high}` для светлой/тёмной темы; `--sl-font` = Inter/Manrope (self-hosted в `public/fonts/`); логотип `logoname.png` в шапке (`replacesTitle:true`); `.sl-markdown-content img { max-width:100%; height:auto; margin-inline:auto }`.
- **Поиск:** Pagefind встроен — индексируется на `astro build`, отдельной настройки не нужно; `lang:'ru'` для русского UI; кириллица индексируется.
- **Проверка:** дерево навигации совпадает со старым (включая desc-историю и скрытые privacy/eap), поиск находит кириллицу, контраст ссылок проходит (axe/devtools).

## Фаза 3 — Лендинг (риск низкий-средний)

`src/pages/index.astro` (свой лёгкий layout, переиспользует CSS-переменные Starlight для единого бренда). Контент — из корневого `index.md`. Секции:

1. **Hero** — заголовок «PrintWizard — конструктор печатных форм для 1С», подзаголовок, 2 CTA («Скачать community» (скоро/disabled), «Документация»→`/guide/`), крупный скриншот, логотип-пазл.
2. **Преимущества** — `CardGrid`/`Card` (Starlight) или свои карточки, 4–6 пунктов, акценты в бренд-цветах.
3. **Как работает** — 3–4 блока «текст + скриншот» (alternating) из глав «Без конфигуратора / Прозрачность связей / Дружелюбный интерфейс / Универсальность».
4. **Аудитория** — аналитик / разработчик / руководитель.
5. **Соц.доказательство** — статьи Infostart (4 ссылки), Telegram `t.me/isprintwizard`, Infostart Marketplace.
6. **CTA** — скачать community / читать доки / сообщить об ошибке (GitHub issues).
7. **Футер** — «© 2020–2026 ООО ЭНСПЕЙС», ссылки.

- Скриншоты: отобрать 4–6 из `docs/img/ch_01`, `ch_02` → `src/assets/screenshots/` (под `astro:assets` `<Image>`); логотипы → `src/assets/`.
- **Проверка:** лендинг на `/` в `astro dev`, мобильная адаптивность, CTA ведут куда надо, дизайн-ревью с владельцем.

## Фаза 4 — Сборка, редиректы, превью, заглушка (риск средний, без боевого)

- **Редиректы** старых URL (`/docs/guide/ch_01_01.html` → `/guide/ch-01-01/`, ~50 правил) через `redirects` в `astro.config.mjs` (Astro на статике генерит meta-refresh HTML-заглушки в `dist/`). Список печатает скрипт миграции (он знает `path_map`) → `src/redirects.generated.mjs`.
- **GitHub Pages заглушка:** подготовить `gh-pages-stub/index.html` — брендированная страница «Документация переехала на printwizard.ru» с авто-redirect + видимой кнопкой. **Только файл-артефакт; деплой в GH Pages — в отложенной фазе 5.**
- **Превью без боевого:** `astro build` → проверить `dist/` (страницы, картинки, redirect-заглушки, sitemap/canonical). Залить `dist/` в отдельный **staging-бакет/префикс** для демонстрации (НЕ в `s3://printwizard.ru/`, `jekyll.yml` не трогаем).
- **Проверка:** открыть ~10 старых URL → редиректят; staging-превью смотрит владелец; решение об отказе/правках до боевого.

## Отложенное (фазы 5–6, при готовности домена / новой версии ПО)

- **Фаза 5 (боевой, риск высокий):** `deploy-site.yml` (Node вместо Ruby, `dist/` вместо `_site_yc/`, те же секреты YC, `s3 sync --delete` + CDN purge); удалить `jekyll.yml`; GitHub Pages → деплой `gh-pages-stub` (без base-path мороки полного зеркала); обновить `.gitignore` (+`dist/`,`node_modules/`,`.astro/`); удалить `_config.yml`/`Gemfile*`; merge в `master`; план отката (revert + повторный Jekyll). Делать в окно низкого трафика.
- **Фаза 6 (docs-llm, риск средний):** переключить `tools/docs-llm/build.py` на `src/content/docs/`; переписать `transform/callouts.py` (asides→текст), `links.py` (slug-ссылки без `.html`); перегенерировать ключи `topics.json`/`excluded.json`; править триггер-пути `docs-llm-build.yml`; затем удалить `/docs`.

## Follow-up: ревизия контента документации (отложено)

Перенос документации технически корректен (frontmatter, callouts, ссылки, якоря,
картинки), но **содержимое страниц нужно пройти шаг за шагом** — вычитать тексты,
проверить актуальность, единообразие, оформление callouts/таблиц/картинок после
миграции. Делается отдельной задачей, не блокирует Фазы 0–4. Известные технические
артефакты для проверки при ревизии: 5 изначально битых ссылок в исходниках
(`16_xml.html`, `ch_02_20.html` ×2, `develop.html`, `.pdwx`-файл) — их стоит
починить в исходных `/docs` или принять.

## Критичные файлы для переиспользования

- `tools/docs-llm/transform/links.py` — `_split_url`, `inline_references` (ядро резолва ссылок/якорей).
- `tools/docs-llm/transform/sections.py` — `slugify` + H2/H3-regex (старые Jekyll-якоря для `anchor_map`).
- `tools/docs-llm/transform/{frontmatter,toc,callouts,images}.py` — `strip_frontmatter`, `toc.apply` напрямую; `_CALLOUT_RE`/`*_IMG_RE` как regex-основа.
- `tools/docs-llm/builder.py` — образец 2-проходной сборки + чтение frontmatter-полей для дерева сайдбара.
- `.github/workflows/jekyll.yml` — шаблон деплоя на Yandex (для отложенной фазы 5).
- `index.md` — единственный источник контента лендинга + карта старых ссылок для redirects.

## Верификация (по завершении фаз 0–4)

1. `npm run build` — без ошибок; `dist/` содержит лендинг, все страницы доков, redirect-заглушки, Pagefind-индекс, sitemap.
2. `npm run dev` — ручной обход: лендинг `/`, оглавление `/guide/`, 10–15 страниц доков, картинки, внутренние ссылки и кириллические якоря, поиск по кириллице, светлая/тёмная тема, мобильная вёрстка.
3. Скрипт миграции `--check` зелёный (детерминизм); WARN-лог dangling-ссылок просмотрен вручную.
4. `python -m unittest discover tools/docs-llm/tests` (новые тесты миграции + существующие docs-llm не сломаны — docs-llm не менялся).
5. Открыть ~10 старых URL вида `/docs/guide/ch_01_01.html` на staging → редирект на новый slug.
6. Дизайн-ревью лендинга и доков с владельцем на staging-превью до любого боевого шага.
