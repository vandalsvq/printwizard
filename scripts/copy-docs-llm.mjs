// Публикация машиночитаемой документации (/docs-llm) на сайте.
//
// Astro копирует содержимое public/ в dist/ как есть, поэтому перед сборкой
// (npm run build → хук prebuild) кладём артефакты /docs-llm в public/docs-llm/.
// Так они попадают в dist/ и деплоятся на printwizard.ru, где доступны по
// стабильным URL, например https://printwizard.ru/docs-llm/bundle.txt
//
// Копируем только рантайм-артефакты (bundle.txt/index.json/listing.txt) и
// README — каталог topics/ намеренно НЕ публикуем: это внутренние файлы для
// review в PR (см. CLAUDE.md, «Архитектура сборки docs-llm»).
//
// public/docs-llm/ — генерируемый каталог, в git не коммитится (см. .gitignore).

import { cp, mkdir, rm } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = join(root, 'docs-llm');
const dest = join(root, 'public', 'docs-llm');

const FILES = ['bundle.txt', 'index.json', 'listing.txt', 'README.md'];

await rm(dest, { recursive: true, force: true });
await mkdir(dest, { recursive: true });

for (const name of FILES) {
  await cp(join(src, name), join(dest, name));
}

console.log(`[copy-docs-llm] published ${FILES.length} files → public/docs-llm/`);
