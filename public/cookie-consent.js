/*
 * Баннер согласия на cookie и отложенная инициализация Яндекс.Метрики.
 *
 * Счётчик не загружается, пока посетитель не нажал «Принять»: основание
 * обработки для веб-аналитики в политике конфиденциальности — согласие,
 * поэтому до согласия никакие идентификаторы не собираются.
 * Выбор хранится в localStorage и переспрашивается только при его очистке.
 *
 * Подключается на всех страницах сайта: лендинг и /reestr/ — из <head>
 * соответствующих .astro, документация — через head в astro.config.mjs.
 */
(function () {
  'use strict';

  var COUNTER_ID = 109784676;
  var STORAGE_KEY = 'pw-cookie-consent';
  var POLICY_URL = '/licensing/privacy/';

  function readChoice() {
    try {
      return window.localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      // Приватный режим или запрет на хранение: считаем, что выбора нет.
      return null;
    }
  }

  function saveChoice(value) {
    try {
      window.localStorage.setItem(STORAGE_KEY, value);
    } catch (e) {
      /* не критично: баннер просто появится в следующий раз */
    }
  }

  function initMetrika() {
    if (window.ym && window.ym.l) return;
    var src = 'https://mc.yandex.ru/metrika/tag.js?id=' + COUNTER_ID;
    (function (m, e, t, r, i, k, a) {
      m[i] = m[i] || function () { (m[i].a = m[i].a || []).push(arguments); };
      m[i].l = 1 * new Date();
      for (var j = 0; j < document.scripts.length; j++) {
        if (document.scripts[j].src === r) return;
      }
      k = e.createElement(t);
      a = e.getElementsByTagName(t)[0];
      k.async = 1;
      k.src = r;
      a.parentNode.insertBefore(k, a);
    })(window, document, 'script', src, 'ym');

    window.ym(COUNTER_ID, 'init', {
      ssr: true,
      webvisor: true,
      clickmap: true,
      ecommerce: 'dataLayer',
      referrer: document.referrer,
      url: location.href,
      accurateTrackBounce: true,
      trackLinks: true
    });
  }

  function injectStyles() {
    if (document.getElementById('pw-cookie-styles')) return;
    var css = [
      '#pw-cookie{position:fixed;left:50%;transform:translateX(-50%);bottom:16px;z-index:9999;',
      'width:calc(100% - 32px);max-width:760px;box-sizing:border-box;padding:16px 20px;',
      'display:flex;gap:16px;align-items:center;flex-wrap:wrap;',
      'background:#fff;color:#1c1f24;border:1px solid rgba(0,0,0,.12);border-radius:12px;',
      'box-shadow:0 8px 32px rgba(0,0,0,.18);font-size:14px;line-height:1.5;',
      'font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif}',
      '#pw-cookie p{margin:0;flex:1 1 320px}',
      '#pw-cookie a{color:inherit;text-decoration:underline}',
      '#pw-cookie .pw-cookie-actions{display:flex;gap:8px;flex:0 0 auto}',
      '#pw-cookie button{font:inherit;cursor:pointer;border-radius:8px;padding:8px 16px;',
      'border:1px solid transparent;white-space:nowrap}',
      '#pw-cookie .pw-accept{background:#1c1f24;color:#fff}',
      '#pw-cookie .pw-accept:hover{opacity:.9}',
      '#pw-cookie .pw-decline{background:transparent;color:inherit;border-color:rgba(0,0,0,.2)}',
      '#pw-cookie .pw-decline:hover{background:rgba(0,0,0,.05)}',
      // Тема берётся у страницы, а не у системы: лендинг всегда светлый,
      // а документация Starlight проставляет data-theme на <html>.
      ":root[data-theme='dark'] #pw-cookie{background:#1c1f24;color:#f1f3f5;",
      'border-color:rgba(255,255,255,.16);box-shadow:0 8px 32px rgba(0,0,0,.5)}',
      ":root[data-theme='dark'] #pw-cookie .pw-accept{background:#f1f3f5;color:#1c1f24}",
      ":root[data-theme='dark'] #pw-cookie .pw-decline{border-color:rgba(255,255,255,.28)}",
      ":root[data-theme='dark'] #pw-cookie .pw-decline:hover{background:rgba(255,255,255,.08)}",
      '@media (max-width:520px){#pw-cookie .pw-cookie-actions{width:100%}',
      '#pw-cookie .pw-cookie-actions button{flex:1 1 auto}}'
    ].join('');
    var style = document.createElement('style');
    style.id = 'pw-cookie-styles';
    style.appendChild(document.createTextNode(css));
    document.head.appendChild(style);
  }

  function showBanner() {
    if (document.getElementById('pw-cookie')) return;
    injectStyles();

    var box = document.createElement('div');
    box.id = 'pw-cookie';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-live', 'polite');
    box.setAttribute('aria-label', 'Согласие на использование cookie');

    var text = document.createElement('p');
    text.innerHTML =
      'Мы хотим включить Яндекс.Метрику, чтобы понимать, как посетители пользуются сайтом. ' +
      'Она ставит cookie и записывает действия на странице. Без вашего согласия счётчик не ' +
      'загружается. Подробности — в <a href="' + POLICY_URL +
      '">политике конфиденциальности</a>.';

    var actions = document.createElement('div');
    actions.className = 'pw-cookie-actions';

    var decline = document.createElement('button');
    decline.type = 'button';
    decline.className = 'pw-decline';
    decline.textContent = 'Отклонить';

    var accept = document.createElement('button');
    accept.type = 'button';
    accept.className = 'pw-accept';
    accept.textContent = 'Принять';

    function close(choice) {
      saveChoice(choice);
      if (box.parentNode) box.parentNode.removeChild(box);
      if (choice === 'accepted') initMetrika();
    }

    decline.addEventListener('click', function () { close('declined'); });
    accept.addEventListener('click', function () { close('accepted'); });

    actions.appendChild(decline);
    actions.appendChild(accept);
    box.appendChild(text);
    box.appendChild(actions);
    document.body.appendChild(box);
  }

  function start() {
    var choice = readChoice();
    if (choice === 'accepted') {
      initMetrika();
    } else if (choice !== 'declined') {
      showBanner();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }

  // Отзыв согласия: ссылка с href="#cookie-settings" в подвале снова покажет баннер.
  document.addEventListener('click', function (event) {
    var link = event.target && event.target.closest ? event.target.closest('a[href="#cookie-settings"]') : null;
    if (!link) return;
    event.preventDefault();
    try { window.localStorage.removeItem(STORAGE_KEY); } catch (e) { /* пусто */ }
    showBanner();
  });
})();
