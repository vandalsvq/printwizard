// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import sidebar from './src/sidebar.generated.mjs';

// Сайт PrintWizard: лендинг (src/pages/index.astro) + документация (Starlight).
// План и решения: plans/pw-263/plan.md
export default defineConfig({
  site: 'https://printwizard.ru',
  integrations: [
    starlight({
      title: 'PrintWizard',
      description: 'Конструктор печатных форм для 1С:Предприятие',
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
      // Редиректы со старых /docs/*.html добавляются в Фазе 4.
    }),
  ],
});
