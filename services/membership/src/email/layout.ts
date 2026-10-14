// The one email layout, as approved in docs/mockups/inscripcion-correos.html:
// a black band with the name, a yellow rule, the body, and a footer with the
// association's legal line and the four links every member email carries.
//
// Email HTML is its own dialect: tables for layout, every style inline, no web
// fonts (Futura where the reader has it, then Trebuchet and Arial). Each block
// also produces its plain-text twin, sent alongside as text/plain.
import { E, SITE, esc, t, url, type Lang } from '../data.ts';

const C = {
  black: '#111314', yellow: '#FFF200', ink: '#3D4A50', mute: '#5A686E',
  paper: '#FBFAF7', hair: '#E3E3DF', ground: '#F1F1EE'
};
const BODY = "font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.6;color:" + C.ink;
const DISPLAY = "font-family:Futura,'Trebuchet MS',Arial,sans-serif;color:" + C.black;

export interface Block { html: string; text: string }

const ADMIN_FOOT = 'Aviso automático de las cuotas en línea. Sin teléfonos, fechas de nacimiento ni datos de pago, a propósito: el detalle está en Stripe.';

const text = (html: string) => html
  .replace(/<a [^>]*href="([^"]+)"[^>]*>(.*?)<\/a>/g, (_, href, label) => (label === href ? href : `${label} (${href})`))
  .replace(/<br\s*\/?>/g, '\n')
  .replace(/<[^>]+>/g, '')
  .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
  .replace(/&quot;/g, '"').replace(/&#39;/g, "'");

export const B = {
  h: (s: string): Block => ({
    html: `<h1 style="${DISPLAY};font-size:22px;line-height:1.25;font-weight:bold;margin:0 0 14px">${esc(s)}</h1>`,
    text: `${s}\n${'='.repeat(Math.min(s.length, 60))}`
  }),
  h4: (s: string): Block => ({
    html: `<h2 style="${DISPLAY};font-size:12px;letter-spacing:.12em;text-transform:uppercase;font-weight:bold;margin:22px 0 8px">${esc(s)}</h2>`,
    text: `\n${s.toUpperCase()}`
  }),
  // `html` is trusted template text with {placeholders} already filled from
  // escaped values; never pass it anything a person typed without esc().
  p: (html: string): Block => ({ html: `<p style="margin:0 0 14px">${html}</p>`, text: text(html) }),
  small: (html: string): Block => ({ html: `<p style="margin:0 0 14px;font-size:12px;line-height:1.55;color:${C.mute}">${html}</p>`, text: text(html) }),
  big: (s: string): Block => ({ html: `<p style="${DISPLAY};font-size:28px;font-weight:bold;margin:0 0 4px">${esc(s)}</p>`, text: s }),
  box: (html: string): Block => ({
    html: `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 16px"><tr><td style="background:${C.paper};border:1px solid ${C.hair};padding:12px 14px;font-size:14px">${html}</td></tr></table>`,
    text: text(html)
  }),
  button: (label: string, href: string): Block => ({
    html: `<table role="presentation" cellpadding="0" cellspacing="0" style="margin:4px 0 18px"><tr><td style="background:${C.black}"><a href="${esc(href)}" style="display:inline-block;padding:13px 20px;${DISPLAY};color:#ffffff;font-size:13px;font-weight:bold;letter-spacing:.07em;text-transform:uppercase;text-decoration:none">${esc(label)}</a></td></tr></table>`,
    text: `${label}: ${href}`
  }),
  // Rows of [label, value]; `total` draws the last one under a rule.
  table: (rows: [string, string][], total = false): Block => {
    const tr = rows.map(([a, b], i) => {
      const last = total && i === rows.length - 1;
      const st = last ? `border-top:2px solid ${C.black};font-weight:bold;color:${C.black}` : `border-bottom:1px solid ${C.hair}`;
      return `<tr><td style="padding:7px 4px;${st}">${a}</td><td style="padding:7px 4px;text-align:right;white-space:nowrap;${st}">${b}</td></tr>`;
    }).join('');
    return {
      html: `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="font-size:14px;margin:0 0 16px">${tr}</table>`,
      text: rows.map(([a, b]) => `  ${text(a)} ........ ${text(b)}`).join('\n')
    };
  },
  dates: (items: string[]): Block => ({
    html: `<table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 16px;border-left:2px solid ${C.black}">${items.map((i) => `<tr><td style="padding:0 0 8px 12px;font-size:14px">${i}</td></tr>`).join('')}</table>`,
    text: items.map((i) => `  - ${text(i)}`).join('\n')
  })
};

// `admin` emails go to the dojo's own mailbox: no member footer, no links a
// member would need, and a line saying what the email is.
export function render(lang: Lang, kind: string, blocks: Block[], origin: string, admin = false): { html: string; text: string } {
  const c = E.common;
  const links = [
    [t(c.link_members, lang), url('members', lang, true, origin)],
    [t(c.link_terms, lang), url('terms', lang, true, origin)],
    [t(c.link_privacy, lang), url('privacy', lang, true, origin)],
    [t(c.link_withdrawal, lang), url('withdrawal', lang, true, origin)]
  ];
  const org = lang === 'ja' ? SITE.org_ja : SITE.org;
  const legal = `${esc(org)} · CIF ${esc(SITE.cif)} · ${esc(SITE.address)}`;
  const html = `<!doctype html>
<html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><title>${esc(SITE.title)}</title></head>
<body style="margin:0;padding:0;background:${C.ground}">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:${C.ground}"><tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="width:100%;max-width:600px;background:#ffffff">
<tr><td style="background:${C.black};padding:16px 24px">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
  <td style="${DISPLAY};color:#ffffff;font-size:16px;font-weight:bold;letter-spacing:.04em;text-transform:uppercase">${esc(SITE.title)}</td>
  <td align="right" style="font-family:Arial,sans-serif;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#B9BEC0">${esc(kind)}</td>
  </tr></table></td></tr>
<tr><td style="height:4px;background:${C.yellow};font-size:0;line-height:0">&nbsp;</td></tr>
<tr><td style="padding:26px 24px 10px;${BODY}">
${blocks.map((b) => b.html).join('\n')}
</td></tr>
<tr><td style="border-top:1px solid ${C.hair};padding:16px 24px 20px;font-family:Arial,sans-serif;font-size:11px;line-height:1.55;color:${C.mute}">
${admin ? ADMIN_FOOT : `${legal}<br>${esc(t(c.footer, lang))}<br>
${links.map(([l, h]) => `<a href="${esc(h)}" style="color:${C.mute}">${esc(l)}</a>`).join(' · ')}`}
</td></tr>
</table></td></tr></table></body></html>`;

  const plain = [
    SITE.title.toUpperCase() + ' · ' + kind,
    '',
    ...blocks.map((b) => b.text),
    '',
    '--',
    ...(admin ? [ADMIN_FOOT] : [
      `${org} · CIF ${SITE.cif} · ${SITE.address}`,
      t(c.footer, lang),
      ...links.map(([l, h]) => `${l}: ${h}`)
    ])
  ].join('\n');
  return { html, text: plain };
}
