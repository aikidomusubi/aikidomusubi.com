/* Gallery — filtering and the local-album lightbox.
 *
 * Every tile is in the HTML already, rendered at build time. This hides the
 * ones that do not match and keeps the filter in the URL so a filtered view can
 * be linked to. With JavaScript off every chip is checked and every tile is
 * visible, which is also what a crawler sees.
 */
(function () {
  'use strict';

  var root = document.getElementById('gx-controls');
  var grid = document.querySelector('.gx-grid');
  if (!root || !grid) return;

  var tiles = Array.prototype.slice.call(grid.querySelectorAll('.gx-tile'));
  var tagInputs = Array.prototype.slice.call(root.querySelectorAll('input[name="tag"]'));
  var kindInputs = Array.prototype.slice.call(root.querySelectorAll('input[name="kind"]'));
  var yearInputs = Array.prototype.slice.call(root.querySelectorAll('input[name="year"]'));
  var count = root.querySelector('.gx-count');
  var empty = grid.querySelector('.gx-empty');

  function checked(list) {
    return list.filter(function (i) { return i.checked; }).map(function (i) { return i.value; });
  }

  function activeYear() {
    var on = yearInputs.filter(function (i) { return i.checked; })[0];
    return on ? on.value : 'all';
  }

  function apply() {
    var tags = checked(tagInputs);
    var kinds = checked(kindInputs);
    var year = activeYear();
    var shown = 0;

    tiles.forEach(function (t) {
      // A tile carries several tags; it survives if any of them is on.
      var mine = (t.dataset.tags || '').split(/\s+/).filter(Boolean);
      var okTag = mine.some(function (x) { return tags.indexOf(x) !== -1; });
      var okKind = kinds.indexOf(t.dataset.kind) !== -1;
      var okYear = year === 'all' || t.dataset.year === year;
      var show = okTag && okKind && okYear;
      t.hidden = !show;
      if (show) shown++;
    });

    if (empty) empty.hidden = shown !== 0;
    if (count) writeStatus(shown, tags, kinds, year);
    syncUrl(tags, kinds, year);
  }

  // The status line. It used to read "9 / 462", which says nine of what, out of
  // what, and why? Now it names the filters that are on and offers the way back
  // out of them. Templates come from _data/gallery.yml via data-* on the <p>,
  // so the four translations live where the rest of the copy does.
  function fill(tpl, n, total) {
    return String(tpl || '')
      .replace('{n}', n)
      .replace('{total}', total)
      .replace(/\{items\}/g, count.dataset.items || '');
  }

  function labelsFor(list, values) {
    return list.filter(function (i) { return values.indexOf(i.value) !== -1; })
      .map(function (i) {
        var span = i.parentNode.querySelector('span:not(.gx-chip-dot):not(.gx-chip-n)');
        return span ? span.textContent.trim() : i.value;
      });
  }

  function writeStatus(shown, tags, kinds, year) {
    var total = tiles.length;
    var filtered = shown !== total;

    count.textContent = '';

    var text = document.createElement('span');
    text.textContent = filtered ?
      fill(count.dataset.showing, shown, total) :
      fill(count.dataset.all, shown, total);
    count.appendChild(text);

    if (filtered) {
      // Only name a facet when it is actually narrowing something: all five
      // tags ticked is not a filter, it is the default.
      var facets = [];
      if (tags.length && tags.length < tagInputs.length) {
        facets = facets.concat(labelsFor(tagInputs, tags));
      }
      if (kinds.length && kinds.length < kindInputs.length) {
        facets = facets.concat(labelsFor(kindInputs, kinds));
      }
      if (year !== 'all') facets.push(year);

      if (facets.length) {
        var f = document.createElement('span');
        f.className = 'gx-count-facets';
        f.textContent = ' · ' + facets.join(' · ');
        count.appendChild(f);
      }

      var clear = document.createElement('button');
      clear.type = 'button';
      clear.className = 'gx-clear';
      clear.textContent = count.dataset.clear || '';
      clear.addEventListener('click', reset);
      count.appendChild(clear);
    }
  }

  function reset() {
    tagInputs.forEach(function (i) { i.checked = true; });
    kindInputs.forEach(function (i) { i.checked = true; });
    yearInputs.forEach(function (i) { i.checked = i.value === 'all'; });
    apply();
    // Focus lands somewhere real rather than on a button that just vanished.
    if (tagInputs[0]) tagInputs[0].focus();
  }

  // Parameters are dropped when they carry no information, so an unfiltered
  // page keeps the clean URL — the one that gets shared and indexed.
  function syncUrl(tags, kinds, year) {
    try {
      var url = new URL(window.location.href);
      if (tags.length === tagInputs.length) url.searchParams.delete('tags');
      else url.searchParams.set('tags', tags.join(','));
      if (kinds.length === kindInputs.length) url.searchParams.delete('kind');
      else url.searchParams.set('kind', kinds.join(','));
      if (year === 'all') url.searchParams.delete('year');
      else url.searchParams.set('year', year);
      window.history.replaceState({}, '', url);
    } catch (err) { /* filtering still works */ }
  }

  function readUrl() {
    var params;
    try { params = new URL(window.location.href).searchParams; }
    catch (err) { return; }

    function restore(list, value) {
      if (!value) return;
      var want = value.split(',');
      list.forEach(function (i) { i.checked = want.indexOf(i.value) !== -1; });
      // A selection matching nothing would render an empty page with no way
      // back except editing the URL.
      if (!list.some(function (i) { return i.checked; })) {
        list.forEach(function (i) { i.checked = true; });
      }
    }
    restore(tagInputs, params.get('tags'));
    restore(kindInputs, params.get('kind'));

    var y = params.get('year');
    if (y) yearInputs.forEach(function (i) { i.checked = i.value === y; });
  }

  root.addEventListener('change', apply);
  readUrl();
  apply();

})();
