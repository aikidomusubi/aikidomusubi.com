/* Click-to-load embeds: YouTube players and Google Maps.
 *
 * Nothing reaches Google until a visitor asks for it. On click the facade is
 * replaced by the real iframe — a youtube-nocookie.com player with autoplay, or
 * the map that button was carrying — so the click that asked for the thing is
 * the click that loads it.
 *
 * Both used to load on sight. The three maps on the access page alone pulled
 * 461 KB from Google and took that page's largest contentful paint to 17.7
 * seconds, as well as setting cookies the cookie policy promises not to set
 * before consent.
 */
(function () {
  'use strict';

  document.addEventListener('click', function (e) {
    var map = e.target.closest('.mp-facade');
    if (map) return loadMap(map);

    var btn = e.target.closest('.pv-facade');
    if (!btn) return;

    var id = btn.dataset.id;
    if (!id) return;

    var params = 'autoplay=1&rel=0';
    if (btn.dataset.params) params += '&' + btn.dataset.params;

    var frame = document.createElement('iframe');
    // -nocookie is not a substitute for the click — it still contacts Google —
    // but once the visitor has asked for the video it is the quieter host.
    frame.src = 'https://www.youtube-nocookie.com/embed/' + id + '?' + params;
    frame.title = btn.getAttribute('aria-label') || '';
    frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    frame.allowFullscreen = true;
    frame.loading = 'eager';

    var holder = btn.parentNode;
    holder.replaceChild(frame, btn);
    frame.focus();
  });

  // -------------------------------------------------------------------------
  // Venue deep links — /acceso/#aikido-musubi and its three siblings.
  //
  // The access page is a picker: four radios, and a `:has()` rule in the page
  // that shows the one panel whose radio is checked. Every other panel is
  // `display: none`, and a fragment cannot scroll to a box that is not drawn.
  // So the footer's "Dónde entrenamos" column — four links straight at those
  // ids — landed on the page with the first venue showing and no scroll, and
  // three of the four went somewhere that looked like nothing had happened.
  //
  // Three cases, and the third is the one that is easy to miss:
  //
  //   * arriving from another page. The browser tries its own scroll first,
  //     finds a hidden element and gives up. This script is `defer`, so it runs
  //     with the DOM parsed and before DOMContentLoaded; it checks the radio
  //     and scrolls itself.
  //   * `hashchange`, for a back button or a pasted address.
  //   * clicking one of the same links WHILE ON /acceso/. Nothing navigates, so
  //     there is no load; and if the hash already names this panel there is no
  //     `hashchange` either. That is why the click is intercepted rather than
  //     left to the browser: it was the case where only the currently-open
  //     venue's link appeared to work, because only that one was already
  //     scrolled into view.
  //
  // Scrolling is `scrollIntoView`, which honours the `scroll-margin-top` set on
  // `.vn-panel` in venues.less — the same @anchor-clear every other anchor on
  // the site clears the nav with. No offset is computed here.
  // -------------------------------------------------------------------------
  if (document.querySelector('.vn-panel')) initVenueLinks();

  function initVenueLinks() {
    // Runs on click, on hashchange and once now. `scroll` is false for the last
    // of those only when there is no hash to honour.
    function openVenue(hash, scroll) {
      var id = (hash || '').replace(/^#/, '');
      if (!id) return false;

      var panel = document.getElementById(id);
      if (!panel || panel.className.indexOf('vn-panel') < 0) return false;

      var radio = document.getElementById('vn-' + panel.getAttribute('data-venue'));
      if (radio) radio.checked = true;

      if (scroll) {
        // `instant`, not the document's own `scroll-behavior: smooth`, and not
        // by preference. This is a fragment link, and the browser's own answer
        // to a fragment is to arrive there — the smooth glide is for anchors
        // inside a page you are already reading. Here the panel did not exist a
        // frame ago and everything under it has just moved, so animating 1,700
        // pixels through content that changed on the way is disorienting rather
        // than smooth. It is also the reliable call: a smooth scroll is an
        // animation, and an animation that is interrupted — by the second call
        // below, by the one on `load` — simply does not finish.
        //
        // Twice, and not out of superstition. This call is what reveals the
        // panel, and what it reveals — a map facade, a floor plan, three lazy
        // entrance photos — has no height until the browser has laid it out, so
        // scrolling in the same frame measures the page as it was.
        panel.scrollIntoView({ behavior: 'instant', block: 'start' });
        requestAnimationFrame(function () {
          panel.scrollIntoView({ behavior: 'instant', block: 'start' });
        });
      }
      return true;
    }

    document.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('a[href*="#"]') : null;
      if (!a || !a.hash) return;
      // Another page's URL that merely carries a fragment is left alone.
      if (a.pathname !== location.pathname || a.host !== location.host) return;
      if (!openVenue(a.hash, true)) return;

      e.preventDefault();
      // The address bar still has to say which venue is open — a reader who
      // copies the link should get the panel they are looking at. pushState
      // rather than assigning location.hash, which would fire hashchange and
      // scroll a second time.
      if (location.hash !== a.hash) history.pushState(null, '', a.hash);
    });

    window.addEventListener('hashchange', function () {
      openVenue(location.hash, true);
    });

    openVenue(location.hash, true);

    // The lazy images inside the panel settle after `load`. Without this the
    // first scroll lands short on a cold cache and right on a warm one, which
    // is the kind of bug that only ever reproduces for somebody else.
    window.addEventListener('load', function () {
      openVenue(location.hash, true);
    });
  }

  // -------------------------------------------------------------------------
  // Entrance photos — click to enlarge.
  //
  // The cards carry a 300px crop, which is enough for a 104px slot and no use
  // for recognising a gate. The full 900px file is fetched on demand, so the
  // page does not pay ~500 KB for photos nobody opened.
  // -------------------------------------------------------------------------
  var dialog = document.getElementById('vn-dialog');

  if (dialog && typeof dialog.showModal === 'function') {
    var full = dialog.querySelector('img');
    var cap  = dialog.querySelector('.vn-dialog-cap');

    document.addEventListener('click', function (ev) {
      var shot = ev.target.closest ? ev.target.closest('.vn-shot') : null;
      if (shot) {
        // <img> rather than <picture>: one src, and the browser has already
        // told us it can do webp by loading the thumbnail from the same set.
        full.src = shot.dataset.full;
        full.onerror = function () { full.onerror = null; full.src = shot.dataset.fallback; };
        full.alt = shot.dataset.caption || '';
        cap.textContent = shot.dataset.caption || '';
        dialog.showModal();
        return;
      }
      // Clicking the backdrop closes: the click lands on the dialog itself,
      // never on its children.
      if (ev.target === dialog || (ev.target.closest && ev.target.closest('.vn-dialog-x'))) {
        dialog.close();
      }
    });

    // Drop the source when it closes so a reopen cannot flash the old photo.
    dialog.addEventListener('close', function () { full.removeAttribute('src'); });
  }

  function loadMap(btn) {
    var src = btn.dataset.src;
    if (!src) return;
    var frame = document.createElement('iframe');
    frame.src = src;
    frame.title = btn.dataset.title || '';
    frame.loading = 'eager';
    frame.referrerPolicy = 'no-referrer-when-downgrade';
    frame.allowFullscreen = true;
    btn.parentNode.replaceChild(frame, btn);
    frame.focus();
  }
})();
