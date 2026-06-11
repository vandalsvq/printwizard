// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import sitemap from '@astrojs/sitemap';
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
        // Яндекс.Метрика (счётчик 109784676) — на всех страницах документации.
        {
          tag: 'script',
          content: `(function(m,e,t,r,i,k,a){
        m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
        m[i].l=1*new Date();
        for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
        k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)
    })(window, document,'script','https://mc.yandex.ru/metrika/tag.js?id=109784676', 'ym');
    ym(109784676, 'init', {ssr:true, webvisor:true, clickmap:true, ecommerce:"dataLayer", referrer: document.referrer, url: location.href, accurateTrackBounce:true, trackLinks:true});`,
        },
        {
          tag: 'noscript',
          content: '<div><img src="https://mc.yandex.ru/watch/109784676" style="position:absolute; left:-9999px;" alt="" /></div>',
        },
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
    // Генерирует sitemap-index.xml + sitemap-0.xml в dist/ на основе `site`.
    // Starlight автоматически подхватывает интеграцию и добавляет <link rel="sitemap">.
    sitemap(),
  ],
});
