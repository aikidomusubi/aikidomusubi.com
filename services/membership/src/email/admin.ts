// What the dojo receives at admin@, as approved in
// docs/mockups/inscripcion-admin.html. Spanish only: one reader.
//
// Spec 8.1: names, plan, first charge, flags, a link to Stripe, and nothing
// else — no phone numbers, no dates of birth, no payment details.
import type { Env } from '../env.ts';
import { esc } from '../data.ts';
import { B, render, type Block } from './layout.ts';
import { send } from './send.ts';

export interface Todo { title: string; sub?: string; action?: { label: string; href: string } }

// A to-do list: one row per thing to do, with a button where one press does it.
export function todo(items: Todo[]): Block {
  const rows = items.map((i) => `<tr><td style="padding:9px 10px;border:1px solid #E3E3DF;border-left:4px solid #ae5224;font-size:14px;color:#111314">
${esc(i.title)}${i.sub ? `<br><span style="font-size:12px;color:#5A686E">${esc(i.sub)}</span>` : ''}</td>
<td style="padding:9px 10px;border:1px solid #E3E3DF;border-left:0;text-align:right;white-space:nowrap">${i.action
    ? `<a href="${esc(i.action.href)}" style="display:inline-block;padding:7px 10px;background:#FFF200;border:1.5px solid #474400;color:#111314;font-family:Futura,'Trebuchet MS',Arial,sans-serif;font-size:11px;font-weight:bold;letter-spacing:.06em;text-transform:uppercase;text-decoration:none">${esc(i.action.label)}</a>`
    : ''}</td></tr>`).join('');
  return {
    html: `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:separate;border-spacing:0 6px;margin:0 0 14px">${rows}</table>`,
    text: items.map((i) => `  [ ] ${i.title}${i.sub ? ` — ${i.sub}` : ''}${i.action ? `\n      ${i.action.label}: ${i.action.href}` : ''}`).join('\n')
  };
}

export async function admin(env: Env, subject: string, kind: string, blocks: Block[], tag: string) {
  const { html, text } = render('es', kind, blocks, env.SITE_ORIGIN, true);
  await send(env, { to: env.ADMIN_EMAIL, subject, html, text, tag: `admin_${tag}` });
}

export const dashboard = (env: Env, path: string) =>
  `https://dashboard.stripe.com/${env.ENVIRONMENT === 'live' ? '' : 'test/'}${path}`;

export { B };
