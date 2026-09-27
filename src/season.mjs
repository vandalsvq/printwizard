// Сезонная картинка превью ссылок (og:image / twitter:image).
//
// Зимнее оформление страниц включает в браузере public/winter.js, но мессенджеры
// и соцсети скриптов не выполняют — превью берут из готовой разметки. Поэтому
// картинку превью выбираем при сборке, а сайт пересобирается по расписанию
// на границах сезона (schedule в .github/workflows/deploy-site.yml).
//
// Даты — те же, что SEASON_START / SEASON_END в public/winter.js.
// Дата берётся по Москве: сборка на GitHub идёт в UTC.
// Проверка локально: PW_SEASON=winter npm run build (или PW_SEASON=off).

export const SEASON_START = [12, 15]; // [месяц, день], включительно
export const SEASON_END = [1, 31];

export function isWinter(date = new Date()) {
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: 'Europe/Moscow',
    month: 'numeric',
    day: 'numeric',
  }).formatToParts(date);
  const month = Number(parts.find((p) => p.type === 'month').value);
  const day = Number(parts.find((p) => p.type === 'day').value);
  const md = month * 100 + day;
  const from = SEASON_START[0] * 100 + SEASON_START[1];
  const to = SEASON_END[0] * 100 + SEASON_END[1];
  return from <= to ? md >= from && md <= to : md >= from || md <= to;
}

function winterNow() {
  if (process.env.PW_SEASON === 'winter') return true;
  if (process.env.PW_SEASON === 'off') return false;
  return isWinter();
}

export const ogImage = `https://printwizard.ru/${winterNow() ? 'og-winter.png' : 'og.png'}`;
