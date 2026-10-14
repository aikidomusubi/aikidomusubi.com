// npm run invite -- --mode test|live --email EMAIL --name "Full Name" [--lang es]
//                   [--first 2027-02] [--days 30] [--proration none|create_prorations] [--send]
// npm run invite -- --mode test|live --csv members.csv [--first 2027-02] [--send]
//
// An invite link for somebody who should not go through the public signup as
// it is: above all the existing members moving off the bank remittance in
// January 2027 (spec 8.4, 15).
//
// --first is the month of their FIRST Stripe charge, on the 5th. Pick the first
// month they will NOT be in the bank remittance, and nobody pays twice. Without
// it, the first charge is the next 5th after they accept.
//
// --csv reads columns email,name,lang[,first] with a header row. The file is
// personal data: keep it out of the repository and delete it when done.
//
// --send emails the invitation (template: "invite" in membership_emails.yml);
// otherwise the link is printed for you to send yourself.
import { readFileSync } from 'node:fs';
import { createInvite } from '../src/invite.ts';
import { isLang, url, type Lang } from '../src/data.ts';
import * as member from '../src/email/member.ts';
import { args, die, env, mode, vars } from './_cli.ts';

const a = args();
const m = mode(a);
const v = vars(m);
if (!v.INVITE_SIGNING_KEY) die('INVITE_SIGNING_KEY missing from the vars file — it must be the same value the Worker has');
const e = env(m, v, true);

function firstCharge(s: string | undefined): number | null {
  if (!s) return null;
  const mm = s.match(/^(\d{4})-(\d{2})$/);
  if (!mm) die(`--first must look like 2027-02, not ${s}`);
  const at = Date.UTC(Number(mm[1]), Number(mm[2]) - 1, 5, 8, 0, 0);
  if (at < Date.now() + 3600_000) die(`${s}: the first charge has to be in the future`);
  return at;
}

const rows: { email: string; name: string; lang: Lang; first: number | null }[] = [];
if (typeof a.csv === 'string') {
  const lines = readFileSync(a.csv, 'utf8').split(/\r?\n/).filter((l) => l.trim());
  const head = lines.shift()!.split(',').map((h) => h.trim().toLowerCase());
  for (const line of lines) {
    const cells = line.split(',').map((c) => c.trim());
    const get = (k: string) => cells[head.indexOf(k)] ?? '';
    rows.push({ email: get('email'), name: get('name'), lang: isLang(get('lang')) ? (get('lang') as Lang) : 'es',
      first: firstCharge(get('first') || (typeof a.first === 'string' ? a.first : undefined)) });
  }
} else {
  if (typeof a.email !== 'string' || typeof a.name !== 'string') die('--email and --name are required (or --csv)');
  rows.push({ email: a.email, name: a.name, lang: isLang(a.lang) ? (a.lang as Lang) : 'es',
    first: firstCharge(typeof a.first === 'string' ? a.first : undefined) });
}

const days = Number(typeof a.days === 'string' ? a.days : 30);
const proration = a.proration === 'create_prorations' ? 'create_prorations' : 'none';
for (const r of rows) {
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(r.email)) { console.log(`  skipped: "${r.email}" is not an email`); continue; }
  const { token, expires } = await createInvite(e, { email: r.email, name: r.name, lang: r.lang, proration, anchor: r.first, days });
  const link = `${url('signup', r.lang)}?invitacion=${encodeURIComponent(token)}`;
  if (a.send) {
    await member.invite({ env: e, lang: r.lang, to: r.email, toName: r.name, hello: r.name.split(' ')[0] }, { link, expiresMs: expires });
    console.log(`  sent    ${r.name} <${r.email}>${r.first ? ` · first charge ${new Date(r.first).toISOString().slice(0, 10)}` : ''}`);
  } else {
    console.log(`  ${r.name} <${r.email}>\n    ${link}`);
  }
}
