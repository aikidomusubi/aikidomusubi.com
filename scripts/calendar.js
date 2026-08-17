/* Dated calendar — progressive enhancement only.
 *
 * Every month and every entry is already in the HTML, rendered at build time
 * from _data/calendar.yml. This file decides which month to show first, moves
 * between them, switches views, and marks today and the past — all things that
 * depend on when the page is read rather than when it was built.
 *
 * With JavaScript off the reader still gets every entry: the agenda list's
 * source <ol> is visible markup, and the month sections are revealed by the
 * no-JS fallback at the end of the stylesheet cascade.
 */
(function () {
  'use strict';

  var root = document.getElementById('calendar-view');
  if (!root) return;

  var months = Array.prototype.slice.call(root.querySelectorAll('.cal-month'));
  if (!months.length) return;

  var label = root.querySelector('#cal-current');
  var nothing = root.querySelector('.cal-nothing');
  var today = root.dataset.today;
  var current = 0;

  // The build stamps the date it ran. If the site has not been rebuilt for a
  // while that is stale, so the browser's own clock wins.
  var now = new Date();
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  today = now.getFullYear() + '-' + pad(now.getMonth() + 1) + '-' + pad(now.getDate());
  var thisMonth = today.slice(0, 7);

  // -------------------------------------------------------------------------
  // Which month to open on
  //
  // The current month if it was rendered, otherwise the next month that has
  // anything in it — landing on a past month because it happens to be first in
  // the archive would be a poor first impression.
  // -------------------------------------------------------------------------
  (function pickStart() {
    for (var i = 0; i < months.length; i++) {
      if (months[i].dataset.month === thisMonth) { current = i; return; }
    }
    for (var j = 0; j < months.length; j++) {
      if (months[j].dataset.month > thisMonth) { current = j; return; }
    }
    current = months.length - 1;
  })();

  function show(i) {
    current = Math.max(0, Math.min(months.length - 1, i));
    months.forEach(function (m, idx) { m.hidden = idx !== current; });
    if (label) label.textContent = months[current].querySelector('.cal-month-head').textContent.trim();

    var prev = root.querySelector('[data-nav="prev"]');
    var next = root.querySelector('[data-nav="next"]');
    if (prev) prev.disabled = current === 0;
    if (next) next.disabled = current === months.length - 1;

    if (nothing) {
      nothing.hidden = !!months[current].querySelector('.cal-entry');
    }
  }

  root.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-nav]');
    if (!btn || btn.disabled) return;
    var how = btn.dataset.nav;
    if (how === 'prev') show(current - 1);
    else if (how === 'next') show(current + 1);
    else if (how === 'today') {
      for (var i = 0; i < months.length; i++) {
        if (months[i].dataset.month >= thisMonth) { show(i); return; }
      }
      show(months.length - 1);
    }
  });

  // -------------------------------------------------------------------------
  // Today, and everything before it
  // -------------------------------------------------------------------------
  Array.prototype.forEach.call(root.querySelectorAll('.cal-cell[data-date]'), function (cell) {
    var d = cell.dataset.date;
    if (d === today) cell.setAttribute('data-today', '');
    else if (d < today) cell.setAttribute('data-past', '');
  });

  // -------------------------------------------------------------------------
  // Agenda list
  //
  // Split at build time would be wrong the moment the site sat unbuilt for a
  // week, so the source list is partitioned here instead. An entry counts as
  // upcoming until the day it ends, not the day it starts — a three-day
  // seminar should not drop into the archive on its second morning.
  // -------------------------------------------------------------------------
  (function splitList() {
    var source = root.querySelector('.cal-list-source');
    if (!source) return;
    var up = root.querySelector('.cal-list-items[data-when="upcoming"]');
    var past = root.querySelector('.cal-list-items[data-when="past"]');
    if (!up || !past) return;

    var items = Array.prototype.slice.call(source.children);
    items.forEach(function (li) {
      var ends = li.dataset.until || li.dataset.date;
      if (ends >= today) {
        up.appendChild(li);
      } else {
        li.setAttribute('data-past', '');
        past.insertBefore(li, past.firstChild);   // most recent first
      }
    });
    source.remove();

    Array.prototype.forEach.call(root.querySelectorAll('.cal-list-head'), function (h) {
      var list = root.querySelector('.cal-list-items[data-when="' + h.dataset.when + '"]');
      h.hidden = !list || !list.children.length;
    });
  })();

  // -------------------------------------------------------------------------
  // View toggle
  // -------------------------------------------------------------------------
  var panels = {};
  Array.prototype.forEach.call(root.querySelectorAll('[data-view-panel]'), function (p) {
    panels[p.dataset.viewPanel] = p;
  });

  var viewBtns = Array.prototype.slice.call(root.querySelectorAll('.cal-view-btn'));

  function setView(name) {
    Object.keys(panels).forEach(function (k) { panels[k].hidden = k !== name; });
    viewBtns.forEach(function (b) {
      b.setAttribute('aria-selected', b.dataset.view === name ? 'true' : 'false');
    });
    // Month navigation means nothing in the list view.
    var nav = root.querySelector('.cal-nav');
    if (nav) nav.hidden = name !== 'month';

    try {
      var url = new URL(window.location.href);
      if (name === 'month') url.searchParams.delete('view');
      else url.searchParams.set('view', name);
      window.history.replaceState({}, '', url);
    } catch (err) { /* the toggle still works */ }
  }

  viewBtns.forEach(function (b) {
    b.addEventListener('click', function () { setView(b.dataset.view); });
  });

  // ?view=list makes a shared link open on the list, which is the more useful
  // one to send to somebody on a phone.
  var startView = 'month';
  try {
    if (new URL(window.location.href).searchParams.get('view') === 'list') startView = 'list';
  } catch (err) { /* default stands */ }

  show(current);
  setView(startView);
})();
