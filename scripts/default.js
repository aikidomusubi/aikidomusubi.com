/* jshint esversion: 6 */

////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////

  // --- which map app can this device actually open? ------------------------
  // A maps.apple.com link opens the Maps APP on an iPhone, an iPad or a Mac,
  // with the dojo's claimed listing and turn-by-turn directions in it. On
  // anything else it opens a web page that asks the reader to get Apple Maps.
  // So both links are rendered and this stamps the root with which one to
  // show; the CSS hides the other. With this script off, both show, which is
  // correct rather than broken.
  //
  // Platform and not browser sniffing: what is being asked is "is there a Maps
  // app behind this link", and that is a property of the device. iPadOS
  // reports itself as a Mac, which is why the test is shaped this way.
  (function () {
    var ua = navigator.userAgent || '';
    var apple = /\b(iPhone|iPad|iPod|Macintosh)\b/.test(ua) &&
                !/\b(Android|CrOS|Windows)\b/.test(ua);
    document.documentElement.setAttribute('data-maps', apple ? 'apple' : 'other');
  }());

  // Document-relative top of an element, the equivalent of jQuery's
  // .offset().top. getBoundingClientRect() is viewport-relative, so the
  // current scroll offset has to be added back in.
  function offsetTop(el) {
    return el.getBoundingClientRect().top + window.pageYOffset;
  }

  // jQuery's .outerHeight(true) — border box plus vertical margins.
  function outerHeight(el, includeMargins) {
    var height = el.offsetHeight;
    if (includeMargins) {
      var cs = window.getComputedStyle(el);
      height += parseFloat(cs.marginTop) + parseFloat(cs.marginBottom);
    }
    return height;
  }

  // Runs fn at most once per animation frame.
  function onAnimationFrame(fn) {
    var ticking = false;
    return function() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function() {
        ticking = false;
        fn();
      });
    };
  }

////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////

  function hiddenCode() {

    var konami = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a'];
    var pressed = [];

    document.addEventListener('keydown', function(e) {
      pressed.push(e.key);

      // Only the tail matters, so the buffer never grows past the code.
      if (pressed.length > konami.length) {
        pressed = pressed.slice(-konami.length);
      }

      var hit = pressed.length === konami.length && konami.every(function(key, i) {
        return pressed[i] === key;
      });

      if (hit) {
        pressed = [];
        window.location.href = 'https://youtu.be/UzdDAd9EBOI';
      }
    });
  }

  function parallaxHeader() { // https://codepen.io/theaftermath87/pen/mJqywj

    var shadower = document.querySelector('.shadower');
    var fixedHead = document.querySelector('.fixedHead');
    if (!shadower || !fixedHead) return;

    var base = null;

    // Where the header art sits vertically at this viewport size. null means
    // the viewport is too small to offset it at all.
    function baseOffset(x, y) {
      if (x >= 992 && x <= 1919) return -215;
      if (x >= 1920 && y <= 1199) return -430;
      if (x >= 1920 && y >= 1200) return -512;
      return null;
    }

    // Viewport size was previously read once at load and never again, so
    // resizing across a breakpoint left the header positioned for the old
    // size until the page was reloaded. Re-measured on resize instead.
    function measure() {
      var x = window.innerWidth || document.documentElement.clientWidth;
      var y = window.innerHeight || document.documentElement.clientHeight;

      base = baseOffset(x, y);

      // Clear the inline value when no offset applies at this size, so the
      // stylesheet's own background-position takes over again.
      if (base === null) {
        fixedHead.style.backgroundPosition = '';
      } else {
        fixedHead.style.backgroundPosition = '50% ' + (base - window.pageYOffset / 2) + 'px';
      }
    }

    measure();

    // Unthrottled scroll handlers writing to style are the classic cause of
    // jank; coalescing to one write per frame keeps the parallax smooth.
    window.addEventListener('scroll', onAnimationFrame(function() {
      var scrolled = window.pageYOffset;

      shadower.style.opacity = Math.min(scrolled / 400, 1);

      if (base !== null) {
        fixedHead.style.backgroundPosition = '50% ' + (base - scrolled / 2) + 'px';
      }
      // The `clipped` class this used to toggle pinned a copy of the nav to the
      // top of the homepage, duplicating what the nav's own sticky positioning
      // does on every other page. The nav is an ordinary sibling of the hero
      // now and sticks by itself.
    }), { passive: true });

    window.addEventListener('resize', onAnimationFrame(measure));
    window.addEventListener('orientationchange', onAnimationFrame(measure));
  }

  function stickySection() {

    var bars = document.querySelectorAll('.stickyBar');
    var stickyBar = null;
    for (var i = 0; i < bars.length; i++) {
      if (bars[i].offsetHeight > 0) { stickyBar = bars[i]; break; }
    }
    if (!stickyBar) return;

    // A placeholder holds the bar's space open once it goes fixed, so the
    // page does not jump by the bar's height at the moment it detaches.
    var placeholder = stickyBar.nextElementSibling;
    if (!placeholder || !placeholder.classList.contains('sticky-placeholder')) {
      placeholder = document.createElement('div');
      placeholder.className = 'sticky-placeholder';
      stickyBar.parentNode.insertBefore(placeholder, stickyBar.nextSibling);
    }

    var stickyTop = null;

    function calculate() {
      // How much nav the bar has to clear once it is pinned. That is the nav's
      // SHRUNK height, because the reader has scrolled by then — and it is the
      // same value the bar's own margin-top uses, published as --nav-shrunk so
      // the two cannot drift. Measuring `.nv-shell` here instead would read its
      // resting height and pin the bar ~48px early, making it jump.
      //
      // This used to query `.navbar.sticky-top`, which the site has not had
      // since the Bootstrap navbar was replaced, so it measured 0 and the bar
      // pinned underneath the nav.
      var root = getComputedStyle(document.documentElement);
      var mainNavHeight = parseFloat(root.getPropertyValue('--nav-shrunk')) *
                          parseFloat(root.fontSize);

      // Measure in the un-fixed state, otherwise the bar is out of flow and
      // reports the wrong document position.
      stickyBar.classList.remove('stickyIsFixed');
      placeholder.style.display = 'none';
      placeholder.style.height = '0px';

      var barHeight = outerHeight(stickyBar, true);
      stickyTop = Math.round(offsetTop(stickyBar) - mainNavHeight);

      placeholder.style.height = barHeight + 'px';
      placeholder.style.display = 'none';

      // Published so CSS can clear it. An in-page link on a page that has this
      // bar must land below the nav AND below the bar, and the bar's height is
      // content-driven — there is no token for it. Anything reading this falls
      // back to 0px when the script has not run, which leaves the nav-only
      // clearance the :target rule already provides.
      document.documentElement.style.setProperty('--sticky-h', barHeight + 'px');
    }

    function update() {
      if (stickyTop === null) return;
      var scrollTop = Math.round(window.pageYOffset);

      // -1 keeps iOS rubber-band scrolling from flickering at the boundary.
      if (scrollTop >= stickyTop - 1) {
        if (!stickyBar.classList.contains('stickyIsFixed')) {
          stickyBar.classList.add('stickyIsFixed');
          placeholder.style.display = 'block';
        }
      } else if (stickyBar.classList.contains('stickyIsFixed')) {
        stickyBar.classList.remove('stickyIsFixed');
        placeholder.style.display = 'none';
      }
    }

    // Deferred so fonts and images have settled and the measurement is real.
    setTimeout(function() {
      calculate();
      update();
    }, 50);

    window.addEventListener('scroll', onAnimationFrame(update), { passive: true });

    var recalculate = onAnimationFrame(function() {
      calculate();
      update();
    });
    window.addEventListener('resize', recalculate);
    window.addEventListener('orientationchange', recalculate);
  }

  function smoothScrolling() {

    // Called from more than one branch below, and delegated from the document,
    // so guard against binding the same handler twice.
    if (document.body.dataset.smoothScrollBound === 'true') return;
    document.body.dataset.smoothScrollBound = 'true';

    document.addEventListener('click', function(e) {
      // The sticky bar's own links, plus any in-page link to an event card —
      // the calendar sends people to /seminarios/#event-<slug>, and a card
      // landing under the sticky header would be worse than not scrolling.
      var link = e.target.closest('.stickyBar a[href^="#"], a[href^="#event-"]');
      if (!link) return;

      var target = document.querySelector(link.getAttribute('href'));
      if (!target) return;

      e.preventDefault();

      document.querySelectorAll('.stickyBar .nav-link').forEach(function(l) {
        l.classList.remove('active');
      });
      link.classList.add('active');

      // No manual scrollTo. The offset used to be measured from
      // `.navbar.sticky-top`, an element this site has not had since the
      // Bootstrap navbar was replaced — so it evaluated to zero and the page
      // landed with the target under the nav. `scroll-margin-top: @anchor-clear`
      // does the job in CSS now, which also means it is right on the very first
      // navigation rather than only after a reload.
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  // Arriving from the calendar with #event-<slug> in the URL used to be
  // corrected here, a frame after load, because the browser had already jumped
  // to the wrong place. It jumped to the wrong place because the correction —
  // and the landing — were both measured against `.navbar.sticky-top`, which no
  // longer exists, so the offset was zero. `scroll-margin-top` on the target
  // handles it in CSS, before paint, with no dependency on when images finish
  // loading. Nothing to do at load time any more.



////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////

// The width of the vertical scrollbar, published for CSS. Full-bleed sections
// are one viewport wide, and `100vw` counts the scrollbar, so without this they
// hang past the edge and the page scrolls sideways. Zero on macOS and on touch,
// where the scrollbar is an overlay. See .full-bleed() in styles/base.less.
function scrollbarWidth() {
  function set() {
    var w = window.innerWidth - document.documentElement.clientWidth;
    document.documentElement.style.setProperty('--sbw', (w > 0 ? w : 0) + 'px');
  }
  set();
  window.addEventListener('resize', onAnimationFrame(set));
}

function init() {

  const page = document.body.classList;

  // Pages that carry an in-page anchor bar. `photos-QDOJ1pyG` is gone from the
  // list with the page itself; the albums live in _data/gallery.yml now.
  const STICKY_PAGES = [
    'index-8oGCaMDs',
    'classes-CJc2lhFv',
    'resources-uStNjtHz',
    'events-hFZ2XXIp',
    'access-information-NdxqmVbV'
  ];

  scrollbarWidth();
  hiddenCode();

  if (page.contains('index-8oGCaMDs')) {
    parallaxHeader();
  }

  // fullCalendarChangeIcons() and initPhotoFilter() used to be called here.
  // The first swapped icons on FullCalendar's toolbar buttons, and FullCalendar
  // is gone; the second filtered the photos page, which is gone, and the events
  // nav, which the seminars page's own script replaced. Neither hook appears on
  // a single built page — checked across all eighty.
  if (page.contains('events-hFZ2XXIp')) {
    document.querySelectorAll('.page .container>main .card .card-body').forEach(cardBody => {
      const lastCardText = cardBody.querySelector('.card-text:last-of-type');
      if (lastCardText && lastCardText.children.length === 3) {
        cardBody.classList.add('has-3-links');
      }
    });
  }

  if (STICKY_PAGES.some(cls => page.contains(cls))) {
    stickySection();
    smoothScrolling();
  }

  console.log('↑ ↑ ↓ ↓ ← → ← → b a');
}

// The bundle is loaded at the end of <body>, so the document may already be
// parsed by the time this runs and DOMContentLoaded would never fire.
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
