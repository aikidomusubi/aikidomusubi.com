/* Fees — carousel controls.
 *
 * The card row is a native scroll container with scroll-snap: it works by
 * trackpad, swipe, shift-wheel and keyboard with no script at all. This adds the
 * arrows and dots, because a thin scrollbar is quiet about there being more.
 *
 * ONE DOT PER SCROLL POSITION, NOT PER CARD.
 *
 * Five cards with three in view is three positions, not five: once the row is
 * scrolled fully right, cards four and five are on screen together and neither
 * can ever sit at the left edge. Dots four and five had nowhere to go — they
 * scrolled to the same place as dot three and then reported the wrong card as
 * current. Positions are what the control can actually reach, so positions are
 * what it offers.
 *
 * The count is derived from measurement rather than assumed, and recalculated on
 * resize, because how many cards fit changes with the breakpoint.
 */
(function () {
  'use strict';

  var lists = Array.prototype.slice.call(document.querySelectorAll('.fee-cards'));
  if (!lists.length) return;

  // One per carousel, called when a panel is revealed. See the note by the
  // period listener at the foot of this file.
  var refreshers = [];

  // Chevrons. The first pass used the "skip to end" double-triangle from the
  // media-player family, which reads as jump-to-last rather than next.
  var ARROW = {
    prev: '<svg viewBox="0 0 320 512" fill="currentColor" aria-hidden="true"><path d="M9.4 233.4c-12.5 12.5-12.5 32.8 0 45.3l192 192c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L77.3 256 246.6 86.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-192 192z"/></svg>',
    next: '<svg viewBox="0 0 320 512" fill="currentColor" aria-hidden="true"><path d="M310.6 233.4c12.5 12.5 12.5 32.8 0 45.3l-192 192c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L242.7 256 73.4 86.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l192 192z"/></svg>'
  };

  var L = (document.documentElement.lang || 'es').slice(0, 2);
  var WORDS = {
    es: { prev: 'Anterior', next: 'Siguiente', go: 'Ver el grupo' },
    ca: { prev: 'Anterior', next: 'Següent',   go: 'Veure el grup' },
    en: { prev: 'Previous', next: 'Next',      go: 'Show group' },
    ja: { prev: '前へ',      next: '次へ',      go: 'グループを表示' }
  };
  var t = WORDS[L] || WORDS.es;

  // The container rests a few pixels in from zero because of its own padding,
  // so "fully left" is not scrollLeft === 0.
  var EDGE = 8;

  lists.forEach(function (list) {
    var cards = Array.prototype.slice.call(list.querySelectorAll('.fee-card'));
    if (cards.length < 2) return;

    var nav = document.createElement('div');
    nav.className = 'fee-nav';
    var prev = button('fee-arrow', t.prev, ARROW.prev);
    var dots = document.createElement('ul');
    dots.className = 'fee-dots';
    var next = button('fee-arrow', t.next, ARROW.next);
    nav.appendChild(prev);
    nav.appendChild(dots);
    nav.appendChild(next);
    list.parentNode.insertBefore(nav, list.nextSibling);

    var bullets = [];

    function motion() {
      return window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
    }

    // One card plus the gap, read from the DOM so it survives a breakpoint
    // changing the card width.
    function step() {
      var a = cards[0].getBoundingClientRect();
      var b = cards[1].getBoundingClientRect();
      return Math.round(b.left - a.left) || Math.round(a.width);
    }

    function positions() {
      var max = list.scrollWidth - list.clientWidth;
      if (max <= EDGE) return 1;
      return Math.round(max / step()) + 1;
    }

    function buildDots() {
      var n = positions();
      if (bullets.length === n) return;
      dots.textContent = '';
      bullets = [];
      for (var i = 0; i < n; i++) {
        (function (index) {
          var li = document.createElement('li');
          var b = button('fee-dot', t.go + ' ' + (index + 1), '');
          b.addEventListener('click', function () {
            list.scrollTo({ left: index * step(), behavior: motion() });
          });
          li.appendChild(b);
          dots.appendChild(li);
          bullets.push(b);
        })(i);
      }
      // A single position is no carousel; the arrows would be dead too.
      nav.hidden = n < 2;
    }

    prev.addEventListener('click', function () {
      list.scrollBy({ left: -step(), behavior: motion() });
    });
    next.addEventListener('click', function () {
      list.scrollBy({ left: step(), behavior: motion() });
    });

    function sync() {
      var max = list.scrollWidth - list.clientWidth;
      prev.disabled = list.scrollLeft <= EDGE;
      next.disabled = list.scrollLeft >= max - EDGE;

      var here = Math.round(list.scrollLeft / step());
      if (here > bullets.length - 1) here = bullets.length - 1;
      if (here < 0) here = 0;
      bullets.forEach(function (b, i) {
        b.setAttribute('aria-current', i === here ? 'true' : 'false');
      });
    }

    var ticking = false;
    list.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () { ticking = false; sync(); });
    }, { passive: true });

    var resizing;
    window.addEventListener('resize', function () {
      clearTimeout(resizing);
      resizing = setTimeout(function () { buildDots(); sync(); }, 150);
    });

    // The period panels are shown and hidden by CSS alone — four radios and
    // `:has()`, deliberately no script. That means nothing tells this code when
    // a panel appears, and a hidden panel measures zero: scrollWidth and
    // clientWidth are both 0, `positions()` returns 1, and `nav.hidden = n < 2`
    // took the dots and both arrows away. Only the panel visible at load ever
    // had controls.
    //
    // A ResizeObserver is the right listener because it watches the thing that
    // actually changed — the row going from no box to a real one. It also
    // covers a late web font reflowing the cards, which the resize handler
    // alone would miss.
    function refresh() {
      if (list.clientWidth === 0) return;   // still hidden; nothing to measure
      buildDots();
      sync();
    }
    refreshers.push(refresh);

    if (window.ResizeObserver) {
      new ResizeObserver(refresh).observe(list);
    }

    buildDots();
    sync();
  });

  // The period panels are shown and hidden by CSS alone — four radios and
  // `:has()`, deliberately no script — so nothing tells this code when a panel
  // appears. That matters because a hidden panel measures zero: scrollWidth and
  // clientWidth are both 0, `positions()` returns 1, and `nav.hidden = n < 2`
  // took the dots and both arrows away. Only the panel visible at load ever had
  // controls.
  //
  // The ResizeObserver above is a safety net for genuine resizes and for a late
  // web font reflowing the cards. It is NOT the mechanism here: it does not fire
  // when an element goes from display:none to visible, which is exactly this
  // case. The radios are, because a change on them is the event that means "a
  // different panel is on screen".
  //
  // Measured synchronously, on purpose. Reading clientWidth forces the pending
  // style and layout work, and `:has()` has already reassigned visibility by
  // then — the new panel reports its real width in the same tick. Deferring to
  // requestAnimationFrame was the first attempt and it was wrong twice over:
  // unnecessary, since the value is available immediately, and unreliable,
  // because rAF does not run in a backgrounded or occluded tab, which left the
  // controls hidden for anyone who switched period in one.
  var periods = document.querySelectorAll('input[name="fee-period"]');
  Array.prototype.forEach.call(periods, function (radio) {
    radio.addEventListener('change', function () {
      refreshers.forEach(function (fn) { fn(); });
    });
  });

  function button(cls, label, svg) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = cls;
    b.setAttribute('aria-label', label);
    if (svg) b.innerHTML = svg;
    return b;
  }
})();
