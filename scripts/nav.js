/* Navigation — dropdowns, mobile panel, and the shrink on scroll.
 *
 * This replaces bootstrap.bundle.min.js, which was 79 KB (22 KB brotli) loaded
 * on every page for exactly two behaviours: this dropdown and this collapse.
 *
 * The menu works without any of it. Every submenu is a plain nested list that
 * CSS reveals on hover and on :focus-within, and every link is a real href, so
 * with the script blocked or still loading the navigation is a list of links
 * that works. What follows only improves it.
 */
(function () {
  'use strict';

  var nav = document.getElementById('nv');
  if (!nav) return;

  var burger = document.getElementById('nv-burger');
  var tops = Array.prototype.slice.call(nav.querySelectorAll('.nv-top'));
  var mq = window.matchMedia('(min-width: 992px)');

  // Tell the stylesheet the script is running, so it can hand hover/focus
  // behaviour over to aria-expanded instead of driving it itself.
  nav.setAttribute('data-js', '');

  // -------------------------------------------------------------------------
  // Dropdowns
  // -------------------------------------------------------------------------
  function closeAll(except) {
    tops.forEach(function (b) {
      if (b !== except) b.setAttribute('aria-expanded', 'false');
    });
  }

  tops.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      closeAll(btn);
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
    });
  });

  // A pointer leaving the whole bar closes whatever is open, but only where the
  // menu is a hover affordance at all. On touch there is no "leave".
  nav.addEventListener('mouseleave', function () {
    if (mq.matches) closeAll(null);
  });

  document.addEventListener('click', function (ev) {
    if (!nav.contains(ev.target)) {
      closeAll(null);
      setPanel(false);
    }
  });

  // Escape closes the open submenu first, then the mobile panel, returning
  // focus to whatever opened it each time.
  document.addEventListener('keydown', function (ev) {
    if (ev.key !== 'Escape') return;
    var open = tops.filter(function (b) { return b.getAttribute('aria-expanded') === 'true'; })[0];
    if (open) {
      open.setAttribute('aria-expanded', 'false');
      open.focus();
      return;
    }
    if (burger && burger.getAttribute('aria-expanded') === 'true') {
      setPanel(false);
      burger.focus();
    }
  });

  // -------------------------------------------------------------------------
  // Mobile panel
  // -------------------------------------------------------------------------
  function setPanel(open) {
    if (!burger) return;
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    nav.toggleAttribute('data-open', open);
    // Only lock the page behind a full-height panel, never on the desktop bar.
    document.documentElement.style.overflow = (open && !mq.matches) ? 'hidden' : '';
  }

  if (burger) {
    burger.addEventListener('click', function () {
      setPanel(burger.getAttribute('aria-expanded') !== 'true');
    });
  }

  // Crossing the breakpoint with the panel open would leave the page scroll
  // locked and the panel styled as a desktop bar.
  mq.addEventListener('change', function () {
    setPanel(false);
    closeAll(null);
  });

  // -------------------------------------------------------------------------
  // Shrink on scroll
  // -------------------------------------------------------------------------
  // Read in a rAF and written only when the state actually flips: a scroll
  // handler that touches the DOM on every event is the classic way to make a
  // sticky header janky.
  //
  // The threshold is measured from the nav's own position in the document, not
  // from the top of the page. On the home page the nav sits below a hero that
  // is nearly a full screen tall, and a flat 64px meant it had already shrunk —
  // hiding the utility row with the address and the languages — before a phone
  // reader had scrolled far enough to lay eyes on it.
  //
  // Measured from #nv-top, a zero-height marker sitting immediately above the
  // nav, and not from the nav itself. A sticky element reports where it is
  // currently painted — both getBoundingClientRect().top and offsetTop — so
  // once it is stuck, measuring it returns the current scroll position and the
  // threshold walks away from you. Verified: at scrollTop 900 the nav's own
  // offsetTop reads 900, while the marker still reads 715.
  var SHRINK_AT = 64;
  var shrunk = false;
  var ticking = false;
  var navTop = 0;
  var marker = document.getElementById('nv-top');

  function measure() {
    navTop = marker ?
      marker.getBoundingClientRect().top + window.pageYOffset : 0;
  }

  function apply() {
    var should = window.pageYOffset > navTop + SHRINK_AT;
    if (should !== shrunk) {
      shrunk = should;
      nav.toggleAttribute('data-shrunk', shrunk);
    }
    ticking = false;
  }

  window.addEventListener('scroll', function () {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(apply);
    }
  }, { passive: true });

  // The hero is sized in viewport units, so the nav's position moves when the
  // viewport does — including when a mobile browser's URL bar slides away.
  window.addEventListener('resize', function () {
    measure();
    apply();
  }, { passive: true });

  measure();
  apply();
})();
