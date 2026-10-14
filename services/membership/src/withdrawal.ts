// POST /withdrawal — the online withdrawal function (Directive (EU) 2023/2673,
// from 19 June 2026; spec 11.3).
//
// The person states their name, the email they signed up with and a sentence;
// they get an acknowledgement with the content, the date and the time; the
// dojo gets the request with a suggested refund. The dojo then cancels and
// refunds within 14 days. Nothing is cancelled automatically: a withdrawal
// from an address that matches no membership still reaches the dojo, which
// is where a person who typed the wrong email needs it to go.
import type { Env } from './env.ts';
import { M, date, esc, isLang, money, time, type Lang, url } from './data.ts';
import { fromSite, json, limited, log, readBody, redirect, wantsJson, page } from './http.ts';
import { stripe } from './stripe.ts';
import { refundFor } from './refund.ts';
import * as member from './email/member.ts';
import { admin, dashboard, B } from './email/admin.ts';
import type Stripe from 'stripe';

const EMAIL = /^[^\s@<>()",;]+@[^\s@<>()",;]+\.[^\s@<>()",;]{2,}$/;
const KNOWN = new Set(['lang', 'name', 'email', 'statement', 'website']);

export async function withdrawal(req: Request, env: Env, now = Date.now()): Promise<Response> {
  if (!fromSite(env, req)) return json(env, req, { error: 'origin' }, 403);
  if (await limited(env, req, 'withdrawal')) return json(env, req, { error: 'rate_limited' }, 429);
  const body = await readBody(req);
  if (!body || Object.keys(body).some((k) => !KNOWN.has(k))) return json(env, req, { error: 'generic' }, 400);
  const lang: Lang = isLang(body.lang) ? body.lang : 'es';
  if (body.website) return json(env, req, { error: 'generic' }, 422);

  const name = (body.name ?? '').replace(/\s+/g, ' ').trim().slice(0, 160);
  const email = (body.email ?? '').trim().toLowerCase();
  const statement = (body.statement ?? '').replace(/\s+/g, ' ').trim().slice(0, 1500);
  const errors: { field: string; code: string }[] = [];
  if (!name) errors.push({ field: 'name', code: 'given_required' });
  if (!EMAIL.test(email) || email.length > 254) errors.push({ field: 'email', code: email ? 'email_invalid' : 'email_required' });
  if (!statement) errors.push({ field: 'statement', code: 'statement_required' });
  if (errors.length) {
    if (wantsJson(req)) {
      return json(env, req, { errors: errors.map((e) => ({ ...e, message: M.errors[e.code]?.[lang] ?? '' })) }, 422);
    }
    return page(lang, M.errors.error_page_title[lang], `<h1>${esc(M.errors.error_page_title[lang])}</h1>
<div class="err"><ul>${errors.map((e) => `<li>${esc(M.errors[e.code]?.[lang] ?? '')}</li>`).join('')}</ul></div>
<p>${esc(M.errors.error_page_back[lang])}</p>`, 422);
  }

  // Which membership, if any. Read-only: the dojo decides.
  let sub: Stripe.Subscription | null = null;
  let refund: Awaited<ReturnType<typeof refundFor>> | null = null;
  try {
    const st = stripe(env);
    const customers = await st.customers.list({ email, limit: 5 });
    for (const c of customers.data) {
      const subs = await st.subscriptions.list({ customer: c.id, status: 'all', limit: 10 });
      sub = subs.data.find((s) => ['active', 'trialing', 'past_due', 'incomplete'].includes(s.status)) ?? null;
      if (sub) break;
    }
    if (sub) refund = await refundFor(st, sub.id, now);
  } catch (e) {
    log({ route: 'withdrawal', outcome: 'lookup_error', error: (e as Error).message?.slice(0, 120) });
  }

  const refundBy = now + 14 * 86400000;
  // The acknowledgement echoes the statement only to the address of a real
  // membership: otherwise this form could post any text to any inbox.
  await member.withdrawalAck({ env, lang, to: email, toName: name, hello: name.split(' ')[0] }, {
    atMs: now, name, email, statement: sub ? statement : '—', refundBy
  });

  const withinDays = sub ? Math.floor((now - sub.created * 1000) / 86400000) : null;
  await admin(env, `Desistimiento: ${name}${sub ? '' : ' (correo sin cuota)'}`, 'Desistimiento', [
    B.h('Solicitud de desistimiento'),
    B.box(`${date(now, 'es')}, ${time(now)}<br>${esc(name)} · ${esc(email)}<br>«${esc(statement)}»`),
    B.p(sub
      ? `Cuota encontrada, creada hace ${withinDays} días${withinDays !== null && withinDays > 14 ? ' — <b>fuera del plazo de 14 días</b>: es una baja, no un desistimiento' : ''}. Devolución sugerida: <b>${money(refund?.total ?? 0, 'es')}</b> (lo pagado menos los días transcurridos). Hay que cancelarla y devolver antes del ${date(refundBy, 'es')}.`
      : 'No hay ninguna cuota activa con ese correo. Puede que se inscribiera con otro: contesta a esta persona.'),
    ...(sub ? [B.button('Abrir en Stripe', dashboard(env, `subscriptions/${sub.id}`))] : [])
  ], 'withdrawal');
  log({ route: 'withdrawal', outcome: sub ? 'matched' : 'unmatched' });

  if (wantsJson(req)) return json(env, req, { receivedAt: now, date: date(now, lang), time: time(now) });
  return redirect(url('withdrawal_ok', lang, true, env.SITE_ORIGIN));
}
