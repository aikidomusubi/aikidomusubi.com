/* Membership: the signup steps, the withdrawal form, and the two pages after.
 *
 * WITHOUT THIS SCRIPT EVERYTHING STILL WORKS. The signup is one long form that
 * posts to the Worker; the withdrawal form posts too. This adds, in the order
 * of docs/mockups/inscripcion-pasos.html (approved 14 October 2026):
 *
 *   steps        the four sections become four steps, with the browser's back
 *                button stepping back rather than leaving the page
 *   people       "add another person" and "remove person 2: Ana"
 *   totals       each period card priced for THIS household, the breakdown,
 *                and the dates of every charge, from scripts/pricing.js — the
 *                same engine the server prices with
 *   errors       next to their field and in a summary that takes focus, in
 *                the same words the server would use (spec 5.5)
 *   memory       the answers kept in sessionStorage while somebody is on
 *                Stripe's page, so "back" from Stripe finds them; cleared on
 *                the thank-you page. Never localStorage, never the URL.
 *
 * No personal data goes anywhere but the Worker: no analytics on these pages.
 */
(function () {
  'use strict';

  var KEY = 'su-form';

  // ---- shared helpers ------------------------------------------------------
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function fill(s, vars) {
    return String(s || '').replace(/\{(\w+)\}/g, function (m, k) { return k in vars ? vars[k] : m; });
  }
  function store(k, v) { try { sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  function load(k) { try { return JSON.parse(sessionStorage.getItem(k) || 'null'); } catch (e) { return null; } }
  function forget(k) { try { sessionStorage.removeItem(k); } catch (e) {} }
  function randomId() {
    var a = new Uint8Array(12);
    (window.crypto || window.msCrypto).getRandomValues(a);
    return Array.prototype.map.call(a, function (b) { return ('0' + b.toString(16)).slice(-2); }).join('');
  }

  function madrid(ms) {
    var parts = {};
    new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Madrid', year: 'numeric', month: 'numeric', day: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false })
      .formatToParts(new Date(ms)).forEach(function (p) { parts[p.type] = p.value; });
    return { y: +parts.year, m: +parts.month, d: +parts.day, time: parts.hour + ':' + parts.minute };
  }

  function makeFormat(lang, months) {
    function money(n) {
      var whole = Math.abs(n - Math.round(n)) < 0.005;
      var s = whole ? String(Math.round(n)) : n.toFixed(2);
      if (!whole && (lang === 'es' || lang === 'ca')) s = s.replace('.', ',');
      return lang === 'ja' ? s + 'ユーロ' : s + ' €';
    }
    function of(name) {
      if (lang === 'ca' && /^[aeiouàèéíòóú]/i.test(name)) return "d'" + name;
      return (lang === 'es' || lang === 'ca') ? 'de ' + name : name;
    }
    function date(ms, withYear) {
      var d = madrid(ms);
      var name = months[d.m - 1];
      if (lang === 'ja') return (withYear ? d.y + '年' : '') + d.m + '月' + d.d + '日';
      if (lang === 'en') return d.d + ' ' + name + (withYear ? ' ' + d.y : '');
      return d.d + ' ' + of(name) + (withYear ? ' de ' + d.y : '');
    }
    function list(items) {
      if (lang === 'ja') return items.join('・');
      if (items.length < 2) return items.join('');
      var and = lang === 'en' ? 'and' : lang === 'ca' ? 'i' : 'y';
      return items.slice(0, -1).join(', ') + ' ' + and + ' ' + items[items.length - 1];
    }
    return { money: money, date: date, list: list };
  }

  // Errors: next to the field, and in a summary that takes focus.
  function fieldEl(field) {
    return document.getElementById('su-' + field.replace(/_/g, '-')) ||
           document.getElementById('wd-' + field.replace(/_/g, '-')) ||
           document.querySelector('[name="' + field + '"]');
  }
  function errEl(field) {
    return document.getElementById('su-' + field.replace(/_/g, '-') + '-err') ||
           document.getElementById('wd-' + field.replace(/_/g, '-') + '-err');
  }
  function clearErrors(box, scope) {
    $$('.su-err', scope).forEach(function (p) { p.hidden = true; p.textContent = ''; });
    $$('[aria-invalid]', scope).forEach(function (i) { i.removeAttribute('aria-invalid'); });
    if (box) { box.hidden = true; $('ul', box).innerHTML = ''; }
  }
  function showErrors(box, errors) {
    var ul = $('ul', box);
    ul.innerHTML = '';
    errors.forEach(function (e) {
      var el = fieldEl(e.field);
      var p = errEl(e.field);
      if (p) { p.innerHTML = e.message; p.hidden = false; }
      if (el && el.setAttribute) el.setAttribute('aria-invalid', 'true');
      var li = document.createElement('li');
      var a = document.createElement('a');
      a.href = el && el.id ? '#' + el.id : '#';
      a.innerHTML = e.message;
      a.addEventListener('click', function (ev) {
        if (!el) return;
        ev.preventDefault();
        if (el.focus) el.focus();
      });
      li.appendChild(a);
      ul.appendChild(li);
    });
    box.hidden = false;
    box.focus();
  }

  // ===========================================================================
  // The signup
  // ===========================================================================
  function initSignup(root) {
    var data = JSON.parse($('#su-data').textContent);
    var P = window.MusubiPricing;
    var CAT = P.catalog(data.fees);
    var U = data.ui;
    var ERR = data.errors;
    var F = makeFormat(data.lang, U.months);
    var form = $('#su-form', root);
    var errorsBox = $('#su-errors', root);
    var sections = $$('.su-step', root);
    var navItems = $$('.su-steps li', root);
    var live = $('#su-live', root);
    var current = 1;
    var NOW = Date.now();
    var periods = {};
    data.fees.periods.forEach(function (p) { periods[p.id] = p; });

    root.classList.add('su-js');
    $('.su-steps', root).hidden = false;
    $$('.su-next, .su-back, #su-add, .su-rm', root).forEach(function (b) { b.hidden = false; });
    $$('.su-card-static', root).forEach(function (s) { s.hidden = true; });

    var err = function (field, code, vars) {
      return { field: field, code: code, message: fill(ERR[code] || ERR.generic, vars || { url: data.urls.contact }) };
    };

    // ---- people ------------------------------------------------------------
    var wrappers = $$('.su-more-person', root);       // persons 2..6
    function blockOf(slot) { return $('#su-p' + slot, root); }
    function visible(slot) {
      if (slot === 1) return true;
      var w = wrappers[slot - 2];
      return w && !w.hidden;
    }
    function val(slot, k) {
      var el = form.elements['p' + slot + '_' + k];
      if (!el) return '';
      if (el.length !== undefined && !el.tagName) {        // a RadioNodeList
        for (var i = 0; i < el.length; i++) if (el[i].checked) return el[i].value;
        return '';
      }
      return (el.value || '').trim();
    }
    function hasData(slot) { return ['given', 'family', 'cat'].some(function (k) { return val(slot, k) !== ''; }); }
    function people() {
      var out = [];
      for (var s = 1; s <= data.maxPeople; s++) {
        if (!visible(s)) continue;
        out.push({ slot: s, given: val(s, 'given'), family: val(s, 'family'), cat: val(s, 'cat'),
                   rate: val(s, 'rate') || 'general', venue: val(s, 'venue') || null,
                   bm: +val(s, 'bm') || null, by: +val(s, 'by') || null });
      }
      return out;
    }
    function nameOf(p) { return (p.given + ' ' + p.family).trim(); }

    wrappers.forEach(function (w) {
      var slot = +w.getAttribute('data-slot');
      w.open = true;
      w.hidden = !hasData(slot);
    });
    function relabel() {
      var n = 0;
      for (var s = 1; s <= data.maxPeople; s++) {
        if (!visible(s)) continue;
        n++;
        var b = blockOf(s);
        var l = $('.su-person-n', b);
        l.textContent = fill(l.getAttribute('data-label'), { n: n });
        var rm = $('.su-rm', b);
        if (rm) {
          var who = val(s, 'given');
          rm.textContent = fill(rm.getAttribute('data-label'), { n: n }) + (who ? ': ' + who : '');
        }
      }
      $('#su-add', root).hidden = wrappers.every(function (w) { return !w.hidden; });
    }
    $('#su-add', root).addEventListener('click', function () {
      var w = wrappers.filter(function (x) { return x.hidden; })[0];
      if (!w) return;
      w.hidden = false;
      w.open = true;
      relabel();
      $('.su-in', w).focus();
      changed();
    });
    $$('.su-rm', root).forEach(function (b) {
      b.addEventListener('click', function () {
        var w = b.closest('.su-more-person');
        $$('input[type=text]', w).forEach(function (i) { i.value = ''; });
        $$('select', w).forEach(function (i) { i.value = ''; });
        $$('input[type=radio]', w).forEach(function (i) { i.checked = i.value === 'general'; });
        w.hidden = true;
        relabel();
        $('#su-add', root).focus();
        changed();
      });
    });

    // The sports-centre venue: offered by age, and its conditions spelled out.
    function updateVenue(slot) {
      var b = blockOf(slot);
      var sel = $('select[name="p' + slot + '_venue"]', b);
      var cat = val(slot, 'cat');
      $$('option', sel).forEach(function (o) {
        if (!o.value) return;
        var price = o.getAttribute(cat === 'youth' ? 'data-youth' : 'data-adult');
        o.disabled = !!cat && (!price || price === '');
      });
      if (sel.selectedOptions[0] && sel.selectedOptions[0].disabled) sel.value = '';
      var cond = $('.su-cond', b);
      var o = sel.selectedOptions[0];
      if (o && o.value && cat) {
        var amount = +o.getAttribute(cat === 'youth' ? 'data-youth' : 'data-adult');
        cond.textContent = fill(cond.getAttribute('data-tpl'), { amount: F.money(amount), venue: o.textContent.trim() });
      }
    }

    // ---- step 2: the household's own numbers --------------------------------
    function members() {
      return people().filter(function (p) { return p.cat; }).map(function (p) {
        return { cat: p.cat, rate: p.rate, venue: p.rate === 'sc' ? p.venue : null };
      });
    }
    function selectedPeriod() {
      var r = $('input[name=period]:checked', form);
      return r ? r.value : '';
    }
    function kindLabel(pm, period) {
      if (pm.kind === 'full') return U.kind_full;
      if (pm.kind === 'sc') return fill(U.kind_sc, { venue: data.venues[pm.venue] || pm.venue });
      return fill(U.kind_family, { amount: F.money(CAT.family * CAT.periods[period].months) });
    }
    function renderPeriods() {
      var ms = members();
      var ps = people();
      var who = $('#su-who', root);
      who.innerHTML = '';
      if (ps.length && ps.every(function (p) { return p.given && p.cat; })) {
        var b = document.createElement('div');
        b.className = 'su-who-in';
        b.innerHTML = '<b></b><span class="su-who-l"></span>';
        $('b', b).textContent = fill(ps.length === 1 ? U.people_1 : U.people_n, { n: ps.length });
        var list = $('.su-who-l', b);
        ps.forEach(function (p) {
          var s = document.createElement('span');
          s.textContent = p.given + ' · ' + (p.cat === 'adult' ? U.adult_short : U.youth_short);
          list.appendChild(s);
        });
        var c = document.createElement('button');
        c.type = 'button'; c.className = 'su-link'; c.textContent = U.change; c.setAttribute('data-go', '1');
        b.appendChild(c);
        who.appendChild(b);
        who.hidden = false;
      } else {
        who.hidden = true;
      }
      if (!ms.length) return;
      var cmp;
      try { cmp = P.compare(ms, CAT); } catch (e) { return; }
      var anyOff = false;
      $$('.su-card[data-period]', root).forEach(function (card) {
        var id = card.getAttribute('data-period');
        var r = cmp[id];
        var input = $('input', card);
        var months = periods[id].months;
        card.classList.toggle('is-off', !r.available);
        input.disabled = !r.available;
        if (!r.available) { anyOff = true; if (input.checked) input.checked = false; }
        $('.su-card-off', card).hidden = r.available;
        $('.su-card-price', card).hidden = !r.available;
        $('.su-card-flag', card).hidden = !(r.available && id === 'annual' && r.saving > 0);
        var per = $('.su-card-per', card);
        var save = $('.su-card-save', card);
        var gift = $('.su-card-gift', card);
        per.hidden = save.hidden = gift.hidden = true;
        if (!r.available) return;
        $('.su-card-amount', card).textContent = F.money(r.total);
        if (months > 1) {
          per.textContent = fill(U.per_month, { amount: F.money(Math.round(r.total / months * 100) / 100) });
          per.hidden = false;
          if (r.saving > 0) { save.textContent = fill(U.saving, { amount: F.money(r.saving) }); save.hidden = false; }
          // An invite is for somebody already enrolled: no first-enrolment gift.
          if (!form.elements.invite.value) {
            gift.textContent = fill(U.gift, { n: ms.length });
            gift.hidden = false;
          }
        }
      });
      $('#su-why', root).hidden = !anyOff;
      $('#su-keikogi', root).hidden = !!form.elements.invite.value;

      var period = selectedPeriod() || 'monthly';
      var res = cmp[period] && cmp[period].available ? cmp[period].result : null;
      var how = $('#su-howprice', root);
      if (!res) { how.hidden = true; return; }
      var tb = $('tbody', how);
      tb.innerHTML = '';
      res.perMember.forEach(function (pm, i) {
        var tr = document.createElement('tr');
        tr.innerHTML = '<td></td><td></td>';
        tr.cells[0].textContent = (ps[i] ? ps[i].given : '') + ' · ' + (pm.cat === 'adult' ? U.adult_short : U.youth_short) + ' · ' + kindLabel(pm, period);
        tr.cells[1].textContent = F.money(pm.amount);
        tb.appendChild(tr);
      });
      var t = document.createElement('tr');
      t.innerHTML = '<td></td><td></td>';
      t.cells[0].textContent = U.total + ' ' + periods[period].unit;
      t.cells[1].textContent = F.money(res.total);
      tb.appendChild(t);
      var base = cmp[period].base;
      $('#su-baseline', root).textContent = periods[period].months > 1 && base ? fill(U.base_line, { amount: F.money(base) }) : '';
      how.hidden = false;
    }

    // ---- step 3: who pays ---------------------------------------------------
    function renderHolders() {
      var ps = people();
      $$('.su-card-h[data-slot]', root).forEach(function (card) {
        var s = card.getAttribute('data-slot');
        if (s === 'other') return;
        var p = ps.filter(function (x) { return String(x.slot) === s; })[0];
        var ok = p && p.cat === 'adult' && p.given;
        card.hidden = !ok;
        var input = $('input', card);
        if (!ok && input.checked) input.checked = false;
        if (ok) $('.su-card-name', card).textContent = nameOf(p);
      });
      var other = $('input[name=holder][value=other]', form).checked;
      $('#su-other', root).hidden = !other;
      var youth = ps.some(function (p) { return p.cat === 'youth'; });
      $('#su-guardian-box', root).hidden = !youth;
    }

    // ---- step 4: the review --------------------------------------------------
    // ---- how the fee is paid -----------------------------------------------
    function isCash() {
      var r = $('input[name=method]:checked', form);
      return !!r && r.value === 'cash';
    }
    // The cash rules show under the cards only when cash is chosen; without
    // JavaScript they are always there. Step 4's button and note follow.
    function syncMethod() {
      var cash = isCash();
      var cb = $('#su-cashbox', root);
      if (cb) cb.hidden = !cash;
      // "Stripe will ask for the card holder's name" means nothing for cash.
      var sn = $('#su-stripe-name', root);
      if (sn) sn.hidden = cash;
      var btn = $('.su-pay', form);
      var note = $('.su-paynote', form);
      if (btn && !btn.disabled) btn.textContent = btn.getAttribute(cash ? 'data-cash' : 'data-stripe');
      if (note) note.textContent = note.getAttribute(cash ? 'data-cash' : 'data-stripe');
    }

    function renderReview() {
      var ps = people();
      var period = selectedPeriod();
      var box = $('#su-summary', root);
      if (!period || !ps.length) { box.hidden = true; return; }
      var res;
      try { res = P.price({ period: period, members: members() }, CAT); } catch (e) { box.hidden = true; return; }
      var months = periods[period].months;
      var unit = periods[period].unit;
      $('.su-rv-unit', box).textContent = unit.charAt(0).toUpperCase() + unit.slice(1);
      var tb = $('tbody', box);
      tb.innerHTML = '';
      res.perMember.forEach(function (pm, i) {
        var tr = document.createElement('tr');
        tr.innerHTML = '<td></td><td></td><td></td><td></td>';
        tr.cells[0].textContent = nameOf(ps[i]);
        tr.cells[1].textContent = pm.cat === 'adult' ? U.adult_short : U.youth_short;
        tr.cells[2].textContent = kindLabel(pm, period);
        tr.cells[3].textContent = F.money(pm.amount);
        tb.appendChild(tr);
      });
      $('.su-rv-total', box).textContent = F.money(res.total);

      var holder = $('input[name=holder]:checked', form);
      var hname = '';
      if (holder && holder.value === 'other') hname = (form.elements.h_given.value + ' ' + form.elements.h_family.value).trim();
      else if (holder) {
        var hp = ps.filter(function (p) { return 'p' + p.slot === holder.value; })[0];
        hname = hp ? nameOf(hp) : '';
      }
      $('#su-holder-line', box).textContent = fill(U.holder_line, { name: hname, email: form.elements.email.value.trim() });

      var tl = $('#su-tl', box);
      tl.innerHTML = '';
      var invited = !!form.elements.invite.value;
      var cash = isCash();
      var anchor = P.nextAnchor(NOW, cash ? P.CASH.day : 5);
      var items = [];
      $('#su-method-line', box).textContent = fill(U.method_line, { method: cash ? U.method_cash : U.method_stripe });
      if (cash) {
        // Cash: nothing online. The first payment within CASH.firstDays, then
        // from the 1st to the 5th (CASH.by) of each period.
        var by = function (ms) { var d = P.madridDate(ms); return Date.UTC(d.y, d.m - 1, P.CASH.by, 12); };
        items.push(['now', '<b>' + U.tl_cash_now + '</b> · ' + U.tl_cash_now_sub]);
        if (!invited) {
          items.push(['now', '<b>' + fill(U.tl_cash_first, { by: F.date(NOW + P.CASH.firstDays * 86400000, false), amount: F.money(P.prorated(res.total, NOW, anchor, months)) }) + '</b> · ' + fill(U.tl_today_sub, { date: F.date(anchor, false) })]);
          items.push(['', '<b>' + F.date(P.withdrawalDeadline(NOW), false) + '</b> · ' + U.tl_withdraw]);
        }
        items.push(['', '<b>' + fill(U.tl_cash_full, { from: F.date(anchor, false), by: F.date(by(anchor), false), amount: F.money(res.total) }) + '</b> · ' + U.tl_first + (months > 1 && !invited ? '. ' + U.tl_keikogi : '')]);
        items.push(['', months === 1 ? fill(U.tl_cash_then, { amount: '<b>' + F.money(res.total) + '</b>' })
          : fill(U.tl_cash_then_q, { amount: '<b>' + F.money(res.total) + '</b>', months: F.list(P.chargeMonths(anchor, months).map(function (m) { return U.months[m]; })) })]);
      } else if (invited) {
        items.push(['now', '<b>' + U.tl_nothing + '</b>']);
      } else {
        var today = P.prorated(res.total, NOW, anchor, months);
        items.push(['now', '<b>' + fill(U.tl_today, { amount: F.money(today) }) + '</b> · ' + fill(U.tl_today_sub, { date: F.date(anchor, false) })]);
        items.push(['', '<b>' + F.date(P.withdrawalDeadline(NOW), false) + '</b> · ' + U.tl_withdraw]);
      }
      if (!invited && !cash) {
        items.push(['', '<b>' + F.date(anchor, false) + ', ' + F.money(res.total) + '</b> · ' + U.tl_first + (months > 1 ? '. ' + U.tl_keikogi : '')]);
        var then = months === 1 ? fill(U.tl_then, { amount: '<b>' + F.money(res.total) + '</b>' })
          : fill(U.tl_then_q, { amount: '<b>' + F.money(res.total) + '</b>', months: F.list(P.chargeMonths(anchor, months).map(function (m) { return U.months[m]; })) });
        items.push(['', then]);
      }
      items.forEach(function (it) {
        var li = document.createElement('li');
        if (it[0]) li.className = 'is-now';
        li.innerHTML = it[1];
        tl.appendChild(li);
      });
      box.hidden = false;
    }

    // ---- validation, mirroring the server's ---------------------------------
    // The server's rule, as a string so that older parsers do not trip on \p{}.
    var NAME = new RegExp("^[\\p{L}\\p{M}](?:[\\p{L}\\p{M}\\s'’.\\-・·]*[\\p{L}\\p{M}.])?$", 'u');
    var EMAIL = /^[^\s@<>()",;]+@[^\s@<>()",;]+\.[^\s@<>()",;]{2,}$/;
    var PHONE = /^\+?[0-9][0-9 ().-]{5,22}$/;
    function checkName(field, v, errs) {
      if (!v) errs.push(err(field, field.indexOf('family') > -1 ? 'family_required' : 'given_required'));
      else if (v.length > 80 || !NAME.test(v)) errs.push(err(field, 'name_invalid'));
    }
    function validateStep(n) {
      var errs = [];
      var ps = people();
      if (n === 1) {
        ps.forEach(function (p) {
          var f = 'p' + p.slot + '_';
          checkName(f + 'given', p.given, errs);
          checkName(f + 'family', p.family, errs);
          if (!p.cat) errs.push(err(f + 'cat', 'cat_required'));
          if (p.cat === 'youth') {
            if (!p.by || !p.bm) errs.push(err(f + 'by', 'bym_required'));
            else if (P.minAge(p.by, p.bm, NOW) > 16) errs.push(err(f + 'by', 'bym_too_old'));
          }
          if (p.rate === 'sc') {
            var sel = form.elements[f + 'venue'];
            var o = sel.selectedOptions[0];
            if (!p.venue) errs.push(err(f + 'venue', 'venue_required'));
            else if (p.cat && !o.getAttribute(p.cat === 'youth' ? 'data-youth' : 'data-adult')) errs.push(err(f + 'venue', 'sc_not_offered'));
            else if (p.cat === 'youth' && p.by && p.bm) {
              var min = +o.getAttribute('data-min') || 0;
              var age = P.minAge(p.by, p.bm, NOW);
              var older = (new Date(NOW).getUTCMonth() + 1 === p.bm) ? age + 1 : age;
              if (older < min) errs.push(err(f + 'venue', 'sc_min_age'));
            }
          }
        });
      }
      if (n === 2) {
        var period = selectedPeriod();
        if (!period) errs.push(err('period', 'period_required'));
        else if (period !== 'monthly' && ps.some(function (p) { return p.rate === 'sc'; })) errs.push(err('period', 'sc_monthly_only'));
      }
      if (n === 3) {
        var h = $('input[name=holder]:checked', form);
        if (!h) errs.push(err('holder', 'holder_required'));
        else if (h.value === 'other') {
          checkName('h_given', form.elements.h_given.value.trim(), errs);
          checkName('h_family', form.elements.h_family.value.trim(), errs);
        }
        var em = form.elements.email.value.trim();
        if (!em) errs.push(err('email', 'email_required'));
        else if (!EMAIL.test(em)) errs.push(err('email', 'email_invalid'));
        var ph = form.elements.phone.value.trim();
        if (ph && !PHONE.test(ph)) errs.push(err('phone', 'phone_invalid'));
        if (!form.elements.adult.checked) errs.push(err('adult', 'adult_required'));
        if (ps.some(function (p) { return p.cat === 'youth'; }) && !form.elements.guardian.checked) errs.push(err('guardian', 'guardian_required'));
      }
      if (n === 4) {
        if (!form.elements.terms.checked) errs.push(err('terms', 'terms_required'));
        if (!form.elements.early.checked) errs.push(err('early', 'early_required'));
      }
      return errs;
    }

    // ---- steps ---------------------------------------------------------------
    function show(n, push, quiet) {
      current = n;
      sections.forEach(function (s) { s.hidden = +s.getAttribute('data-step') !== n; });
      navItems.forEach(function (li) {
        var k = +li.getAttribute('data-step');
        li.classList.toggle('is-done', k < n);
        li.classList.toggle('is-current', k === n);
        if (k === n) li.setAttribute('aria-current', 'step'); else li.removeAttribute('aria-current');
      });
      if (n === 2) renderPeriods();
      if (n === 3) renderHolders();
      if (n === 4) renderReview();
      if (push !== false) {
        try { history.pushState({ suStep: n }, '', '#paso-' + n); } catch (e) {}
      }
      var h = $('#su-h-' + n, root);
      if (h && !quiet) { h.focus({ preventScroll: true }); h.scrollIntoView({ behavior: 'instant', block: 'start' }); }
      save();
    }
    function go(n) {
      // Forward only past steps that are valid; back is always allowed.
      for (var k = current; k < n; k++) {
        var errs = validateStep(k);
        if (errs.length) {
          if (k !== current) show(k);
          clearErrors(errorsBox, form);
          showErrors(errorsBox, errs);
          return;
        }
      }
      clearErrors(errorsBox, form);
      show(n);
    }
    root.addEventListener('click', function (e) {
      var b = e.target.closest('[data-go]');
      if (!b || !root.contains(b)) return;
      e.preventDefault();
      go(+b.getAttribute('data-go'));
    });
    window.addEventListener('popstate', function (e) {
      var n = e.state && e.state.suStep;
      if (n) show(n, false);
    });

    // ---- memory: sessionStorage only ---------------------------------------
    function serialize() {
      var o = {};
      $$('input, select, textarea', form).forEach(function (el) {
        if (!el.name || el.name === 'website') return;
        if (el.type === 'radio') { if (el.checked) o[el.name] = el.value; }
        else if (el.type === 'checkbox') { if (el.checked) o[el.name] = 'on'; }
        else if (el.value !== '') o[el.name] = el.value;
      });
      return o;
    }
    function save() { store(KEY, { v: serialize(), step: current }); }
    function restore(o) {
      Object.keys(o).forEach(function (k) {
        var el = form.elements[k];
        if (!el || k === 'website') return;
        if (el.length !== undefined && !el.tagName) {
          for (var i = 0; i < el.length; i++) el[i].checked = el[i].value === o[k];
        } else if (el.type === 'checkbox') {
          el.checked = o[k] === 'on';
        } else {
          el.value = o[k];
        }
      });
      wrappers.forEach(function (w) { w.hidden = !hasData(+w.getAttribute('data-slot')); });
    }

    var timer = null;
    function announce() {
      clearTimeout(timer);
      timer = setTimeout(function () {
        var period = selectedPeriod();
        if (!period) return;
        try {
          var r = P.price({ period: period, members: members() }, CAT);
          live.textContent = U.total + ': ' + F.money(r.total) + ' ' + periods[period].unit;
        } catch (e) { live.textContent = ''; }
      }, 700);
    }
    function changed(e) {
      var t = e && e.target;
      if (t && t.name) {
        var m = t.name.match(/^p(\d)_(cat|venue|rate)$/);
        if (m) updateVenue(+m[1]);
      }
      relabel();
      syncMethod();
      if (current === 2) renderPeriods();
      if (current === 3) renderHolders();
      if (current === 4) renderReview();
      save();
      announce();
    }
    form.addEventListener('input', changed);
    form.addEventListener('change', changed);

    // ---- arriving -------------------------------------------------------------
    var q = new URLSearchParams(location.search);
    var saved = load(KEY);
    if (saved && saved.v) restore(saved.v);
    var map = { mensual: 'monthly', trimestral: 'quarterly', anual: 'annual', monthly: 'monthly', quarterly: 'quarterly', annual: 'annual' };
    var per = map[(q.get('periodo') || q.get('period') || '').toLowerCase()];
    if (per && !selectedPeriod()) {
      var radio = $('input[name=period][value="' + per + '"]', form);
      if (radio) radio.checked = true;
    }
    var age = q.get('edad') || q.get('categoria') || '';
    if (age && !val(1, 'cat')) {
      var c = /^(16|joven|youth|nino|niño)$/i.test(age) ? 'youth' : 'adult';
      var r1 = $('input[name=p1_cat][value="' + c + '"]', form);
      if (r1) r1.checked = true;
    }
    var notice = $('#su-notice', root);
    function say(kind) {
      $$('p', notice).forEach(function (p) { p.textContent = p.getAttribute('data-' + kind); });
      notice.hidden = false;
    }
    if (q.get('invitacion')) {
      form.elements.invite.value = q.get('invitacion');
      say('invite');
    }
    if (q.toString()) {
      // The address bar is shared and bookmarked; the preselection has done its
      // job, and an invite token is nobody else's business.
      try { history.replaceState(null, '', location.pathname + (location.hash === '#volver' ? '#volver' : '')); } catch (e) {}
    }
    for (var s = 1; s <= data.maxPeople; s++) updateVenue(s);
    relabel();
    syncMethod();

    var start = 1;
    if (location.hash === '#volver' && saved) { say('cancel'); start = 4; }
    sections.forEach(function (sec) { sec.hidden = true; });
    show(start, false, start === 1);
    try { history.replaceState({ suStep: start }, '', location.pathname + '#paso-' + start); } catch (e) {}

    // ---- sending ----------------------------------------------------------------
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      clearErrors(errorsBox, form);
      for (var k = 1; k <= 4; k++) {
        var errs = validateStep(k);
        if (errs.length) { show(k); showErrors(errorsBox, errs); return; }
      }
      if (!form.elements.sid.value) form.elements.sid.value = randomId();
      var btn = $('.su-pay', form);
      var label = btn.textContent;
      btn.disabled = true;
      btn.textContent = btn.getAttribute('data-sending');
      var body = serialize();
      body.website = form.elements.website.value;
      fetch(data.endpoint + '/checkout', {
        method: 'POST',
        headers: { 'content-type': 'application/json', accept: 'application/json' },
        body: JSON.stringify(body)
      }).then(function (res) {
        return res.json().catch(function () { return {}; }).then(function (j) { return { ok: res.ok, j: j }; });
      }).then(function (r) {
        if (r.ok && r.j.url) { save(); location.assign(r.j.url); return; }
        btn.disabled = false;
        btn.textContent = label;
        var errs = (r.j.errors || [{ field: 'form', message: ERR.generic }]).map(function (x) {
          return { field: x.field === 'form' ? 'form' : x.field, message: x.message || ERR.generic };
        });
        var first = fieldEl(errs[0].field);
        var sec = first && first.closest ? first.closest('.su-step') : null;
        if (sec) show(+sec.getAttribute('data-step'));
        showErrors(errorsBox, errs);
      }).catch(function () {
        btn.disabled = false;
        btn.textContent = label;
        showErrors(errorsBox, [{ field: 'form', message: ERR.network }]);
      });
    });
  }

  // ===========================================================================
  // The withdrawal form, and the page after it
  // ===========================================================================
  function initWithdrawal(form) {
    var box = $('#wd-errors');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      clearErrors(box, form);
      var btn = $('.mb-confirm', form);
      var label = btn.textContent;
      btn.disabled = true;
      btn.textContent = btn.getAttribute('data-sending');
      var body = {};
      $$('input, textarea', form).forEach(function (el) { if (el.name) body[el.name] = el.value; });
      fetch(form.action, {
        method: 'POST',
        headers: { 'content-type': 'application/json', accept: 'application/json' },
        body: JSON.stringify(body)
      }).then(function (res) {
        return res.json().catch(function () { return {}; }).then(function (j) { return { ok: res.ok, j: j }; });
      }).then(function (r) {
        if (r.ok && r.j.receivedAt) {
          store('wd-at', { date: r.j.date, time: r.j.time });
          location.assign(form.getAttribute('data-ok'));
          return;
        }
        btn.disabled = false;
        btn.textContent = label;
        var errs = (r.j.errors || []).map(function (x) { return { field: x.field, message: x.message }; });
        if (!errs.length) errs = [{ field: 'form', message: form.getAttribute('data-generic') }];
        showErrors(box, errs);
      }).catch(function () {
        btn.disabled = false;
        btn.textContent = label;
        showErrors(box, [{ field: 'form', message: form.getAttribute('data-network') }]);
      });
    });
  }

  function showStamp(p) {
    var at = load('wd-at');
    if (!at) return;
    p.textContent = fill(p.getAttribute('data-tpl'), at);
    p.hidden = false;
    forget('wd-at');
  }

  // ---- go ---------------------------------------------------------------------
  var root = document.getElementById('su');
  if (root) initSignup(root);
  var wd = document.getElementById('wd-form');
  if (wd) initWithdrawal(wd);
  var stamp = document.getElementById('wd-stamp');
  if (stamp) showStamp(stamp);
  // The thank-you page: the answers have done their job.
  if (document.querySelector('.mb-thanks')) forget(KEY);
})();
