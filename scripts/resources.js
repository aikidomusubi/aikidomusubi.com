/* Recursos — search and category chips.
 *
 * The page ships every entry and is filtered here. 123 entries is small
 * enough that sending them all costs less than a round trip, and it means the
 * resources is readable, printable and indexable with JavaScript off — which is
 * also why the bar is rendered `hidden` and only revealed once this runs. A
 * search box that does nothing is worse than no search box.
 *
 * Searching hides individual entries; a group whose entries have all gone
 * hides too, so the page never shows a heading with nothing under it.
 */
(function () {
  'use strict';

  var bar, chips, input, groups, terms, countEl, numEl, emptyEl;
  var filterBtn, filterLabel;
  var cat = 'all', q = '';

  // Accents are part of how these words are written but not of how people
  // type them: someone looking for "dojo" should find "dōjō", and someone
  // looking for "técnica" should find it without the accent.
  function fold(s) {
    return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }

  function apply() {
    var needle = fold(q.trim()), shown = 0, i, j;

    for (i = 0; i < terms.length; i++) {
      var t = terms[i];
      var ok = (cat === 'all' || t.dataset.cat === cat) &&
               (!needle || t.hay.indexOf(needle) > -1);
      t.el.hidden = !ok;
      if (ok) shown++;
    }

    for (j = 0; j < groups.length; j++) {
      groups[j].hidden = !groups[j].querySelector('.rs-row:not([hidden])');
    }

    numEl.textContent = shown;
    emptyEl.hidden = shown > 0;
  }

  function init() {
    bar = document.querySelector('[data-rs-bar]');
    if (!bar) return;

    input = document.getElementById('rs-q');
    chips = bar.querySelectorAll('.rs-chips button');
    countEl = document.querySelector('[data-rs-count]');
    emptyEl = document.querySelector('[data-rs-empty]');
    groups = document.querySelectorAll('.rs-grp');

    // The number is its own element, so nothing has to reconstruct the sentence
    // around it. This used to read the rendered text back out and substitute the
    // digits, which worked but meant the four languages had to survive a
    // regular expression.
    numEl = countEl.querySelector('[data-rs-n]');

    // The phone's one-line bar: a button, and the chips in a drawer under it.
    // Above @bp-md the CSS hides the button and keeps the drawer open, so this
    // runs there too and changes nothing anybody can see.
    filterBtn = bar.querySelector('[data-rs-filter]');
    filterLabel = bar.querySelector('[data-rs-filter-label]');

    // `.rs-row`, which is what the layout renders. This said `.rs-t` — a class
    // that exists nowhere — so `terms` was empty, every chip filtered to zero
    // and every group hid itself. It looked fine on load only because apply()
    // does not run until the first interaction.
    terms = [].map.call(document.querySelectorAll('.rs-row'), function (el) {
      return { el: el, dataset: el.dataset, hay: fold(el.dataset.s || '') };
    });

    bar.hidden = false;   // already false via the inline reveal; harmless if it ran

    input.addEventListener('input', function () { q = input.value; apply(); });
    input.addEventListener('search', function () { q = input.value; apply(); });

    bar.querySelector('[data-rs-clear]').addEventListener('click', function () {
      input.value = '';
      q = '';
      apply();
      input.focus();
    });

    if (filterBtn) {
      filterBtn.addEventListener('click', function () {
        var open = bar.classList.toggle('is-open');
        filterBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    }

    [].forEach.call(chips, function (b) {
      b.addEventListener('click', function () {
        cat = b.dataset.cat;

        // The button becomes the chip: it carries the label, and `data-active`
        // paints it like a chosen chip so the state reads without opening the
        // drawer. `all` is a filter like any other and simply is not marked.
        if (filterLabel) filterLabel.textContent = b.dataset.label || '';
        if (filterBtn) filterBtn.toggleAttribute('data-active', cat !== 'all');

        // Picking closes it. The drawer exists to be got out of the way.
        if (filterBtn && bar.classList.contains('is-open')) {
          bar.classList.remove('is-open');
          filterBtn.setAttribute('aria-expanded', 'false');
        }

        [].forEach.call(chips, function (o) {
          var on = o === b;
          o.toggleAttribute('data-on', on);
          o.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        apply();
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
}());

/* ---------------------------------------------------------------------------
 * The syllabus panel
 *
 * Six sheets are already in the page; this shows one. Everything here is
 * progressive enhancement: the buttons in the list are real links to
 * `/recursos/?r=kyu3`, and without JavaScript that URL loads the page with the
 * sheet visible — which is why the sheets are rendered rather than fetched.
 *
 * The URL is the state. Opening pushes `?r=<id>`, closing pops back, Back
 * closes, and a link that somebody sends opens on the right sheet. That is the
 * part a modal usually gets wrong, and it is also what makes Share worth
 * having: the thing being shared is a sheet, not a page.
 * ------------------------------------------------------------------------- */
(function () {
  'use strict';

  var panel = document.getElementById('ex-panel');
  if (!panel) return;

  var html   = document.documentElement;
  var scrim  = document.querySelector('.ex-scrim');
  var scroll = panel.querySelector('[data-ex-scroll]');
  var titleEl = panel.querySelector('[data-ex-title]');
  var printEl = panel.querySelector('[data-ex-printname]');
  var acts   = panel.querySelector('[data-ex-acts]');
  var legend = panel.querySelector('[data-ex-legend]');
  var printUrlEl = panel.querySelector('[data-ex-printurl]');
  var eyebrowEl = panel.querySelector('[data-ex-eyebrow]');
  var eyebrowDefault = eyebrowEl ? eyebrowEl.textContent : '';
  var sheets = [].slice.call(panel.querySelectorAll('[data-ex-sheet]'));
  var last = null;
  var current = null;
  var baseTitle = document.title;

  function sheetById(id) {
    for (var i = 0; i < sheets.length; i++) {
      if (sheets[i].dataset.exSheet === id) return sheets[i];
    }
    return null;
  }

  // "The whole programme" is the 1st kyū sheet with the colours on: the
  // syllabus is cumulative, so those are the same list of techniques and only
  // the presentation differs.
  function show(id) {
    var all = id === 'all';
    var target = sheetById(all ? 'kyu1' : id);
    if (!target) return false;
    sheets.forEach(function (s) { s.hidden = s !== target; });
    if (legend) legend.hidden = !all;
    panel.classList.toggle('ex-colour', all);

    // The on-screen heading and the printed masthead name the same sheet — a
    // printout that says something different from what was on screen is a bug
    // nobody notices until it is on paper.
    var name = all ? (panel.dataset.nameAll || '') : (target.dataset.name || '');
    // The panel holds two kinds of document — a grading sheet and a rule — and
    // the line above the title says which. It used to say "grading programme"
    // over the dojo rules.
    if (eyebrowEl) {
      eyebrowEl.textContent = all ? eyebrowDefault
                                  : (target.dataset.eyebrow || eyebrowDefault);
    }
    titleEl.textContent = name;
    var full = ((eyebrowEl && eyebrowEl.textContent) ? eyebrowEl.textContent + ' · ' : '') + name;
    if (printEl) printEl.textContent = full;
    if (printUrlEl) printUrlEl.textContent = sheetUrl(id);
    document.title = full + ' · ' + baseTitle;
    current = id;
    if (scroll) scroll.scrollTop = 0;
    return true;
  }

  // One place builds the shareable, printable address of a sheet.
  function sheetUrl(id) {
    return location.origin + location.pathname + (id ? '?r=' + encodeURIComponent(id) : '');
  }

  function open(id, push) {
    if (!show(id)) return;
    last = document.activeElement;
    html.classList.add('ex-on');
    panel.removeAttribute('inert');
    panel.setAttribute('aria-hidden', 'false');
    if (push && history.pushState) {
      history.pushState({ ex: id }, '', '?r=' + encodeURIComponent(id));
    }
    var x = panel.querySelector('[data-ex-close]');
    if (x) setTimeout(function () { x.focus(); }, 60);
  }

  function close(pop) {
    if (!html.classList.contains('ex-on')) return;
    html.classList.remove('ex-on');
    panel.setAttribute('aria-hidden', 'true');
    // Focus before inert: moving focus out of a subtree that is already inert
    // drops it on <body> instead of on the control that opened the panel.
    if (last && document.contains(last)) last.focus();
    panel.setAttribute('inert', '');
    document.title = baseTitle;
    current = null;
    if (pop && history.pushState) {
      history.pushState({}, '', location.pathname);
    }
  }

  document.addEventListener('click', function (e) {
    var opener = e.target.closest('[data-ex-open]');
    if (opener) {
      // Modified clicks are the reader asking for a new tab, and the href is a
      // real URL, so let the browser have them.
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
      e.preventDefault();
      open(opener.dataset.exOpen, true);
      return;
    }
    if (e.target.closest('[data-ex-close]') || e.target === scrim) close(true);
  });

  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape' || !html.classList.contains('ex-on')) return;
    close(true);
  });

  window.addEventListener('popstate', function () {
    var id = new URLSearchParams(location.search).get('r');
    if (id && known(id)) { open(id, false); } else { close(false); }
  });

  // ---- share and print ----------------------------------------------------
  // Lifted from the timetable deliberately: the same two controls, doing the
  // same job, should behave the same way. Share hands the URL to the operating
  // system's own sheet and falls back to copying it; both buttons are built by
  // script because a dead one is worse than none.
  if (acts) {
    var ICON_SHARE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M12 3v13M8 7l4-4 4 4"/><path d="M5 14v5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5"/></svg>';
    var ICON_PRINT = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
      'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      '<path d="M6 9V3h12v6"/><rect x="3" y="9" width="18" height="8" rx="2"/>' +
      '<path d="M6 17h12v4H6z"/></svg>';

    var mk = function (label, icon) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'ex-action';
      b.innerHTML = icon + '<span>' + label + '</span>';
      acts.appendChild(b);
      return b;
    };

    var canShare = typeof navigator !== 'undefined' && typeof navigator.share === 'function';
    var canCopy = typeof navigator !== 'undefined' && navigator.clipboard &&
                  typeof navigator.clipboard.writeText === 'function';

    if (canShare || canCopy) {
      var shareBtn = mk(acts.dataset.share, ICON_SHARE);
      var shareLabel = shareBtn.querySelector('span');
      shareBtn.addEventListener('click', function () {
        var url = sheetUrl(current);
        if (canShare) {
          navigator.share({ title: titleEl.textContent, url: url }).catch(function () {});
          return;
        }
        navigator.clipboard.writeText(url).then(function () {
          var was = shareLabel.textContent;
          shareLabel.textContent = acts.dataset.shareCopied;
          shareBtn.setAttribute('data-done', '');
          setTimeout(function () {
            shareLabel.textContent = was;
            shareBtn.removeAttribute('data-done');
          }, 2000);
        }).catch(function () {});
      });
    }

    if (typeof window.print === 'function') {
      mk(acts.dataset.print, ICON_PRINT)
        .addEventListener('click', function () { window.print(); });
    }
  }

  // ---- the deep link ------------------------------------------------------
  function known(id) { return id === 'all' || !!sheetById(id); }

  var initial = new URLSearchParams(location.search).get('r');
  if (initial && known(initial)) open(initial, false);
})();
