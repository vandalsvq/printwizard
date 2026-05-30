// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// Сайт PrintWizard: лендинг (src/pages/index.astro) + документация (Starlight).
// План и решения: plans/pw-263/plan.md
export default defineConfig({
  site: 'https://printwizard.ru',
  integrations: [
    starlight({
      title: 'PrintWizard',
      defaultLocale: 'root',
      locales: {
        root: { label: 'Русский', lang: 'ru' },
      },
      customCss: ['./src/styles/custom.css'],
      // Сайдбар и редиректы добавляются в фазах 1–4 (генерируются скриптом миграции).
    }),
  ],
});
