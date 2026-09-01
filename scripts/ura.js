/* Ura 裏 — the panel, and the two live bits inside it.
 *
 * Three jobs, all of them progressive enhancement:
 *
 *   1. Turn the home's link to /ura/ into a sliding panel. Without this the
 *      link is an ordinary navigation to a real page, which is why the door is
 *      an <a> and not a button.
 *   2. Mark today in the week grid. The grid is rendered at build time from
 *      _data/schedule.yml; only the highlight is live.
 *   3. Drop calendar entries that have gone past since the last build, and show
 *      the first five that are still ahead. GitHub Pages only builds on push,
 *      so a date-filtered list has to be filtered in the browser or it lies.
 *
 * The words expander lives here too because it is the same page.
 */
(function () {
  'use strict';

  var DAYS = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
  // No cap. "What is coming" shows every future entry: the five-at-a-time
  // reveal made sense when the list was thirty-five copies of one grading
  // class, and hides a seminar now that seminars are in it.

  function todayISO() {
    var d = new Date();
    function p(n) { return (n < 10 ? '0' : '') + n; }
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
  }

  // --- 2 · the seven days that start today ---------------------------------
  // The build emits twenty-one dated cells; this picks the seven beginning
  // today. If today is not among them the build is more than three weeks old,
  // so it falls back to the first seven and hides the day numbers rather than
  // showing dates that have gone by.
  function week(root) {
    var box = root.querySelector('[data-ura-week]');
    if (!box) return;
    var cells = [].slice.call(box.querySelectorAll('.ur-day'));
    if (!cells.length) return;

    var now = todayISO(), start = -1;
    for (var i = 0; i < cells.length; i++) {
      if (cells[i].dataset.date === now) { start = i; break; }
    }
    var stale = start < 0;
    if (stale) start = 0;

    var key = DAYS[new Date().getDay()];
    for (var j = 0; j < cells.length; j++) {
      var show = j >= start && j < start + 7;
      cells[j].hidden = !show;
      cells[j].toggleAttribute('data-nodates', stale);
      cells[j].toggleAttribute('data-today',
        stale ? cells[j].dataset.day === key : j === start);
    }

    range(root, stale ? null : cells[start], stale ? null : cells[start + 6]);
  }

  // The heading says which seven days these are, so it has to move with them.
  // The templates and the month names come down on the element itself rather
  // than living in here: four languages of date phrasing belong in the data.
  function range(root, first, last) {
    var el = root.querySelector('[data-ura-range]');
    if (!el) return;
    if (!first || !last) { el.hidden = true; return; }

    var a = first.dataset.date.split('-'), b = last.dataset.date.split('-');
    var months = (el.dataset.months || '').split('|');
    var m1 = months[+a[1] - 1], m2 = months[+b[1] - 1];
    if (!m1 || !m2) return;

    el.hidden = false;
    el.textContent = (a[1] === b[1] ? el.dataset.same : el.dataset.cross)
      .replace('DD1', String(+a[2])).replace('DD2', String(+b[2]))
      .replace('MON1', m1).replace('MON2', m2);
  }

  // --- 3 · what is still coming -------------------------------------------
  function filterAhead(root) {
    var box = root.querySelector('[data-ura-ahead]');
    if (!box) return;
    var now = todayISO(), shown = 0;
    var rows = box.querySelectorAll('.ur-nx');
    for (var i = 0; i < rows.length; i++) {
      var keep = rows[i].dataset.date >= now;
      rows[i].hidden = !keep;
      if (keep) shown++;
    }
    box.toggleAttribute('data-empty', shown === 0);
  }

  // --- the words expander --------------------------------------------------
  function words(root) {
    var btn = root.querySelector('.ur-morebtn');
    var box = root.querySelector('#ura-more');
    if (!btn || !box) return;
    btn.addEventListener('click', function () {
      var open = box.hasAttribute('data-open');
      box.toggleAttribute('data-open', !open);
      btn.setAttribute('aria-expanded', String(!open));
      btn.textContent = open ? btn.dataset.more : btn.dataset.less;
    });
  }

  // --- 4 · the archive: filter in place, and open one at a time ------------
  // Filtering is a matter of hiding tiles — no request, no navigation. The
  // links underneath still point at the gallery filtered by that year, which
  // is what happens with JavaScript off.
  function archive(root) {
    var years = root.querySelector('[data-ura-years]');
    var sheet = root.querySelector('[data-ura-sheet]');
    if (!years || !sheet) return;
    var none = root.querySelector('[data-ura-sheet-none]');

    // The archive is 462 entries and the page carries only the newest 64 as
    // markup; the rest arrive as JSON and become tiles when their year is
    // opened. Putting all 462 in the HTML cost 1,194 extra elements and 2.4 s
    // of render delay on a throttled phone, in front of an LCP that is a
    // paragraph of text.
    var rest = [];
    var payload = root.querySelector('[data-ura-arch]');
    if (payload) {
      try { rest = JSON.parse(payload.textContent); } catch (err) { rest = []; }
    }

    // One record per entry, in date order, whether or not it has an element
    // yet. Everything downstream — the year strip, the modal, the arrows —
    // walks this list, so none of them needs to know which half it is in.
    var items = [].slice.call(sheet.querySelectorAll('a')).map(function (a) {
      return { el: a, url: a.href, full: a.dataset.full, name: a.dataset.name || '',
               date: a.dataset.date || '', year: a.dataset.year };
    }).concat(rest.map(function (r) {
      return { el: null, url: r[0], full: '/images/' + r[1] + '.webp', thumb: r[1],
               name: r[2], date: r[3], year: String(r[3]).slice(0, 4) };
    }));
    var nRecent = items.length - rest.length;
    items.forEach(function (it, i) { if (it.el) it.el._i = i; });

    // Built once and kept. Appending a year's tiles together keeps that year
    // in date order, which is all that shows: one year is visible at a time.
    function build(it, i) {
      if (it.el) return it.el;
      var a = document.createElement('a');
      a.href = it.url;
      a.rel = 'noopener';
      a.hidden = true;
      a._i = i;
      a.dataset.year = it.year;
      a.dataset.full = it.full;
      a.dataset.name = it.name;
      a.dataset.date = it.date;
      var img = document.createElement('img');
      img.src = '/images/' + it.thumb + '-t.webp';
      img.alt = '';
      img.loading = 'lazy';
      img.width = 160;
      img.height = 160;
      var sr = document.createElement('span');
      sr.className = 'sr-only';
      sr.textContent = it.name;
      a.appendChild(img);
      a.appendChild(sr);
      sheet.appendChild(a);
      it.el = a;
      return a;
    }

    // One place that applies a year, because two things ask for it now: the
    // strip, and the modal's arrows walking off the end of a year.
    function selectYear(y) {
      var shown = 0;
      [].forEach.call(years.querySelectorAll('a'), function (o) {
        o.toggleAttribute('data-on', o.dataset.year === y);
      });
      if (y !== 'recent') {
        items.forEach(function (it, i) { if (it.year === y) build(it, i); });
      }
      items.forEach(function (it, i) {
        // "recent" is the sixty-four newest by date, which is what the section
        // is for; every other chip is a whole year.
        var ok = y === 'recent' ? i < nRecent : it.year === y;
        if (!it.el) return;
        it.el.hidden = !ok;
        if (ok) shown++;
      });
      if (none) none.hidden = shown > 0;
    }

    years.addEventListener('click', function (e) {
      var a = e.target.closest('a[data-year]');
      if (!a) return;
      e.preventDefault();
      selectYear(a.dataset.year);
    });

    var dlg = root.querySelector('[data-ura-modal]');
    if (!dlg || !dlg.showModal) return;
    var img = dlg.querySelector('[data-ura-modal-img]');
    var nameEl = dlg.querySelector('[data-ura-modal-name]');
    var dateEl = dlg.querySelector('[data-ura-modal-date]');
    var cta = dlg.querySelector('[data-ura-modal-cta]');
    var tpl = cta.dataset.tpl || '';

    // "Facebook" or "Instagram" from the URL, so the button names the place it
    // is actually going rather than saying "see more" and hoping.
    function where(href) {
      var h = '';
      try { h = new URL(href, location.href).hostname.replace(/^www\./, ''); }
      catch (err) { return ''; }
      var base = h.split('.')[0];
      return base.charAt(0).toUpperCase() + base.slice(1);
    }

    var prevBtn = dlg.querySelector('[data-ura-modal-prev]');
    var nextBtn = dlg.querySelector('[data-ura-modal-next]');
    var current = null;

    function show(it) {
      if (!it || !it.full) return;
      current = it;
      img.src = it.full;
      img.alt = it.name;
      nameEl.textContent = it.name;
      dateEl.textContent = it.date;
      cta.href = it.url;
      cta.textContent = tpl.replace('NAME', where(it.url));
      if (!dlg.open) dlg.showModal();
    }

    // Steps through ALL 462 in date order, not just what is on screen. It used
    // to walk the visible set, which made the arrows stop at the edge of
    // whatever year was open — a corridor per year rather than one archive.
    //
    // Crossing into another year moves the filter with you: the year is
    // revealed and its chip lights up, so closing the modal leaves you looking
    // at the year you walked into rather than the one you started from.
    function step(d) {
      if (!items.length) return;
      var i = items.indexOf(current);
      var next = items[(i + d + items.length) % items.length];
      if (!next.el || next.el.hidden) selectYear(next.year);
      show(next);
    }

    sheet.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (!a || a._i === undefined) return;
      e.preventDefault();
      show(items[a._i]);
    });

    prevBtn.addEventListener('click', function () { step(-1); });
    nextBtn.addEventListener('click', function () { step(1); });

    dlg.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); step(1); }
    });

    dlg.addEventListener('click', function (e) {
      // The backdrop is the dialog itself outside its own box.
      if (e.target === dlg || e.target.closest('[data-ura-modal-close]')) dlg.close();
    });
    // The src is deliberately NOT cleared on close. It was, to avoid holding a
    // decoded image, and the saving is not worth what it costs: any stray
    // close — and a <dialog> has several ways to close itself — emptied the
    // <img> while the modal was still on screen, which showed the alt text
    // where the picture should be.
  }

  function live(root) { week(root); filterAhead(root); words(root); archive(root); }

  // --- 1 · the panel -------------------------------------------------------
  // The panel ships empty and pulls /ura/ on first open. That page is the page
  // the door links to, so there is one Ura and the panel cannot drift from it;
  // and the home stops carrying a second copy of ~60 KB of markup that most
  // visitors never open.
  //
  // Everything here degrades: if the fetch fails, or the response has no body
  // to lift, the door goes back to being a link and navigates.
  function panel() {
    var el = document.getElementById('ura-panel');
    if (!el) return;
    var html = document.documentElement, scrim = document.querySelector('.ura-scrim');
    var slot = el.querySelector('[data-ura-slot]');
    var spin = el.querySelector('[data-ura-loading]');
    var src = el.dataset.uraSrc;
    var last = null, state = 'empty';

    // The panel's stylesheet is fetched as `rel=preload` and promoted to a
    // stylesheet on load, so it is off the critical path. If someone opens Ura
    // before it has landed, promote it now: the closed state is inline in the
    // head, so without the full sheet the panel would stay hidden and the
    // click would do nothing visible.
    function ensureStyles() {
      var link = document.querySelector('link[rel="preload"][as="style"][href*="ura.min.css"]');
      if (link) { link.onload = null; link.rel = 'stylesheet'; }
    }

    function reveal() {
      ensureStyles();
      html.classList.add('ura-on');
      el.removeAttribute('inert');
      el.setAttribute('aria-hidden', 'false');
      el.scrollTop = 0;
      var x = el.querySelector('.ur-x');
      if (x) setTimeout(function () { x.focus(); }, 60);
    }

    function load() {
      if (state !== 'empty') return Promise.resolve(state === 'ready');
      state = 'loading';
      if (spin) spin.hidden = false;
      return fetch(src, { credentials: 'same-origin' })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          return r.text();
        })
        .then(function (text) {
          // DOMParser and not innerHTML: the response is a whole document, and
          // parsing it inertly means none of its <script> or <img> runs or
          // loads until the fragment we want is in the page.
          var doc = new DOMParser().parseFromString(text, 'text/html');
          var body = doc.querySelector('[data-ura-body]');
          if (!body) throw new Error('no body');
          if (spin) spin.hidden = true;
          slot.innerHTML = body.innerHTML;
          rewriteForPanel(slot);
          live(el);
          state = 'ready';
          return true;
        })
        .catch(function () {
          state = 'empty';
          if (spin) spin.hidden = true;
          return false;
        });
    }

    // The fetched markup is the PAGE's, so its two "back to the home page"
    // controls are links. Inside the panel they have to close it instead.
    function rewriteForPanel(root) {
      // The masthead in the shell already says "Close"; this is the one at the
      // foot of the fetched page, which says "back to the home page" because
      // on that page it goes there. In the panel it closes, so it has to say
      // so — the label comes off the shell's own button rather than being a
      // second copy of the string.
      var shellLabel = el.querySelector('.ur-mast .ur-x span');
      [].forEach.call(root.querySelectorAll('a.ur-back'), function (a) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = a.className;
        b.textContent = shellLabel ? shellLabel.textContent : a.textContent;
        b.setAttribute('data-ura-close', '');
        a.parentNode.replaceChild(b, a);
      });
    }

    function open(e) {
      last = document.activeElement;
      var href = e && e.target.closest('[data-ura-open]');
      href = href && href.getAttribute('href');
      if (e) e.preventDefault();
      reveal();
      if (history.pushState) history.pushState({ ura: 1 }, '', '#ura');
      load().then(function (ok) {
        if (!ok && href) location.href = href;
      });
    }

    function close() {
      html.classList.remove('ura-on');
      el.setAttribute('aria-hidden', 'true');
      // Focus first, then inert: moving focus out of a subtree that is already
      // inert leaves it on <body> instead of on the control that opened Ura.
      if (last) last.focus();
      el.setAttribute('inert', '');
      if (history.pushState && location.hash === '#ura') {
        history.pushState({}, '', location.pathname);
      }
    }

    document.addEventListener('click', function (e) {
      if (e.target.closest('[data-ura-open]')) open(e);
      else if (e.target.closest('[data-ura-close]') || e.target === scrim) close();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape' || !html.classList.contains('ura-on')) return;
      // A <dialog> handles its own Escape and closes itself. Without this the
      // same keypress also reached here and shut the panel behind it, so one
      // press on an open photograph dismissed the whole of Ura.
      if (document.querySelector('dialog[open]')) return;
      close();
    });

    window.addEventListener('popstate', function () {
      if (location.hash === '#ura') {
        if (!html.classList.contains('ura-on')) { reveal(); load(); }
      } else if (html.classList.contains('ura-on')) {
        // Same three steps as close(), because Back is a way of closing it.
        html.classList.remove('ura-on');
        el.setAttribute('aria-hidden', 'true');
        el.setAttribute('inert', '');
      }
    });

    // Landing on /#ura opens it straight away — that is the shareable URL for
    // "the home, with Ura already out".
    if (location.hash === '#ura') { reveal(); load(); }
  }

  function init() {
    // On /ura/ the content is already in the document. In the panel it is not
    // yet, so live() runs there only once the fetch has landed.
    var pan = document.getElementById('ura-panel');
    if (!pan) {
      var root = document.querySelector('.ur');
      if (root) live(root);
    }
    panel();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());
