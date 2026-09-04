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

    // Anything anchored to a cell in the month that just went away has to let
    // go of it — today that is the entry detail panel.
    root.dispatchEvent(new CustomEvent('cal:changed'));
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

    // The source list is the two sources concatenated — the events collection
    // then the dated facts — so it is only sorted within each. Sort the whole
    // thing before splitting, or September lands after October.
    var items = Array.prototype.slice.call(source.children);
    // Date, then clock. Sorting on the date alone left the five entries on
    // 12 December in whatever order two unstable Liquid sorts produced —
    // the 21:00 dinner above the 11:00 open mat. `data-start` is absent on an
    // all-day entry, and '' sorts before any time, which is where it belongs.
    items.sort(function (a, b) {
      var ka = a.dataset.date + (a.dataset.start || '');
      var kb = b.dataset.date + (b.dataset.start || '');
      return ka < kb ? -1 : ka > kb ? 1 : 0;
    });
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
  // Tap a day (narrow screens)
  //
  // The month grid shrinks to numbers and colour bars on a phone, which says
  // "something is on" without saying what. This puts the what one tap away
  // instead of forcing a view switch.
  // ---------------------------------------------------------------------------
  // Copying an entry somewhere else
  // ---------------------------------------------------------------------------
  // The day-peek and the week view both re-render by cloning entries out of the
  // month grid. A raw clone would bring the detail panel with it — a second
  // element with the same id, and a trigger button with no listener behind it,
  // so a dead control. Both surfaces are already detail views in their own
  // right, so the copy is stripped back to the plain entry it used to be.
  function cleanClone(entry) {
    var c = entry.cloneNode(true);
    var pop = c.querySelector('.cal-pop');
    if (pop) pop.parentNode.removeChild(pop);
    c.removeAttribute('data-open');

    var trigger = c.querySelector('.cal-entry-trigger');
    if (trigger) {                       // unwrap: it was the script's doing
      while (trigger.firstChild) c.insertBefore(trigger.firstChild, trigger);
      c.removeChild(trigger);
    }
    return c;
  }

  // -------------------------------------------------------------------------
  var peek = root.querySelector('.cal-daypeek');

  if (peek) {
    root.addEventListener('click', function (e) {
      var cell = e.target.closest('.cal-cell[data-date]');
      if (!cell) return;
      // Only acts where the grid is actually collapsed; on a wide screen the
      // entries are already legible in the cell.
      if (!window.matchMedia('(max-width: 767.98px)').matches) return;

      var entries = cell.querySelectorAll('.cal-entry');
      root.querySelectorAll('.cal-cell[data-selected]').forEach(function (c) {
        c.removeAttribute('data-selected');
      });

      if (!entries.length) { peek.hidden = true; return; }

      cell.setAttribute('data-selected', '');
      peek.innerHTML = '';
      var h = document.createElement('p');
      h.className = 'cal-daypeek-date';
      var d = new Date(cell.dataset.date + 'T00:00:00');
      h.textContent = d.getDate() + ' ' + (JSON.parse(root.dataset.monthNames || '[]')[d.getMonth()] || '');
      peek.appendChild(h);
      Array.prototype.forEach.call(entries, function (en) { peek.appendChild(cleanClone(en)); });
      peek.hidden = false;
    });
  }

  // -------------------------------------------------------------------------
  // Week view
  //
  // Built from the month grid's own cells rather than from a third copy of the
  // data in the markup. Every cell carries data-date and its entries, so a week
  // is seven lookups — and because a day gets a whole row here instead of a
  // 5.5rem box, each entry can show what the month cell has no room for.
  // -------------------------------------------------------------------------
  var weekPanel = root.querySelector('.cal-week');
  var renderWeek = null;

  if (weekPanel) {
    var weekList = weekPanel.querySelector('.cal-week-days');
    var weekLabel = weekPanel.querySelector('.cal-week-label');
    var weekEmpty = weekPanel.querySelector('.cal-week-empty');
    var weekStartsSun = root.dataset.weekStart === 'sun';
    // The whole day_names table is emitted rather than a pre-filtered one:
    // building a JSON object by string-concatenation in Liquid was fragile and
    // the table is small enough that jsonify plus a lookup here is simpler.
    var lang = root.dataset.lang || 'es';
    var dayTable = JSON.parse(root.dataset.dayNames || '{}');
    function dayLong(key) {
      var row = dayTable[key];
      return (row && row[lang] && row[lang].long) || '';
    }
    var monthNames = JSON.parse(root.dataset.monthNames || '[]');

    function iso(d) {
      return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
    }

    // Monday-start weeks need Sunday pulled back to the previous week.
    function startOfWeek(d) {
      var x = new Date(d.getFullYear(), d.getMonth(), d.getDate());
      var shift = weekStartsSun ? x.getDay() : (x.getDay() + 6) % 7;
      x.setDate(x.getDate() - shift);
      return x;
    }

    var weekCursor = startOfWeek(new Date());

    function cellFor(dateStr) {
      return root.querySelector('.cal-cell[data-date="' + dateStr + '"]');
    }

    renderWeek = function () {
      weekList.innerHTML = '';
      var any = false;
      var first = null, last = null;

      for (var i = 0; i < 7; i++) {
        var d = new Date(weekCursor);
        d.setDate(d.getDate() + i);
        var key = iso(d);
        if (i === 0) first = d;
        if (i === 6) last = d;

        var cell = cellFor(key);
        var entries = cell ? cell.querySelectorAll('.cal-entry') : [];

        var li = document.createElement('li');
        li.className = 'cal-week-day';
        li.dataset.date = key;
        if (key === today) li.setAttribute('data-today', '');
        else if (key < today) li.setAttribute('data-past', '');

        var head = document.createElement('p');
        head.className = 'cal-week-dayname';
        var dayKey = ['sun','mon','tue','wed','thu','fri','sat'][d.getDay()];
        head.innerHTML = '<span class="cal-week-dow">' + dayLong(dayKey) + '</span>' +
                         '<span class="cal-week-date">' + d.getDate() + ' ' + (monthNames[d.getMonth()] || '') + '</span>';
        li.appendChild(head);

        var body = document.createElement('div');
        body.className = 'cal-week-entries';
        if (entries.length) {
          any = true;
          Array.prototype.forEach.call(entries, function (e) {
            body.appendChild(cleanClone(e));
          });
        } else {
          var none = document.createElement('p');
          none.className = 'cal-week-none';
          none.textContent = '—';
          none.setAttribute('aria-hidden', 'true');
          body.appendChild(none);
        }
        li.appendChild(body);
        weekList.appendChild(li);
      }

      if (weekLabel && first && last) {
        var a = first.getDate() + ' ' + (monthNames[first.getMonth()] || '');
        var b = last.getDate() + ' ' + (monthNames[last.getMonth()] || '');
        weekLabel.textContent = a + ' – ' + b + ' ' + last.getFullYear();
      }
      if (weekEmpty) weekEmpty.hidden = any;
    };

    weekPanel.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-weeknav]');
      if (!btn) return;
      weekCursor.setDate(weekCursor.getDate() + (btn.dataset.weeknav === 'next' ? 7 : -7));
      renderWeek();
    });
  }

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
    // Month navigation belongs to the month view alone.
    var nav = root.querySelector('.cal-nav');
    if (nav) nav.hidden = name !== 'month';
    if (name === 'week' && renderWeek) renderWeek();

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
    var v = new URL(window.location.href).searchParams.get('view');
    if (v === 'list' || v === 'week') startView = v;
  } catch (err) { /* default stands */ }

  show(current);
  setView(startView);

  // -------------------------------------------------------------------------
  // Entry detail panels
  // -------------------------------------------------------------------------
  // An entry used to be a bare link that carried you off the page without
  // saying what to. It is a disclosure now: it opens a panel with the date, the
  // venue, a couple of sentences and the link as a button inside it.
  //
  // NOT a hover tooltip. SC 1.4.13 wants hover content dismissible, hoverable
  // and persistent, and hover does not exist on the phone where a calendar
  // mostly gets read. So: click and Enter open it, Escape and an outside click
  // close it, focus returns to what opened it, and hover is an extra on
  // pointer devices rather than the mechanism.
  //
  // The no-JavaScript path is the one already in the HTML — an <a> that
  // navigates. Everything below only runs once this file has.
  (function entryPanels() {
    var open = null;          // the .cal-entry currently showing its panel
    var hoverTimer = null;
    var canHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;

    var entries = Array.prototype.slice.call(root.querySelectorAll('.cal-month .cal-entry'))
      .filter(function (e) { return e.querySelector('.cal-pop'); });

    entries.forEach(function (entry, i) {
      var pop = entry.querySelector('.cal-pop');
      pop.id = pop.id || 'cal-pop-' + i;

      // The entry carries no link of its own any more, so it needs something
      // focusable: a button wrapped around the text it already shows. The real
      // link is the panel's call to action, once.
      var trigger = document.createElement('button');
      trigger.type = 'button';
      trigger.className = 'cal-entry-trigger';
      while (entry.firstChild && entry.firstChild !== pop) {
        trigger.appendChild(entry.firstChild);
      }
      entry.insertBefore(trigger, pop);

      // AND IT NEEDS A NAME OF ITS OWN.
      //
      // On a phone the month grid shrinks an entry to a 0.35rem coloured bar
      // and hides all three of its spans with `display: none` (see the narrow
      // rule in styles/calendar.less). The button wrapped round them is then a
      // control with no text a screen reader can reach — ten unnamed buttons in
      // a month, and a plain WCAG 4.1.2 failure on the page a phone is most
      // likely to be reading.
      //
      // The name is the text the entry already carries, read before anything
      // hides it. On a wide screen that text is visible and the label repeats
      // it exactly, which is what 2.5.3 wants; on a narrow one it is the only
      // name there is.
      var label = (trigger.textContent || '').replace(/\s+/g, ' ').trim();
      if (label) trigger.setAttribute('aria-label', label);

      trigger.setAttribute('aria-expanded', 'false');
      trigger.setAttribute('aria-controls', pop.id);

      trigger.addEventListener('click', function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        toggle(entry, entry !== open);
      });

      if (canHover) {
        entry.addEventListener('mouseenter', function () {
          window.clearTimeout(hoverTimer);
          hoverTimer = window.setTimeout(function () { toggle(entry, true); }, 160);
        });
        // The panel is inside the entry, so moving onto it is not a leave —
        // which is exactly the "hoverable" half of 1.4.13.
        entry.addEventListener('mouseleave', function () {
          window.clearTimeout(hoverTimer);
          hoverTimer = window.setTimeout(function () {
            if (entry === open && !entry.contains(document.activeElement)) close();
          }, 260);
        });
      }

      pop.querySelector('.cal-pop-x').addEventListener('click', function () {
        close(true);
      });
    });

    function place(entry) {
      var pop = entry.querySelector('.cal-pop');
      // Measure against the viewport and flip when the panel would run off the
      // right-hand side, which it does for anything in the last two columns.
      pop.removeAttribute('data-flip');
      var r = pop.getBoundingClientRect();
      if (r.right > document.documentElement.clientWidth - 8) {
        pop.setAttribute('data-flip', '');
      }
      // And upward when there is more room above than below.
      pop.removeAttribute('data-up');
      r = pop.getBoundingClientRect();
      if (r.bottom > window.innerHeight - 8 &&
          entry.getBoundingClientRect().top > window.innerHeight / 2) {
        pop.setAttribute('data-up', '');
      }
    }

    function toggle(entry, on) {
      if (on && open && open !== entry) close();
      var pop = entry.querySelector('.cal-pop');
      var trigger = entry.querySelector('.cal-entry-trigger');
      pop.hidden = !on;
      entry.toggleAttribute('data-open', on);
      if (trigger) trigger.setAttribute('aria-expanded', on ? 'true' : 'false');
      if (on) { place(entry); open = entry; } else if (open === entry) { open = null; }
    }

    function close(refocus) {
      if (!open) return;
      var entry = open;
      toggle(entry, false);
      if (refocus) {
        var t = entry.querySelector('.cal-entry-trigger');
        if (t) t.focus();
      }
    }

    document.addEventListener('click', function (ev) {
      if (open && !open.contains(ev.target)) close();
    });

    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && open) close(true);
    });

    // Changing month or view while a panel is open would leave it floating over
    // a grid it no longer belongs to.
    root.addEventListener('cal:changed', function () { close(); });
    viewBtns.forEach(function (b) {
      b.addEventListener('click', function () { close(); });
    });
    window.addEventListener('resize', function () { if (open) place(open); }, { passive: true });
  })();
})();
