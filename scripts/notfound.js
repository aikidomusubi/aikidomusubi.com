/* 404 — the kaijū and the ma-ai.
 *
 * He walks in from a random side and a throw only lands while he is inside the
 * circle. Perfect centre calls "ma-ai", the rest of the circle calls "ukemi",
 * and a miss says which way you missed. Every landed throw makes the next one
 * faster.
 *
 * The walk is driven by elapsed time and not by a fixed step per frame: a step
 * per frame ties the speed to the refresh rate, and on a 120 Hz screen he
 * walked at twice the intended pace.
 */
(function () {
  'use strict';

  var stage = document.getElementById('nf');
  if (!stage) return;

  var kaiju = document.getElementById('nf-kaiju'),
      flip  = document.getElementById('nf-flip'),
      boom  = document.getElementById('nf-boom'),
      call  = document.getElementById('nf-call'),
      elS   = document.getElementById('nf-streak'),
      elB   = document.getElementById('nf-best'),
      zone  = stage.querySelector('.nf-zone'),
      words = JSON.parse(document.getElementById('nf-words').textContent),
      reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var W = 0, mid = 0, reach = 0, x = 0, dir = 1, speed = 0,
      live = false, streak = 0, best = 0, raf = 0, last = 0;

  function measure() {
    W = stage.clientWidth;
    mid = W / 2;
    reach = Math.min(Math.max(W * 0.085, 72), 135);
    zone.style.setProperty('--z', (reach * 2) + 'px');
  }

  function place() { kaiju.style.left = (x - kaiju.offsetWidth / 2) + 'px'; }

  function spawn() {
    measure();
    dir = Math.random() < 0.5 ? 1 : -1;
    x = dir > 0 ? -kaiju.offsetWidth : W + kaiju.offsetWidth;
    speed = (126 + Math.min(streak, 9) * 22) * dir;   // px per second
    // the woodcut faces left, so it only needs flipping when walking right
    flip.style.setProperty('--f', dir > 0 ? -1 : 1);
    kaiju.classList.remove('thrown');
    kaiju.style.opacity = '';
    kaiju.style.bottom = '';
    kaiju.style.transform = '';
    void kaiju.offsetWidth;                            // flush the transition
    live = true;
    last = 0;
    place();
    raf = requestAnimationFrame(loop);
  }

  function loop(t) {
    if (!live) return;
    if (!last) last = t;
    var dt = Math.min((t - last) / 1000, 0.05);
    last = t;
    x += speed * dt;
    place();
    if ((dir > 0 && x > W + kaiju.offsetWidth) || (dir < 0 && x < -kaiju.offsetWidth)) {
      live = false;
      say(words.gone, 'bad');
      streak = 0;
      elS.textContent = '0';
      setTimeout(spawn, 650);
      return;
    }
    raf = requestAnimationFrame(loop);
  }

  function say(text, cls) {
    call.textContent = text;
    call.className = 'nf-call on ' + cls;
    setTimeout(function () { call.className = 'nf-call ' + cls; }, 950);
  }

  function strike() {
    if (!live) return;
    live = false;
    cancelAnimationFrame(raf);
    var d = Math.abs(x - mid);
    if (d <= reach) {
      streak++;
      best = Math.max(best, streak);
      elS.textContent = String(streak);
      elB.textContent = String(best);
      say(d <= reach * 0.42 ? words.maai : words.ukemi, 'good');
      boom.style.left = x + 'px';
      boom.className = 'nf-boom';
      void boom.offsetWidth;
      boom.className = 'nf-boom go';
      kaiju.classList.add('thrown');
      kaiju.style.transform = 'rotate(' + (dir > 0 ? 206 : -206) + 'deg) scale(.82)';
      kaiju.style.left = (x - kaiju.offsetWidth / 2 + dir * 280) + 'px';
      kaiju.style.bottom = '30vh';
      setTimeout(spawn, 1200);
    } else {
      say(d > reach * 2.4 ? words.early : words.late, 'bad');
      streak = 0;
      elS.textContent = '0';
      setTimeout(function () { live = true; last = 0; raf = requestAnimationFrame(loop); }, 400);
    }
  }

  stage.addEventListener('pointerdown', function (e) {
    if (!e.target.closest('a')) strike();
  });

  stage.addEventListener('keydown', function (e) {
    if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); strike(); }
  });

  window.addEventListener('resize', measure);

  if (reduce) {
    // Nothing moves. He stands in the circle and the page is still a 404.
    measure();
    x = mid;
    place();
  } else {
    window.addEventListener('load', function () { measure(); setTimeout(spawn, 500); });
  }
}());
