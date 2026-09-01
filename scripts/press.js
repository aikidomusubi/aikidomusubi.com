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
