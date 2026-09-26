/*
 * Зимнее оформление сайта: с 15 декабря по 31 января (даты — ниже).
 *
 * Ставит на <html> атрибут data-season="winter": все стили сезона лежат под ним
 * (src/styles/winter.css), вне сезона они не срабатывают, а картинки не грузятся.
 * Скрипт подключён в <head> без defer, чтобы атрибут появился до первой отрисовки.
 *
 * Проверка вне сезона: ?winter=1 — включить (и заново заморозить логотип),
 * ?winter=0 — выключить; выбор запоминается до закрытия вкладки.
 *
 * Пасхалка: логотип в шапке вмёрз в лёд. Щелчки мышью бьют по льду — трещина,
 * ещё трещина, на третий лёд разлетается, а детали пазла встряхиваются. После
 * этого логотип снова обычная ссылка, и до закрытия вкладки лёд не возвращается.
 * Enter с клавиатуры лёд не трогает — переход по ссылке работает всегда.
 */
(function () {
  var SEASON_START = [12, 15]; // [месяц, день], включительно
  var SEASON_END = [1, 31];
  var KEY_FORCE = 'pw-winter';
  var KEY_BROKEN = 'pw-ice-broken';
  var KEY_DRIFT = 'pw-drift';
  var SVG_NS = 'http://www.w3.org/2000/svg';

  function sget(key) {
    try { return sessionStorage.getItem(key); } catch (e) { return null; }
  }
  function sset(key, value) {
    try {
      if (value === null) sessionStorage.removeItem(key);
      else sessionStorage.setItem(key, value);
    } catch (e) { /* хранилище недоступно — не страшно */ }
  }

  var forced = /[?&]winter=([01])(?:&|#|$)/.exec(location.search);
  if (forced) {
    sset(KEY_FORCE, forced[1]);
    // Явный ?winter=1 возвращает лёд на логотип и начинает сугроб заново —
    // удобно показывать всё ещё раз.
    if (forced[1] === '1') {
      sset(KEY_BROKEN, null);
      sset(KEY_DRIFT, null);
    }
  }
  var force = sget(KEY_FORCE);

  function inSeason(date) {
    var md = (date.getMonth() + 1) * 100 + date.getDate();
    var from = SEASON_START[0] * 100 + SEASON_START[1];
    var to = SEASON_END[0] * 100 + SEASON_END[1];
    return from <= to ? md >= from && md <= to : md >= from || md <= to;
  }

  if (force === '0' || (force !== '1' && !inSeason(new Date()))) return;
  document.documentElement.setAttribute('data-season', 'winter');

  var calm = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  ready(function () {
    var header = document.querySelector('header.header, .site-header');
    if (header) icicles(header);
    drift(header);
    if (sget(KEY_BROKEN) !== '1') {
      var logos = document.querySelectorAll('.site-title img, .site-header .brand img');
      for (var i = 0; i < logos.length; i++) freeze(logos[i]);
    }
    var hero = document.querySelector('.hero');
    if (hero && !calm) snowfall(hero);
  });

  /* --- Сосульки под шапкой ------------------------------------------------ */

  // Раскладка строится сразу на всю ширину шапки — без повторяющейся плитки.
  // Генератор с постоянным зерном: при каждой загрузке та же картина, а при
  // смене ширины меняется только правый край. Слой лежит в <body> под шапкой
  // (position: fixed): внутри шапки Starlight его бы обрезало, а на лендинге
  // размытие фона у шапки не дало бы льду «видеть» страницу за собой.

  function icicles(header) {
    var box = document.createElement('div');
    box.className = 'pw-icicles';
    box.setAttribute('aria-hidden', 'true');
    // Стекло: размытие того, что под сосульками, строго по их силуэту (маска).
    var glass = document.createElement('div');
    glass.className = 'pw-icicles-glass';
    var art = document.createElement('div');
    box.appendChild(glass);
    box.appendChild(art);
    document.body.appendChild(box);

    var tips = [];
    var built = '';
    var docs = header.matches('header.header');

    function place() {
      var rect = header.getBoundingClientRect();
      var z = getComputedStyle(header).zIndex;
      box.style.zIndex = z === 'auto' ? '10' : z;
      box.style.top = rect.bottom - 1 + 'px';
      // Уже 72rem под шапкой документации встаёт панель «На этой странице»:
      // сосульки мельче, чтобы не закрывали её кнопку.
      var scale = docs && window.innerWidth < 72 * 16 ? 0.6 : 1;
      var key = Math.round(rect.width) + ':' + scale;
      if (key === built) return;
      built = key;
      var ice = buildIcicles(Math.round(rect.width), scale);
      art.innerHTML = ice.svg;
      box.style.height = ice.height + 'px';
      var mask = 'url("' + ice.mask + '")';
      glass.style.webkitMaskImage = mask;
      glass.style.maskImage = mask;
      tips = ice.tips;
    }

    place();
    window.addEventListener('resize', place);
    if (window.ResizeObserver) new ResizeObserver(place).observe(header);
    if (!calm) drip(box, function () { return tips; });
  }

  // Детерминированный генератор (mulberry32).
  function seeded(seed) {
    return function () {
      seed = (seed + 0x6d2b79f5) | 0;
      var t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function between(rnd, a, b) {
    return a + rnd() * (b - a);
  }

  function n1(v) {
    return Math.round(v * 10) / 10;
  }

  // Нижний край снежного карниза: несоизмеримые синусоиды — без видимого ритма.
  function ledgeY(x, scale) {
    var y = 5.2 + 1.5 * Math.sin(x / 27 + 0.6) + 0.9 * Math.sin(x / 9.7 + 2.1) + 0.45 * Math.sin(x / 4.3 + 4);
    return y * (0.6 + 0.4 * scale);
  }

  // Гладкая кривая через точки (Catmull-Rom → кубические Безье).
  function smooth(p, closed) {
    var n = p.length;
    var d = 'M' + n1(p[0][0]) + ' ' + n1(p[0][1]);
    var last = closed ? n : n - 1;
    for (var i = 0; i < last; i++) {
      var p0 = p[i > 0 || closed ? (i - 1 + n) % n : i];
      var p1 = p[i];
      var p2 = p[(i + 1) % n];
      var p3 = i + 2 < n || closed ? p[(i + 2) % n] : p2;
      d += 'C' + n1(p1[0] + (p2[0] - p0[0]) / 6) + ' ' + n1(p1[1] + (p2[1] - p0[1]) / 6) + ' ' +
        n1(p2[0] - (p3[0] - p1[0]) / 6) + ' ' + n1(p2[1] - (p3[1] - p1[1]) / 6) + ' ' + n1(p2[0]) + ' ' + n1(p2[1]);
    }
    return closed ? d + 'Z' : d;
  }

  // Одна сосулька: толстый корень уходит в снег, к кончику сужается,
  // по длине — волнистые наплывы, сама чуть изогнута.
  function oneIcicle(rnd, x, len, scale) {
    var root = ledgeY(x, scale) - 2.5;
    var w0 = Math.min(8, Math.max(1.8, len * 0.17 + 1.6)) * (0.55 + 0.45 * scale);
    var bend = between(rnd, -1.8, 1.8) * scale;
    var ripples = Math.max(1.5, len / 6.5);
    var phase = between(rnd, 0, Math.PI * 2);
    var n = Math.max(8, Math.min(30, Math.round(len * 0.8)));
    var left = [], right = [], spine = [];
    for (var i = 0; i <= n; i++) {
      var t = i / n;
      var w = w0 * Math.pow(1 - t, 0.85) * (1 + 0.12 * Math.sin(Math.PI * 2 * ripples * t + phase));
      if (t < 0.14) w *= 1 + 0.7 * Math.pow(1 - t / 0.14, 2);
      var cx = x + bend * t * t;
      var y = root + t * (len + 2.5);
      left.push([cx - w, y]);
      right.push([cx + w, y]);
      spine.push([cx, y, w]);
    }
    var tip = [spine[n][0], spine[n][1]];
    var outline = left.slice(0, n).concat([[tip[0], tip[1] + 0.35]], right.slice(0, n).reverse());
    var glint = [], edge = [];
    for (var k = 2; k < Math.floor(n * 0.72); k++) glint.push([spine[k][0] - spine[k][2] * 0.45, spine[k][1]]);
    for (var m = 3; m < Math.floor(n * 0.6); m++) edge.push([spine[m][0] + spine[m][2] * 0.5, spine[m][1]]);
    return {
      body: smooth(outline, true),
      glint: glint.length > 1 ? smooth(glint, false) : '',
      edge: edge.length > 1 ? smooth(edge, false) : '',
      tip: tip,
      len: len,
      w0: w0,
      drop: len > 11 && rnd() < 0.5 ? between(rnd, 0.9, 1.4) * (0.6 + 0.4 * scale) : 0
    };
  }

  function buildIcicles(width, scale) {
    var rnd = seeded(20261215);
    var items = [];
    var x = between(rnd, 18, 40);
    function add(ix, len) {
      var ice = oneIcicle(rnd, ix, len * scale, scale);
      if (ix > 8 && ix < width - 8) items.push(ice);
    }
    // Гроздья (одна длинная и 1–3 короче рядом), одиночки и пустые участки.
    while (x < width - 20) {
      var kind = rnd();
      if (kind < 0.45) {
        var main = rnd() < 0.1 ? between(rnd, 30, 40) : between(rnd, 14, 30);
        add(x, main);
        var extra = 1 + Math.floor(rnd() * 4);
        for (var j = 0; j < extra; j++) add(x + (rnd() < 0.5 ? -1 : 1) * between(rnd, 4, 16), between(rnd, 3, main * 0.65));
        x += between(rnd, 40, 95);
      } else if (kind < 0.85) {
        add(x, between(rnd, 3, 14));
        x += between(rnd, 12, 34);
      } else {
        x += between(rnd, 30, 80);
      }
    }
    items.sort(function (a, b) { return b.len - a.len; }); // длинные позади коротких

    var height = Math.ceil(40 * scale + 16);
    var bottom = [];
    for (var bx = 0; bx <= width + 4; bx += 4) bottom.push([bx, n1(ledgeY(bx, scale))]);
    var snow = 'M0 0H' + (width + 4) + 'V' + bottom[bottom.length - 1][1];
    for (var q = bottom.length - 1; q >= 0; q--) snow += 'L' + bottom[q][0] + ' ' + bottom[q][1];
    snow += 'Z';
    var snowEdge = 'M' + bottom.map(function (p) { return p[0] + ' ' + p[1]; }).join('L');

    var art = [], silhouettes = [];
    items.forEach(function (ice, i) {
      // Тело и изморозь у корня — один контур: <use> наследует заливку от себя,
      // а не от оригинала, поэтому заливки висят на обёртке и на <use>.
      art.push('<g class="b" fill="url(#pw-ice-b)"><path id="pw-i' + i + '" d="' + ice.body + '"/></g>' +
        '<use href="#pw-i' + i + '" class="f" fill="url(#pw-ice-f)"/>');
      if (ice.edge) art.push('<path class="r" d="' + ice.edge + '"/>');
      if (ice.glint && ice.len > 6) {
        art.push('<path class="h" stroke-width="' + n1(Math.min(1.1, 0.5 + ice.w0 * 0.12)) + '" d="' + ice.glint + '"/>');
      }
      if (ice.drop) {
        art.push('<circle fill="url(#pw-ice-d)" cx="' + n1(ice.tip[0]) + '" cy="' + n1(ice.tip[1] + ice.drop * 0.6) + '" r="' + n1(ice.drop) + '"/>');
      }
      silhouettes.push(ice.body);
    });

    var svg =
      '<svg class="pw-icicles-art" xmlns="' + SVG_NS + '" width="' + width + '" height="' + height + '" viewBox="0 0 ' + width + ' ' + height + '">' +
      '<defs>' +
      '<linearGradient id="pw-ice-b" x2="1"><stop offset="0" class="s1"/><stop offset=".18" class="s2"/><stop offset=".45" class="s3"/><stop offset=".78" class="s4"/><stop offset="1" class="s5"/></linearGradient>' +
      '<linearGradient id="pw-ice-f" x2="0" y2="1"><stop offset="0" class="sf"/><stop offset=".4" class="sf0"/></linearGradient>' +
      '<radialGradient id="pw-ice-d" cx=".35" cy=".35" r=".7"><stop offset="0" class="sd1"/><stop offset="1" class="sd2"/></radialGradient>' +
      '<linearGradient id="pw-snow" x2="0" y2="1"><stop offset="0" class="sn1"/><stop offset="1" class="sn2"/></linearGradient>' +
      '</defs>' +
      art.join('') +
      '<path fill="url(#pw-snow)" d="' + snow + '"/><path class="se" d="' + snowEdge + '"/>' +
      '</svg>';

    // Снег и сосульки обходятся в разные стороны — отдельными контурами,
    // иначе на стыке корня и карниза в маске получилась бы дыра.
    var maskSvg = '<svg xmlns="' + SVG_NS + '" width="' + width + '" height="' + height + '"><path d="' + silhouettes.join('') + '"/><path d="' + snow + '"/></svg>';
    var mask = 'data:image/svg+xml,' + maskSvg.replace(/"/g, "'").replace(/</g, '%3C').replace(/>/g, '%3E').replace(/#/g, '%23');

    var tips = items
      .filter(function (ice) { return ice.len > 12 * scale; })
      .map(function (ice) { return { x: ice.tip[0], y: ice.tip[1] }; });
    return { svg: svg, mask: mask, height: height, tips: tips };
  }

  // Капель: время от времени на кончике случайной длинной сосульки набухает
  // капля, отрывается и падает.
  function drip(layer, getTips) {
    function later() {
      setTimeout(tick, 900 + Math.random() * 2600);
    }
    function tick() {
      var tips = getTips();
      if (document.hidden || !tips.length || !layer.animate) return later();
      var tip = tips[Math.floor(Math.random() * tips.length)];
      var drop = document.createElement('span');
      drop.className = 'pw-drop';
      drop.style.left = n1(tip.x) + 'px';
      drop.style.top = n1(tip.y) + 'px';
      layer.appendChild(drop);
      var grow = 1100 + Math.random() * 1400;
      var fallTime = 420;
      var fall = 70 + Math.random() * 90;
      var o = grow / (grow + fallTime);
      drop.animate(
        [
          { transform: 'scale(0.15)', opacity: 0.6 },
          { transform: 'scale(1)', opacity: 1, offset: o * 0.9 },
          { transform: 'translateY(1px) scale(0.9, 1.25)', opacity: 1, offset: o, easing: 'cubic-bezier(.5,0,1,.6)' },
          { transform: 'translateY(' + fall + 'px) scale(0.75, 1.5)', opacity: 0 }
        ],
        { duration: grow + fallTime, fill: 'forwards' }
      ).onfinish = function () {
        drop.remove();
      };
      later();
    }
    later();
  }

  /* --- Логотип во льду ---------------------------------------------------- */

  // Трещины в координатах 100×100 от точки удара чуть выше центра.
  // Первый удар — короткие лучи, второй — ветвление к краям.
  var CRACKS = [
    ['M50 48 L42 37 L34 31', 'M50 48 L59 57 L63 70', 'M50 48 L61 43'],
    [
      'M34 31 L26 21 L19 17', 'M42 37 L38 20 L36 8', 'M63 70 L69 86 L71 96',
      'M59 57 L76 63 L92 61', 'M61 43 L79 31 L88 13', 'M50 48 L39 60 L24 66 L8 71',
      'M39 60 L36 79 L33 92'
    ]
  ];

  // Детали пазла логотипа (src/assets/logo.png) — многоугольники в долях
  // картинки. Швы проходят по белым зазорам между деталями, поэтому разрез
  // не виден; «выступы» — язычки, заходящие в соседнюю деталь.
  var PIECES = [
    { dx: -1, dy: -1, poly: '0 0, 48% 0, 48% 46%, 0 46%' },
    { dx: 1, dy: -1, poly: '48% 0, 100% 0, 100% 60%, 71% 60%, 71% 71%, 62% 71%, 62% 60%, 48% 60%' },
    { dx: -1, dy: 1, poly: '0 46%, 48% 46%, 48% 72%, 37% 72%, 37% 88%, 48% 88%, 48% 100%, 0 100%' },
    { dx: 1, dy: 1, poly: '48% 60%, 62% 60%, 62% 71%, 71% 71%, 71% 60%, 100% 60%, 100% 100%, 48% 100%, 48% 88%, 37% 88%, 37% 72%, 48% 72%' }
  ];

  function freeze(img) {
    var link = img.closest('a');
    if (!link) return;

    var wrap = document.createElement('span');
    wrap.className = 'pw-ice-wrap';
    img.parentNode.insertBefore(wrap, img);
    wrap.appendChild(img);

    var ice = document.createElement('span');
    ice.className = 'pw-ice';
    ice.setAttribute('data-stage', '0');
    ice.setAttribute('aria-hidden', 'true');
    var svg = document.createElementNS(SVG_NS, 'svg');
    svg.setAttribute('viewBox', '0 0 100 100');
    svg.setAttribute('preserveAspectRatio', 'none');
    CRACKS.forEach(function (lines, n) {
      var g = document.createElementNS(SVG_NS, 'g');
      g.setAttribute('class', 'c' + (n + 1));
      ['hl', 'ln'].forEach(function (cls) {
        lines.forEach(function (d) {
          var p = document.createElementNS(SVG_NS, 'path');
          p.setAttribute('d', d);
          p.setAttribute('pathLength', '1');
          p.setAttribute('class', cls);
          g.appendChild(p);
        });
      });
      svg.appendChild(g);
    });
    ice.appendChild(svg);
    wrap.appendChild(ice);

    var hadTitle = link.hasAttribute('title');
    if (!hadTitle) link.setAttribute('title', 'Логотип вмёрз в лёд — постучите по нему');

    var stage = 0;
    function onClick(e) {
      // Клавиатура (detail === 0) и открытие в новой вкладке — как обычно.
      if (e.detail === 0 || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      stage += 1;
      if (stage < 3) {
        ice.setAttribute('data-stage', String(stage));
        knock(wrap, stage);
        return;
      }
      link.removeEventListener('click', onClick, true);
      if (!hadTitle) link.removeAttribute('title');
      sset(KEY_BROKEN, '1');
      shatter(wrap, ice, img, e);
    }
    link.addEventListener('click', onClick, true);
  }

  function knock(wrap, stage) {
    if (calm || !wrap.animate) return;
    var a = stage === 1 ? 5 : 8;
    wrap.animate(
      [
        { transform: 'none' },
        { transform: 'rotate(' + -a + 'deg) scale(0.95)' },
        { transform: 'rotate(' + a * 0.6 + 'deg)' },
        { transform: 'none' }
      ],
      { duration: 260, easing: 'ease-out' }
    );
  }

  function shatter(wrap, ice, img, e) {
    if (calm || !ice.animate) {
      ice.style.opacity = '0';
      setTimeout(function () { ice.remove(); }, 450);
      return;
    }
    var box = ice.getBoundingClientRect();
    var ox = clamp(((e.clientX - box.left) / box.width) * 100, 15, 85);
    var oy = clamp(((e.clientY - box.top) / box.height) * 100, 15, 85);
    shards(box, ox, oy);
    ice.remove();
    shake(wrap, img);
  }

  function clamp(v, lo, hi) {
    return Math.max(lo, Math.min(hi, v));
  }

  // Корка раскалывается веером треугольников от точки удара: лучи до краёв
  // плюс углы, отсортированные по углу, — соседние точки дают осколок.
  function shards(box, ox, oy) {
    var layer = document.createElement('div');
    layer.className = 'pw-shards';
    layer.style.left = box.left + 'px';
    layer.style.top = box.top + 'px';
    layer.style.width = box.width + 'px';
    layer.style.height = box.height + 'px';
    document.body.appendChild(layer);

    var pts = [[0, 0], [100, 0], [100, 100], [0, 100]];
    var rays = 9;
    for (var i = 0; i < rays; i++) {
      var ang = ((i + Math.random() * 0.7) / rays) * Math.PI * 2;
      pts.push(toEdge(ox, oy, Math.cos(ang), Math.sin(ang)));
    }
    pts.sort(function (a, b) {
      return Math.atan2(a[1] - oy, a[0] - ox) - Math.atan2(b[1] - oy, b[0] - ox);
    });

    var left = pts.length;
    pts.forEach(function (p, k) {
      var q = pts[(k + 1) % pts.length];
      var cx = (ox + p[0] + q[0]) / 3;
      var cy = (oy + p[1] + q[1]) / 3;
      var len = Math.hypot(cx - ox, cy - oy) || 1;
      var push = 16 + Math.random() * 18;
      var dx = ((cx - ox) / len) * push;
      var dy = ((cy - oy) / len) * push;
      var fall = 22 + Math.random() * 26;
      var spin = (Math.random() - 0.5) * 220;

      var s = document.createElement('span');
      s.className = 'pw-shard';
      s.style.clipPath = 'polygon(' + ox + '% ' + oy + '%, ' + p[0] + '% ' + p[1] + '%, ' + q[0] + '% ' + q[1] + '%)';
      s.style.transformOrigin = cx + '% ' + cy + '%';
      layer.appendChild(s);
      s.animate(
        [
          { transform: 'none', opacity: 1 },
          { transform: 'translate(' + dx * 0.6 + 'px,' + (dy * 0.6 - 6) + 'px) rotate(' + spin * 0.4 + 'deg)', opacity: 1, offset: 0.3 },
          { transform: 'translate(' + dx + 'px,' + (dy + fall) + 'px) rotate(' + spin + 'deg)', opacity: 0 }
        ],
        { duration: 750 + Math.random() * 350, easing: 'cubic-bezier(.2,.55,.45,1)', fill: 'forwards' }
      ).onfinish = function () {
        left -= 1;
        if (!left) layer.remove();
      };
    });
  }

  function toEdge(ox, oy, dx, dy) {
    var t = Infinity;
    if (dx > 0) t = Math.min(t, (100 - ox) / dx);
    if (dx < 0) t = Math.min(t, -ox / dx);
    if (dy > 0) t = Math.min(t, (100 - oy) / dy);
    if (dy < 0) t = Math.min(t, -oy / dy);
    return [ox + dx * t, oy + dy * t];
  }

  // Освободившийся пазл встряхивается: детали расходятся на пару пикселей
  // и защёлкиваются обратно.
  function shake(wrap, img) {
    var clones = PIECES.map(function (piece) {
      var c = img.cloneNode(false);
      c.removeAttribute('id');
      c.setAttribute('alt', '');
      c.setAttribute('aria-hidden', 'true');
      c.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;max-width:none;margin:0;clip-path:polygon(' + piece.poly + ')';
      wrap.appendChild(c);
      return { el: c, piece: piece };
    });
    img.style.visibility = 'hidden';
    var left = clones.length;
    clones.forEach(function (item) {
      var d = 3;
      var x = item.piece.dx * d;
      var y = item.piece.dy * d;
      var r = item.piece.dx * item.piece.dy * 5;
      item.el.animate(
        [
          { transform: 'none' },
          { transform: 'translate(' + x + 'px,' + y + 'px) rotate(' + r + 'deg)', offset: 0.35 },
          { transform: 'translate(' + -x * 0.25 + 'px,' + -y * 0.25 + 'px)', offset: 0.75 },
          { transform: 'none' }
        ],
        { duration: 620, delay: 40, easing: 'ease-in-out' }
      ).onfinish = function () {
        item.el.remove();
        left -= 1;
        if (!left) img.style.visibility = '';
      };
    });
  }

  /* --- Сугроб внизу окна -------------------------------------------------- */

  // Из-под сосулек идёт редкий снег и копится внизу окна: каждая снежинка
  // оставляет бугорок, а сам сугроб медленно подрастает волнами — будто
  // намело ветром. Крутые склоны осыпаются. Высота хранится до закрытия
  // вкладки, так что при переходах по страницам сугроб продолжает расти.

  function drift(header) {
    var canvas = document.createElement('canvas');
    canvas.className = 'pw-drift';
    canvas.setAttribute('aria-hidden', 'true');
    document.body.appendChild(canvas);
    var ctx = canvas.getContext('2d');
    if (!ctx) return;

    var STEP = 4; // ширина столбца высот, px
    var w = 0, h = 0, cap = 36, heights = [], flakes = [], glints = [], colors = {};
    var raf = 0, last = 0, lastDraw = 0, lastSave = 0;

    // Где намело больше, где меньше: медленные несоизмеримые волны.
    function dunes(x) {
      var m = 0.6 + 0.25 * Math.sin(x / 173 + 1.3) + 0.2 * Math.sin(x / 61 + 4.1) + 0.12 * Math.sin(x / 23 + 0.7);
      return Math.max(0.15, m);
    }

    function readColors() {
      var css = getComputedStyle(document.documentElement);
      var dark = document.documentElement.getAttribute('data-theme') === 'dark';
      colors = {
        top: css.getPropertyValue('--pw-snow-1').trim() || '#fff',
        bottom: css.getPropertyValue('--pw-snow-2').trim() || '#e2eef8',
        edge: css.getPropertyValue('--pw-snow-edge').trim() || 'rgba(111,165,201,.75)',
        flake: dark ? '220,235,245' : '127,185,220',
        glint: dark ? '255,255,255' : '96,150,192'
      };
    }

    function restore(count) {
      var saved = null;
      try { saved = JSON.parse(sget(KEY_DRIFT) || 'null'); } catch (e) { saved = null; }
      var out = [];
      for (var i = 0; i < count; i++) {
        if (saved && saved.length > 1) {
          out.push(Math.min(cap, saved[Math.round((i * (saved.length - 1)) / (count - 1))]));
        } else {
          out.push(1.5 + cap * 0.12 * dunes(i * STEP)); // тонкий слой для начала
        }
      }
      return out;
    }

    function save() {
      sset(KEY_DRIFT, JSON.stringify(heights.map(function (v) { return Math.round(v * 10) / 10; })));
    }

    function flake(anywhere) {
      var top = header ? header.getBoundingClientRect().bottom : 0;
      var r = 0.9 + Math.random() * 1.6;
      return {
        x: Math.random() * w,
        y: anywhere ? top + Math.random() * (h - top) : top - r,
        r: r,
        v: 16 + r * 8 + Math.random() * 10,
        phase: Math.random() * Math.PI * 2,
        sway: 0.4 + Math.random() * 0.7,
        a: 0.35 + Math.random() * 0.35
      };
    }

    function resize() {
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = window.innerWidth;
      h = window.innerHeight;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      cap = w < 700 ? 22 : 36;
      if (heights.length) {
        sset(KEY_DRIFT, JSON.stringify(heights));
      }
      heights = restore(Math.ceil(w / STEP) + 1);
      glints = [];
      for (var gx = 10; gx < w; gx += 30 + Math.random() * 50) {
        glints.push({ i: Math.round(gx / STEP), dy: 2 + Math.random() * 6, phase: Math.random() * 6.28, speed: 1 + Math.random() * 2 });
      }
      var n = calm ? 0 : Math.round(w / 80);
      while (flakes.length < n) flakes.push(flake(true));
      flakes.length = n;
      draw(0);
    }

    function heightAt(x) {
      var i = Math.max(0, Math.min(heights.length - 1, Math.round(x / STEP)));
      return heights[i];
    }

    function deposit(x, amount) {
      var c = Math.round(x / STEP);
      for (var k = -3; k <= 3; k++) {
        var i = c + k;
        if (i < 0 || i >= heights.length) continue;
        heights[i] += amount * (1 - Math.abs(k) / 4) * (1 - heights[i] / cap);
      }
    }

    // Осыпание: склон круче предела сползает вниз, сугроб остаётся пологим.
    function settle() {
      var limit = 1.8;
      for (var i = 0; i < heights.length - 1; i++) {
        var d = heights[i] - heights[i + 1];
        if (d > limit) { heights[i] -= (d - limit) / 2; heights[i + 1] += (d - limit) / 2; }
        else if (d < -limit) { heights[i] += (-d - limit) / 2; heights[i + 1] -= (-d - limit) / 2; }
      }
    }

    function draw(t) {
      ctx.clearRect(0, 0, w, h);
      for (var f = 0; f < flakes.length; f++) {
        var fl = flakes[f];
        ctx.beginPath();
        ctx.fillStyle = 'rgba(' + colors.flake + ',' + fl.a + ')';
        ctx.arc(fl.x + Math.sin(fl.phase) * 7, fl.y, fl.r, 0, Math.PI * 2);
        ctx.fill();
      }
      // Поверхность — сглаженная кривая по серединам столбцов.
      ctx.beginPath();
      ctx.moveTo(0, h);
      ctx.lineTo(0, h - heights[0]);
      for (var i = 1; i < heights.length - 1; i++) {
        var x0 = i * STEP, y0 = h - heights[i];
        var xm = (i + 0.5) * STEP, ym = h - (heights[i] + heights[i + 1]) / 2;
        ctx.quadraticCurveTo(x0, y0, xm, ym);
      }
      ctx.lineTo(w, h - heights[heights.length - 1]);
      ctx.lineTo(w, h);
      ctx.closePath();
      var grad = ctx.createLinearGradient(0, h - cap, 0, h);
      grad.addColorStop(0, colors.top);
      grad.addColorStop(1, colors.bottom);
      ctx.fillStyle = grad;
      ctx.fill();
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(0, h - heights[0]);
      for (var j = 1; j < heights.length - 1; j++) {
        ctx.quadraticCurveTo(j * STEP, h - heights[j], (j + 0.5) * STEP, h - (heights[j] + heights[j + 1]) / 2);
      }
      ctx.strokeStyle = colors.edge;
      ctx.lineWidth = 1;
      ctx.stroke();
      ctx.restore();
      // Искорки на снегу.
      for (var g = 0; g < glints.length; g++) {
        var gl = glints[g];
        var hi = heights[Math.min(gl.i, heights.length - 1)];
        if (hi < gl.dy + 2) continue;
        var a = calm ? 0.5 : Math.max(0, Math.sin(t / 1000 * gl.speed + gl.phase));
        if (a < 0.05) continue;
        ctx.fillStyle = 'rgba(' + colors.glint + ',' + (a * 0.8).toFixed(2) + ')';
        ctx.fillRect(gl.i * STEP, h - hi + gl.dy, 1.2, 1.2);
      }
    }

    function frame(t) {
      raf = requestAnimationFrame(frame);
      if (t - lastDraw < 33) return; // ~30 кадров в секунду хватает
      var dt = last ? Math.min((t - last) / 1000, 0.1) : 0;
      last = lastDraw = t;
      var top = header ? header.getBoundingClientRect().bottom : 0;
      // Подрастает сам: до половины предела примерно за две минуты.
      var rate = (cap * 0.5) / 120;
      for (var i = 0; i < heights.length; i++) {
        heights[i] += rate * dt * dunes(i * STEP) * (1 - heights[i] / cap);
      }
      for (var f = 0; f < flakes.length; f++) {
        var fl = flakes[f];
        fl.y += fl.v * dt;
        fl.phase += fl.sway * dt;
        var fx = fl.x + Math.sin(fl.phase) * 7;
        if (fl.y + fl.r >= h - heightAt(fx)) {
          deposit(fx, 0.5 + fl.r * 0.45);
          flakes[f] = flake(false);
          flakes[f].y = top;
        }
      }
      settle();
      draw(t);
      if (t - lastSave > 4000) {
        lastSave = t;
        save();
      }
    }

    readColors();
    resize();
    window.addEventListener('resize', resize);
    window.addEventListener('pagehide', save);
    // Тема в документации переключается без перезагрузки.
    if (window.MutationObserver) {
      new MutationObserver(function () { readColors(); draw(last); })
        .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    }
    if (!calm) raf = requestAnimationFrame(frame);
  }

  /* --- Снег на первом экране лендинга ------------------------------------- */

  function snowfall(hero) {
    var canvas = document.createElement('canvas');
    canvas.className = 'pw-snow';
    canvas.setAttribute('aria-hidden', 'true');
    hero.insertBefore(canvas, hero.firstChild);
    var ctx = canvas.getContext('2d');
    if (!ctx) return;

    var w = 0, h = 0, flakes = [], raf = 0, last = 0, visible = true;

    function flake(anywhere) {
      var r = 1 + Math.random() * 2.3;
      return {
        x: Math.random() * w,
        y: anywhere ? Math.random() * h : -r * 2,
        r: r,
        v: 14 + r * 9 + Math.random() * 8, // пикселей в секунду: крупные падают быстрее
        phase: Math.random() * Math.PI * 2,
        sway: 0.4 + Math.random() * 0.8,
        a: 0.35 + Math.random() * 0.4
      };
    }

    function resize() {
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = hero.clientWidth;
      h = hero.clientHeight;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var n = Math.round(Math.min(90, w / 16));
      while (flakes.length < n) flakes.push(flake(true));
      flakes.length = n;
    }

    function frame(t) {
      raf = 0;
      var dt = last ? Math.min((t - last) / 1000, 0.05) : 0;
      last = t;
      ctx.clearRect(0, 0, w, h);
      for (var i = 0; i < flakes.length; i++) {
        var f = flakes[i];
        f.y += f.v * dt;
        f.phase += f.sway * dt;
        if (f.y - f.r > h) {
          flakes[i] = f = flake(false);
        }
        ctx.beginPath();
        ctx.fillStyle = 'rgba(127,185,220,' + f.a + ')';
        ctx.arc(f.x + Math.sin(f.phase) * 8, f.y, f.r, 0, Math.PI * 2);
        ctx.fill();
      }
      if (visible) raf = requestAnimationFrame(frame);
    }

    function start() {
      if (!raf) {
        last = 0;
        raf = requestAnimationFrame(frame);
      }
    }

    resize();
    if (window.ResizeObserver) new ResizeObserver(resize).observe(hero);
    // Ушёл с первого экрана — снег не считаем.
    if (window.IntersectionObserver) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        if (visible) start();
      }).observe(hero);
    }
    start();
  }
})();
