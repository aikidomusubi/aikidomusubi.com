/* Glosario — search and category chips.
 *
 * The page ships every entry and is filtered here. 123 entries is small
 * enough that sending them all costs less than a round trip, and it means the
 * glossary is readable, printable and indexable with JavaScript off — which is
 * also why the bar is rendered `hidden` and only revealed once this runs. A
 * search box that does nothing is worse than no search box.
 *
 * Searching hides individual entries; a group whose entries have all gone
 * hides too, so the page never shows a heading with nothing under it.
 */
(function () {
  'use strict';

  var bar, chips, input, groups, terms, countEl, emptyEl, countTpl;
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
      groups[j].hidden = !groups[j].querySelector('.gl-t:not([hidden])');
    }

    countEl.textContent = countTpl.replace('N', shown);
    emptyEl.hidden = shown > 0;
  }

  function init() {
    bar = document.querySelector('[data-gl-bar]');
    if (!bar) return;

    input = document.getElementById('gl-q');
    chips = bar.querySelectorAll('.gl-chips button');
    countEl = document.querySelector('[data-gl-count]');
    emptyEl = document.querySelector('[data-gl-empty]');
    groups = document.querySelectorAll('.gl-grp');

    // The count line is rendered as "123 entradas"; keep the noun and replace
    // only the number, so the four languages stay in the data.
    countTpl = countEl.textContent.replace(/^\s*\d+/, 'N');

    terms = [].map.call(document.querySelectorAll('.gl-t'), function (el) {
      return { el: el, dataset: el.dataset, hay: fold(el.dataset.s || '') };
    });

    bar.hidden = false;   // already false via the inline reveal; harmless if it ran

    input.addEventListener('input', function () { q = input.value; apply(); });
    input.addEventListener('search', function () { q = input.value; apply(); });

    bar.querySelector('[data-gl-clear]').addEventListener('click', function () {
      input.value = '';
      q = '';
      apply();
      input.focus();
    });

    [].forEach.call(chips, function (b) {
      b.addEventListener('click', function () {
        cat = b.dataset.cat;
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
