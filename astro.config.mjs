// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import sidebar from './src/sidebar.mjs';

// Сайт PrintWizard: лендинг (src/pages/index.astro) + документация (Starlight).
// План и решения: plans/pw-263/plan.md
export default defineConfig({
  site: 'https://printwizard.ru',
  // Редиректы со старых /docs/*.html генерируются скриптом миграции как
  // реальные .html-файлы в public/docs/ (Astro копирует их в dist как есть) —
  // надёжно для статики S3/Yandex, где URL резолвится по точному ключу объекта.
  integrations: [
    starlight({
      title: 'PrintWizard',
      description: 'Конструктор печатных форм для 1С:Предприятие',
      favicon: '/favicon.png',
      head: [
        { tag: 'meta', attrs: { property: 'og:image', content: 'https://printwizard.ru/og.png' } },
        { tag: 'meta', attrs: { property: 'og:type', content: 'website' } },
        { tag: 'meta', attrs: { name: 'twitter:card', content: 'summary_large_image' } },
        { tag: 'meta', attrs: { name: 'twitter:image', content: 'https://printwizard.ru/og.png' } },
      ],
      defaultLocale: 'root',
      locales: {
        root: { label: 'Русский', lang: 'ru' },
      },
      logo: {
        src: './src/assets/logo.png',
        alt: 'PrintWizard',
      },
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/vandalsvq/printwizard' },
      ],
      customCss: [
        '@fontsource/inter/400.css',
        '@fontsource/inter/500.css',
        '@fontsource/inter/600.css',
        '@fontsource/inter/700.css',
        './src/styles/custom.css',
      ],
      sidebar,
    }),
  ],
});
