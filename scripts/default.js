/* jshint esversion: 6 */

////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////

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

    var falseHeader = document.querySelector('.falseHeader');
    var shadower = document.querySelector('.shadower');
    var fixedHead = document.querySelector('.fixedHead');
    if (!falseHeader || !shadower || !fixedHead) return;

    var base = null;
    var stickyHeight = 0;

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
      stickyHeight = offsetTop(falseHeader);

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

      falseHeader.classList.toggle('clipped', scrolled >= stickyHeight);
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
      var navbar = document.querySelector('.navbar.sticky-top');
      var mainNavHeight = navbar ? outerHeight(navbar) : 0;

      // Measure in the un-fixed state, otherwise the bar is out of flow and
      // reports the wrong document position.
      stickyBar.classList.remove('stickyIsFixed');
      placeholder.style.display = 'none';
      placeholder.style.height = '0px';

      var barHeight = outerHeight(stickyBar, true);
      stickyTop = Math.round(offsetTop(stickyBar) - mainNavHeight);

      placeholder.style.height = barHeight + 'px';
      placeholder.style.display = 'none';
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
      var link = e.target.closest('.stickyBar a[href^="#"]');
      if (!link) return;

      var target = document.querySelector(link.getAttribute('href'));
      if (!target) return;

      e.preventDefault();

      document.querySelectorAll('.stickyBar .nav-link').forEach(function(l) {
        l.classList.remove('active');
      });
      link.classList.add('active');

      var navbar = document.querySelector('.navbar.sticky-top');
      var bar = document.querySelector('.stickyBar');
      var offset = (navbar ? outerHeight(navbar) : 0) + (bar ? outerHeight(bar) : 0);

      window.scrollTo({
        top: offsetTop(target) - offset,
        behavior: 'smooth'
      });
    });
  }

  function modalContent() {

    // Bootstrap 5 fires native CustomEvents whose type is the whole string
    // "show.bs.modal". jQuery would read ".bs.modal" as a namespace on a
    // "show" event and never match, so this listens natively.
    document.querySelectorAll('a[data-bs-toggle="modal"]').forEach(function(trigger) {
      var selector = trigger.getAttribute('data-bs-target');
      var album = trigger.getAttribute('data-target-name');
      if (!selector || !album) return;

      var modal = document.querySelector(selector);
      if (!modal) return;

      // Bound once at init rather than on every click, so repeated opens
      // do not stack duplicate listeners, and fetched once per album.
      modal.addEventListener('show.bs.modal', function() {
        var body = modal.querySelector('.modal-body');
        if (!body || body.dataset.loaded === 'true') return;

        fetch('/photos/' + album + '.html')
          .then(function(res) {
            if (!res.ok) throw new Error('HTTP ' + res.status);
            return res.text();
          })
          .then(function(html) {
            body.innerHTML = html;
            body.dataset.loaded = 'true';
          })
          .catch(function(err) {
            console.error('Could not load album "' + album + '":', err);
          });
      });
    });
  }

  function fullCalendarChangeIcons() {

    var svgIconTh = '<svg aria-hidden="true" focusable="false" data-prefix="fas" data-icon="th" class="svg-inline--fa fa-th fa-w-16" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="currentColor" d="M149.333 56v80c0 13.255-10.745 24-24 24H24c-13.255 0-24-10.745-24-24V56c0-13.255 10.745-24 24-24h101.333c13.255 0 24 10.745 24 24zm181.334 240v-80c0-13.255-10.745-24-24-24H205.333c-13.255 0-24 10.745-24 24v80c0 13.255 10.745 24 24 24h101.333c13.256 0 24.001-10.745 24.001-24zm32-240v80c0 13.255 10.745 24 24 24H488c13.255 0 24-10.745 24-24V56c0-13.255-10.745-24-24-24H386.667c-13.255 0-24 10.745-24 24zm-32 80V56c0-13.255-10.745-24-24-24H205.333c-13.255 0-24 10.745-24 24v80c0 13.255 10.745 24 24 24h101.333c13.256 0 24.001-10.745 24.001-24zm-205.334 56H24c-13.255 0-24 10.745-24 24v80c0 13.255 10.745 24 24 24h101.333c13.255 0 24-10.745 24-24v-80c0-13.255-10.745-24-24-24zM0 376v80c0 13.255 10.745 24 24 24h101.333c13.255 0 24-10.745 24-24v-80c0-13.255-10.745-24-24-24H24c-13.255 0-24 10.745-24 24zm386.667-56H488c13.255 0 24-10.745 24-24v-80c0-13.255-10.745-24-24-24H386.667c-13.255 0-24 10.745-24 24v80c0 13.255 10.745 24 24 24zm0 160H488c13.255 0 24-10.745 24-24v-80c0-13.255-10.745-24-24-24H386.667c-13.255 0-24 10.745-24 24v80c0 13.255 10.745 24 24 24zM181.333 376v80c0 13.255 10.745 24 24 24h101.333c13.255 0 24-10.745 24-24v-80c0-13.255-10.745-24-24-24H205.333c-13.255 0-24 10.745-24 24z"></path></svg>';
    var svgIconBars = '<svg aria-hidden="true" focusable="false" data-prefix="fas" data-icon="bars" class="svg-inline--fa fa-bars fa-w-14" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"><path fill="currentColor" d="M16 132h416c8.837 0 16-7.163 16-16V76c0-8.837-7.163-16-16-16H16C7.163 60 0 67.163 0 76v40c0 8.837 7.163 16 16 16zm0 160h416c8.837 0 16-7.163 16-16v-40c0-8.837-7.163-16-16-16H16c-8.837 0-16 7.163-16 16v40c0 8.837 7.163 16 16 16zm0 160h416c8.837 0 16-7.163 16-16v-40c0-8.837-7.163-16-16-16H16c-8.837 0-16 7.163-16 16v40c0 8.837 7.163 16 16 16z"></path></svg>';

    document.querySelectorAll('.fc-myCustomListWeekButton-button.btn.btn-primary').forEach(function(btn) {
      btn.innerHTML = svgIconBars;
    });
    document.querySelectorAll('.fc-myCustomDayGridWeekButton-button.btn.btn-primary').forEach(function(btn) {
      btn.innerHTML = svgIconTh;
    });
  }

  function initPhotoFilter(navSelector, cardSelector) {
    const navLinks = document.querySelectorAll(`${navSelector} .nav-link`);
    const cards = document.querySelectorAll(cardSelector);

    if (!navLinks.length || !cards.length) return;

    navLinks.forEach(link => {
      link.addEventListener('click', function(e) {
        e.preventDefault();

        navLinks.forEach(l => l.classList.remove('active'));
        this.classList.add('active');

        const filter = this.dataset.filter;

        cards.forEach(card => {
          if (filter === 'all') {
            card.style.display = '';
          } else {
            card.style.display = card.classList.contains(filter) ? '' : 'none';
          }
        });
      });
    });
  }

////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////

function init() {

  const page = document.body.classList;

  // Pages that carry an in-page anchor bar.
  const STICKY_PAGES = [
    'index-8oGCaMDs',
    'classes-CJc2lhFv',
    'resources-uStNjtHz',
    'photos-QDOJ1pyG',
    'events-hFZ2XXIp',
    'access-information-NdxqmVbV'
  ];

  hiddenCode();

  if (page.contains('index-8oGCaMDs')) {
    parallaxHeader();
  }

  if (page.contains('training-schedule-IFMn5oCc')) {
    fullCalendarChangeIcons();
  }

  if (page.contains('photos-QDOJ1pyG')) {
    modalContent();
    initPhotoFilter('#photos-QDOJ1pyG-nav', '.photos-QDOJ1pyG-container .col');
  }

  if (page.contains('events-hFZ2XXIp')) {
    initPhotoFilter('#events-hFZ2XXIp-nav', '.events-hFZ2XXIp-container .card');

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
