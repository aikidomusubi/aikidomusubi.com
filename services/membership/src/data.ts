// The site's own data, as bundled by scripts/gen-catalog.mjs, and the small
// helpers that turn it into words: one string per language, money, dates.
import data from './generated/data.json';
import { Pricing, type Catalog } from './pricing.ts';

export type Lang = 'es' | 'ca' | 'en' | 'ja';
export const LANGS: Lang[] = ['es', 'ca', 'en', 'ja'];
export const isLang = (x: unknown): x is Lang => typeof x === 'string' && (LANGS as string[]).includes(x);

type I18n = Partial<Record<Lang, string>>;
// The data files are loosely typed by nature; these are the shapes read here.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const FEES = data.fees as any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const M = data.membership as any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const E = data.emails as any;
export const VENUES = data.venues as Record<string, I18n>;
export const SITE = data.site as { title: string; org: string; org_ja: string; cif: string; address: string };
export const CATALOG: Catalog = Pricing.catalog(FEES);

// One string in one language, falling back to Spanish, with {placeholders}.
// {org}, {title} and {address} are always available: the organisation's names
// come from _config.yml and _data/footer.yml and are never typed in a string.
export function t(map: I18n | undefined, lang: Lang, vars: Record<string, string | number> = {}): string {
  const s = (map && (map[lang] ?? map.es)) ?? '';
  const all: Record<string, string | number> = {
    org: lang === 'ja' ? SITE.org_ja : SITE.org, title: SITE.title, address: SITE.address, ...vars
  };
  return s.replace(/\{(\w+)\}/g, (m, k) => (k in all ? String(all[k]) : m));
}

export function url(kind: string, lang: Lang, absolute = true, origin = 'https://aikidomusubi.com'): string {
  const path = t(M.urls[kind], lang);
  return absolute ? origin + path : path;
}

const NBSP = ' ';

// 77 → "77 €", 30.99 → "30,99 €"; Japanese copy says ユーロ.
export function money(euros: number, lang: Lang): string {
  const whole = Math.abs(euros - Math.round(euros)) < 0.005;
  let n = whole ? String(Math.round(euros)) : euros.toFixed(2);
  if (!whole && (lang === 'es' || lang === 'ca')) n = n.replace('.', ',');
  return lang === 'ja' ? `${n}ユーロ` : `${n}${NBSP}€`;
}

export function madrid(ms: number) {
  const parts: Record<string, string> = {};
  new Intl.DateTimeFormat('en-GB', {
    timeZone: 'Europe/Madrid', year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', hour12: false
  }).formatToParts(new Date(ms)).forEach((p) => { parts[p.type] = p.value; });
  return { y: +parts.year, m: +parts.month, d: +parts.day, time: `${parts.hour}:${parts.minute}` };
}

// Catalan elides "de" before a vowel: "5 d'abril", "5 d'agost", "5 d'octubre".
function ofMonth(lang: Lang, name: string) {
  if (lang === 'ca' && /^[aeiouàèéíòóú]/i.test(name)) return `d'${name}`;
  return lang === 'es' || lang === 'ca' ? `de ${name}` : name;
}

export function date(ms: number, lang: Lang, withYear = true): string {
  const { y, m, d } = madrid(ms);
  const name = M.ui.months[lang]?.[m - 1] ?? M.ui.months.es[m - 1];
  if (lang === 'ja') return withYear ? `${y}年${m}月${d}日` : `${m}月${d}日`;
  if (lang === 'en') return withYear ? `${d} ${name} ${y}` : `${d} ${name}`;
  return withYear ? `${d} ${ofMonth(lang, name)} de ${y}` : `${d} ${ofMonth(lang, name)}`;
}

export const time = (ms: number) => madrid(ms).time;

export function list(items: string[], lang: Lang): string {
  if (lang === 'ja') return items.join('・');
  if (items.length < 2) return items.join('');
  const and = lang === 'en' ? 'and' : lang === 'ca' ? 'i' : 'y';
  return `${items.slice(0, -1).join(', ')} ${and} ${items[items.length - 1]}`;
}

export function monthNames(indices: number[], lang: Lang): string {
  return list(indices.map((i) => M.ui.months[lang]?.[i] ?? M.ui.months.es[i]), lang);
}

export function periodName(id: string, lang: Lang) {
  const p = FEES.periods.find((x: { id: string }) => x.id === id);
  return p ? t(p.name, lang).toLowerCase() : id;
}
export function periodUnit(id: string, lang: Lang) {
  const p = FEES.periods.find((x: { id: string }) => x.id === id);
  return p ? t(p.unit, lang) : '';
}
export const venueName = (id: string | null | undefined, lang: Lang) => (id ? t(VENUES[id], lang) || id : '');

export function esc(s: unknown): string {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!));
}

export const isoDay = (ms: number) => {
  const { y, m, d } = madrid(ms);
  return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
};
