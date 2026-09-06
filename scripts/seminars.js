/* Seminars listing — filtering, progressive enhancement only.
 *
 * Every seminar is in the HTML, rendered at build time. This file hides the
 * ones that do not match the current filter and keeps that filter in the URL so
 * a filtered view can be linked to. With JavaScript off nothing is hidden and
 * every seminar is visible — which is also what a crawler sees. The `when`
 * radio starts on "upcoming", but that attribute hides nothing on its own: the
 * no-script page is still the whole list.
 *
 * "UPCOMING" IS THE DEFAULT because the first question the page is opened with
 * is "what is on next", not "what has this dojo ever hosted". Two things follow
 * from moving the default off "all", and both are in here: the URL now omits
 * `when` for `upcoming` and spells out `all` (an unfiltered URL is the one that
 * gets shared, and it has to survive being pasted back), and the default falls
 * back to "all" when nothing is upcoming, so a quiet month opens on the archive
 * rather than on an empty page.
 *
 * The nav this replaces linked to #show-all, #upcoming and #ended: three
 * anchors that existed nowhere in the document, with no script behind them.
 */
(function () {
  'use strict';

  var root = document.getElementById('seminar-controls');
  var list = document.querySelector('.seminars');
  if (!root || !list) return;

  var cards = Array.prototype.slice.call(list.querySelectorAll('.seminar'));
  var catInputs = Array.prototype.slice.call(root.querySelectorAll('.seminar-chip input[type="checkbox"]'));
  var whenInputs = Array.prototype.slice.call(root.querySelectorAll('input[name="when"]'));
  var count = root.querySelector('.seminar-count');
  var empty = list.querySelector('.seminar-empty');
  var asked = false;              // did the URL name a `when`?

  function activeCategories() {
    return catInputs.filter(function (i) { return i.checked; })
                    .map(function (i) { return i.value; });
  }

  function activeWhen() {
    var on = whenInputs.filter(function (i) { return i.checked; })[0];
    return on ? on.value : 'all';
  }

  /* ORDER DEPENDS ON THE FILTER, and only on this one.
   *
   * The page is authored newest first, which is the right reading order for a
   * record: "All" and "Past" are a history, and a history reads backwards from
   * now. "Upcoming" is not a history — it is a queue, and the useful end of a
   * queue is the front. Rendered in page order it put the seminar fifteen
   * months out above the one this Saturday.
   *
   * Both orders are computed once from the DOM. Reordering is `insertBefore`
   * against the empty-state paragraph so that paragraph stays last, where the
   * markup puts it.
   */
  var docOrder = cards.slice();
  var dateAsc = cards.slice().sort(function (a, b) {
    var x = a.dataset.date || '', y = b.dataset.date || '';
    return x < y ? -1 : x > y ? 1 : 0;
  });
  var orderNow = null;

  function reorder(when) {
    var wanted = when === 'upcoming' ? 'asc' : 'doc';
    if (wanted === orderNow) return;      // nothing to move
    orderNow = wanted;
    (wanted === 'asc' ? dateAsc : docOrder).forEach(function (card) {
      if (empty) list.insertBefore(card, empty);
      else list.appendChild(card);
    });
  }

  function apply() {
    var cats = activeCategories();
    var when = activeWhen();
    var shown = 0;

    reorder(when);

    cards.forEach(function (card) {
      var okCat = cats.indexOf(card.dataset.category) !== -1;
      var okWhen = when === 'all' || card.dataset.state === when;
      var show = okCat && okWhen;
      card.hidden = !show;
      if (show) shown++;
    });

    if (empty) empty.hidden = shown !== 0;

    // Announced rather than silent: with 40 seminars on the page, a filter that
    // removes most of them should say how many are left.
    if (count) {
      var all = cards.length;
      count.hidden = shown === all;
      count.textContent = shown + ' / ' + all;
    }

    syncUrl(cats, when);
  }

  // Both parameters are omitted when they carry no information — an unfiltered
  // page keeps a clean URL, which is also the one that gets shared and indexed.
  // The `when` default is "upcoming", so that is the value that carries no
  // information and "all" is the one that has to be written down.
  function syncUrl(cats, when) {
    try {
      var url = new URL(window.location.href);
      if (cats.length === catInputs.length) url.searchParams.delete('category');
      else url.searchParams.set('category', cats.join(','));
      if (when === 'upcoming') url.searchParams.delete('when');
      else url.searchParams.set('when', when);
      window.history.replaceState({}, '', url);
    } catch (err) { /* filtering still works */ }
  }

  function readUrl() {
    var params;
    try { params = new URL(window.location.href).searchParams; }
    catch (err) { return; }

    var cat = params.get('category');
    if (cat) {
      var wanted = cat.split(',');
      catInputs.forEach(function (i) { i.checked = wanted.indexOf(i.value) !== -1; });
      // A category list that matches nothing would render an empty page with no
      // way back except editing the URL, so it is ignored.
      if (!catInputs.some(function (i) { return i.checked; })) {
        catInputs.forEach(function (i) { i.checked = true; });
      }
    }

    // "all" is accepted now that it is no longer the default — without it a
    // shared ?when=all link would silently open on "upcoming".
    var when = params.get('when');
    if (when === 'all' || when === 'upcoming' || when === 'ended') {
      whenInputs.forEach(function (i) { i.checked = i.value === when; });
      asked = true;
    }
  }

  root.addEventListener('change', apply);

  readUrl();
  apply();

  /* THE EMPTY DEFAULT, WHICH IS THE ONE FAILURE THE NEW DEFAULT CAN CAUSE.
   *
   * Between seasons there is nothing upcoming, and a page whose default filter
   * matches nothing opens as a heading and an apology over a list the reader
   * cannot see. So if the reader did not ask for a filter and "upcoming" turned
   * out to be empty, fall back to "all". Only on load: once somebody picks
   * "Próximamente" themselves, an empty result is the honest answer to what
   * they asked.
   */
  if (!asked && activeWhen() === 'upcoming' &&
      !cards.some(function (c) { return !c.hidden; })) {
    whenInputs.forEach(function (i) { i.checked = i.value === 'all'; });
    apply();
  }
})();

/* Multi-poster cards.
 *
 * An event whose front matter carries `posters:` renders every one of them
 * stacked in the card. This crossfades between them, and turns a click into a
 * picker rather than a link to one JPEG.
 *
 * A SEPARATE IIFE on purpose: the filter above returns early when the controls
 * are missing, and the posters have nothing to do with the filter.
 *
 * Nothing here is load-bearing. With the script off, the stack is five images
 * in a box with the first one shown by CSS, and the card is a plain link to
 * that poster.
 */
(function () {
  'use strict';

  var stacks = Array.prototype.slice.call(document.querySelectorAll('.seminar-shots'));
  if (!stacks.length) return;

  var HOLD = 4500;
  var mq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
  var running = [];
  var modal = null, big = null, strip = null, closeBtn = null, lastFocus = null, shownIn = null;

  function reduced() { return !!(mq && mq.matches); }

  // ---- the crossfade ------------------------------------------------------
  stacks.forEach(function (stack) {
    var shots = Array.prototype.slice.call(stack.querySelectorAll('.seminar-shot'));
    if (shots.length < 2) return;
    var names = (stack.dataset.shots || '').split(',');
    var at = 0, timer = null;

    function show(n) {
      shots[at].classList.remove('is-on');
      at = (n + shots.length) % shots.length;
      shots[at].classList.add('is-on');
    }
    function start() { if (!timer && !reduced() && !document.hidden) timer = setInterval(function () { show(at + 1); }, HOLD); }
    function stop() { if (timer) { clearInterval(timer); timer = null; } }

    // WCAG 2.2.2 wants a way to stop content that moves by itself. There is no
    // button, by design, so it stops wherever the reader's attention lands:
    // the pointer over it, the keyboard in it, the tab hidden, or the system
    // asking for less motion.
    stack.addEventListener('mouseenter', stop);
    stack.addEventListener('mouseleave', start);
    stack.addEventListener('focusin', stop);
    stack.addEventListener('focusout', start);

    stack.addEventListener('click', function (e) {
      e.preventDefault();
      openPicker(stack, names, at);
    });

    running.push({ start: start, stop: stop });
    start();
  });

  document.addEventListener('visibilitychange', function () {
    running.forEach(function (r) { if (document.hidden) r.stop(); else r.start(); });
  });
  if (mq && mq.addEventListener) {
    mq.addEventListener('change', function () {
      running.forEach(function (r) { r.stop(); if (!reduced()) r.start(); });
    });
  }

  // ---- the picker ---------------------------------------------------------
  // Built once, on the first click, and reused. GLightbox would have done the
  // gallery but not the thumbnail strip, and loading 42 KB to then fight its
  // arrows was the worse trade.
  function build() {
    modal = document.createElement('div');
    modal.className = 'sh-modal';
    modal.hidden = true;
    modal.innerHTML =
      '<div class="sh-scrim" data-sh-close></div>' +
      '<div class="sh-box" role="dialog" aria-modal="true">' +
        '<button class="sh-x" type="button" data-sh-close>' +
          '<svg aria-hidden="true" focusable="false" viewBox="0 0 16 16">' +
          '<path fill="none" stroke="currentColor" stroke-width="1.6" d="M3 3l10 10M13 3L3 13"/></svg>' +
        '</button>' +
        '<img class="sh-big" alt="">' +
        '<div class="sh-thumbs"></div>' +
      '</div>';
    document.body.appendChild(modal);
    big = modal.querySelector('.sh-big');
    strip = modal.querySelector('.sh-thumbs');
    closeBtn = modal.querySelector('.sh-x');

    modal.addEventListener('click', function (e) {
      if (e.target.closest('[data-sh-close]')) close();
    });
    document.addEventListener('keydown', function (e) {
      if (modal.hidden) return;
      if (e.key === 'Escape') { close(); return; }
      if (e.key !== 'Tab') return;
      // A dialog over the page has to keep the keyboard inside it.
      var f = Array.prototype.slice.call(modal.querySelectorAll('button'));
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
  }

  function pick(names, n, title) {
    big.src = '/images/' + names[n] + '.jpg';
    big.alt = title;
    Array.prototype.slice.call(strip.querySelectorAll('button')).forEach(function (b, i) {
      b.setAttribute('aria-pressed', String(i === n));
    });
  }

  function openPicker(stack, names, at) {
    if (!modal) build();
    var title = stack.dataset.shotsTitle || '';
    var word = stack.dataset.shotsPick || 'Poster';

    closeBtn.setAttribute('aria-label', stack.dataset.shotsClose || 'Close');
    modal.querySelector('.sh-box').setAttribute('aria-label', title);

    strip.innerHTML = '';
    names.forEach(function (name, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'sh-thumb';
      b.setAttribute('aria-label', word + ' ' + (i + 1));
      b.innerHTML = '<img src="/images/' + name + '.jpg" alt="" width="640" height="905">';
      b.addEventListener('click', function () { pick(names, i, title); });
      strip.appendChild(b);
    });

    pick(names, at, title);

    // The stack itself is the fallback: a click does not always leave focus on
    // the link, and returning it to <body> would drop the reader at the top of
    // a page of forty cards.
    var was = document.activeElement;
    lastFocus = (was && was !== document.body) ? was : stack;
    shownIn = document.querySelector('.page');
    if (shownIn) shownIn.setAttribute('inert', '');
    document.documentElement.classList.add('sh-on');
    modal.hidden = false;
    closeBtn.focus();
    running.forEach(function (r) { r.stop(); });
  }

  function close() {
    modal.hidden = true;
    document.documentElement.classList.remove('sh-on');
    // INERT COMES OFF FIRST. The link that opened this is inside the inert
    // subtree, and focusing something inert does nothing at all — the focus
    // would have been dropped on <body> and the reader put back at the top of
    // the document.
    if (shownIn) { shownIn.removeAttribute('inert'); shownIn = null; }
    if (lastFocus && document.contains(lastFocus)) lastFocus.focus();
    running.forEach(function (r) { r.start(); });
  }
}());
