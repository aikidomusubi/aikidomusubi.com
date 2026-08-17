/* Training timetable — progressive enhancement only.
 *
 * The timetable itself is static HTML rendered at build time from
 * _data/schedule.yml. Everything in this file is optional: with JavaScript off
 * the visitor still gets the full week, every venue, every class, correctly
 * laid out. That is the point of the rewrite — the old build shipped an empty
 * <div> and fetched 174 KB of calendar library to fill it, so no JS meant no
 * schedule, and a crawler saw nothing at all.
 *
 * What this adds: category and venue filtering, day tabs on narrow screens,
 * today's column, a now-line, and per-class .ics export.
 */
(function () {
  'use strict';

  var root = document.getElementById('timetable');
  if (!root) return;

  var DAYS = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
  var grid = root.querySelector('.timetable-grid');
  var days = Array.prototype.slice.call(root.querySelectorAll('.tt-day'));
  var classes = Array.prototype.slice.call(root.querySelectorAll('.tt-class'));
  var catInputs = Array.prototype.slice.call(root.querySelectorAll('input[name="category"]'));
  var locInputs = Array.prototype.slice.call(root.querySelectorAll('input[name="location"]'));

  function minutes(hhmm) {
    var p = hhmm.split(':');
    return parseInt(p[0], 10) * 60 + parseInt(p[1], 10);
  }

  // -------------------------------------------------------------------------
  // Density: a 45-minute block cannot hold four lines of text. Tag blocks by
  // duration so the stylesheet can drop the level, then the venue. Done here
  // rather than in Liquid because the thresholds are about rendered height,
  // which is a presentation concern.
  // -------------------------------------------------------------------------
  classes.forEach(function (el) {
    var dur = minutes(el.dataset.end) - minutes(el.dataset.start);
    // A block sharing its column with a concurrent class is half width, which
    // puts its start and end times on separate lines. That costs a line, so it
    // runs out of room roughly an hour sooner than a full-width block does.
    var narrow = el.hasAttribute('data-narrow');
    if (dur < 45) el.setAttribute('data-tiny', '');
    else if (dur < (narrow ? 90 : 60)) el.setAttribute('data-short', '');
  });

  // -------------------------------------------------------------------------
  // Filtering
  // -------------------------------------------------------------------------
  function activeCategories() {
    return catInputs.filter(function (i) { return i.checked; })
                    .map(function (i) { return i.value; });
  }

  function activeLocation() {
    var on = locInputs.filter(function (i) { return i.checked; })[0];
    return on ? on.value : null;
  }

  function apply() {
    var cats = activeCategories();
    var loc = activeLocation();

    classes.forEach(function (el) {
      var show = el.dataset.location === loc && cats.indexOf(el.dataset.category) !== -1;
      if (show) el.removeAttribute('hidden');
      else el.setAttribute('hidden', '');
    });

    // Empty-state per day, so a filtered-out day says so instead of showing a
    // blank column with no explanation.
    days.forEach(function (day) {
      var any = day.querySelector('.tt-class:not([hidden])');
      var msg = day.querySelector('.tt-empty');
      if (msg) msg.hidden = !!any;
    });

    // Mirror checked state onto the label as an attribute. The stylesheet uses
    // :has() for this, which is fine everywhere current, but the attribute
    // keeps the dimming correct if :has() is unavailable.
    catInputs.forEach(function (i) {
      i.closest('.tt-chip').toggleAttribute('data-off', !i.checked);
    });
  }

  catInputs.forEach(function (i) { i.addEventListener('change', apply); });

  locInputs.forEach(function (i) {
    i.addEventListener('change', function () {
      apply();
      // Keep the deep link the old calendar supported: ?location=<slug>.
      try {
        var url = new URL(window.location.href);
        url.searchParams.set('location', i.dataset.slug);
        window.history.replaceState({}, '', url);
      } catch (e) { /* older browsers: the filter still works */ }
    });
  });

  // Honour ?location=<slug> (and #location=<slug>, which the old build also read)
  (function initLocation() {
    var slug = null;
    try {
      slug = new URL(window.location.href).searchParams.get('location');
      if (!slug && window.location.hash) {
        slug = new URLSearchParams(window.location.hash.replace(/^#/, '')).get('location');
      }
    } catch (e) { return; }
    if (!slug) return;
    var match = locInputs.filter(function (i) { return i.dataset.slug === slug; })[0];
    if (match) match.checked = true;
  })();

  // -------------------------------------------------------------------------
  // Day tabs (narrow screens)
  // -------------------------------------------------------------------------
  var todayKey = DAYS[new Date().getDay()];

  var tabs = document.createElement('div');
  tabs.className = 'tt-tabs';
  tabs.setAttribute('role', 'tablist');

  days.forEach(function (day) {
    var key = day.dataset.day;
    var head = day.querySelector('.tt-day-head');
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'tt-tab';
    btn.setAttribute('role', 'tab');
    btn.dataset.day = key;
    btn.textContent = head.querySelector('.tt-day-short').textContent.trim();
    btn.setAttribute('aria-label', head.querySelector('.tt-day-long').textContent.trim());
    if (key === todayKey) btn.setAttribute('data-today', '');
    tabs.appendChild(btn);
  });

  function selectDay(key) {
    days.forEach(function (d) { d.toggleAttribute('data-active', d.dataset.day === key); });
    Array.prototype.forEach.call(tabs.children, function (b) {
      var on = b.dataset.day === key;
      b.setAttribute('aria-selected', on ? 'true' : 'false');
      b.setAttribute('tabindex', on ? '0' : '-1');
    });
  }

  tabs.addEventListener('click', function (e) {
    var btn = e.target.closest('.tt-tab');
    if (btn) selectDay(btn.dataset.day);
  });

  // Arrow-key navigation, which is what a tablist is expected to support.
  tabs.addEventListener('keydown', function (e) {
    if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
    var list = Array.prototype.slice.call(tabs.children);
    var i = list.indexOf(document.activeElement);
    if (i === -1) return;
    e.preventDefault();
    var next = list[(i + (e.key === 'ArrowRight' ? 1 : list.length - 1)) % list.length];
    next.focus();
    selectDay(next.dataset.day);
  });

  grid.parentNode.insertBefore(tabs, grid);
  selectDay(todayKey);

  // Today's column on the wide layout.
  days.forEach(function (d) { d.toggleAttribute('data-today', d.dataset.day === todayKey); });

  // -------------------------------------------------------------------------
  // Now-line — only drawn while the current time falls inside a band
  // -------------------------------------------------------------------------
  var slot = parseInt(root.dataset.slot, 10) || 15;

  // Rebuild the band offsets from the axis labels rather than duplicating the
  // YAML here, so the two cannot drift.
  var bandStarts = [];
  Array.prototype.forEach.call(root.querySelectorAll('.tt-axis-label'), function (el) {
    bandStarts.push({ row: parseInt(el.style.getPropertyValue('--row'), 10),
                      min: minutes(el.textContent.trim()) });
  });

  function rowForNow() {
    var now = new Date();
    var mins = now.getHours() * 60 + now.getMinutes();
    // Find the hour label at or before now, within the same band run.
    var best = null;
    bandStarts.forEach(function (b) {
      if (b.min <= mins && (!best || b.min > best.min)) best = b;
    });
    if (!best) return null;
    var delta = mins - best.min;
    if (delta > 60) return null;               // we are in the gap between bands
    return best.row + delta / slot;
  }

  function drawNow() {
    var existing = root.querySelector('.tt-now');
    if (existing) existing.remove();
    var today = days.filter(function (d) { return d.dataset.day === todayKey; })[0];
    if (!today) return;
    var row = rowForNow();
    if (row === null) return;
    var body = today.querySelector('.tt-day-body');
    var line = document.createElement('div');
    line.className = 'tt-now';
    line.style.top = 'calc((' + row + ' - 1) * var(--slot-h))';
    line.setAttribute('aria-hidden', 'true');
    body.appendChild(line);
  }

  drawNow();
  setInterval(drawNow, 60000);

  // -------------------------------------------------------------------------
  // Add to calendar
  //
  // Built as a Blob at click time rather than shipped as files: 21 classes in
  // four languages would be 84 static .ics files to keep in sync with the YAML.
  // -------------------------------------------------------------------------
  var ICS_DAY = { sun: 'SU', mon: 'MO', tue: 'TU', wed: 'WE', thu: 'TH', fri: 'FR', sat: 'SA' };
  var icsLabel = root.dataset.icsLabel || 'Add to calendar';

  function pad(n) { return (n < 10 ? '0' : '') + n; }

  function nextOccurrence(dayKey, hhmm) {
    var target = DAYS.indexOf(dayKey);
    var d = new Date();
    var delta = (target - d.getDay() + 7) % 7;
    d.setDate(d.getDate() + delta);
    var p = hhmm.split(':');
    d.setHours(parseInt(p[0], 10), parseInt(p[1], 10), 0, 0);
    return d;
  }

  function stamp(d) {
    return d.getFullYear() + pad(d.getMonth() + 1) + pad(d.getDate()) +
           'T' + pad(d.getHours()) + pad(d.getMinutes()) + '00';
  }

  function icsFor(el) {
    var start = nextOccurrence(el.dataset.day, el.dataset.start);
    var end = nextOccurrence(el.dataset.day, el.dataset.end);
    var uid = [el.dataset.category, el.dataset.location, el.dataset.day,
               el.dataset.start.replace(':', '')].join('-') + '@aikidomusubi.com';
    return [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//Aikido Musubi//Training schedule//EN',
      'CALSCALE:GREGORIAN',
      'BEGIN:VEVENT',
      'UID:' + uid,
      'DTSTAMP:' + stamp(new Date()),
      'DTSTART;TZID=Europe/Madrid:' + stamp(start),
      'DTEND;TZID=Europe/Madrid:' + stamp(end),
      'RRULE:FREQ=WEEKLY;BYDAY=' + ICS_DAY[el.dataset.day],
      'SUMMARY:' + el.dataset.title,
      'LOCATION:' + el.dataset.place,
      'END:VEVENT',
      'END:VCALENDAR'
    ].join('\r\n');
  }

  classes.forEach(function (el) {
    var a = document.createElement('a');
    a.className = 'tt-ics';
    a.href = '#';
    a.textContent = icsLabel;
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var blob = new Blob([icsFor(el)], { type: 'text/calendar;charset=utf-8' });
      var url = URL.createObjectURL(blob);
      var dl = document.createElement('a');
      dl.href = url;
      dl.download = (el.dataset.category + '-' + el.dataset.day + '.ics');
      document.body.appendChild(dl);
      dl.click();
      dl.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    });
    el.appendChild(a);
  });

  apply();
})();
