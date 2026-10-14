// Types for the shared pricing engine, which is plain JavaScript in
// scripts/pricing.js so that the signup page can load it as it is. The Worker
// imports the ES-module copy gen-catalog.mjs makes of that same file.
// @ts-ignore — generated, untyped
import PricingJs from './generated/pricing.mjs';

export type Cat = 'adult' | 'youth';
export type Rate = 'general' | 'sc';
export type Kind = 'full' | 'family' | 'sc';
export type PeriodId = 'monthly' | 'quarterly' | 'annual';

export interface Member { cat: Cat; rate: Rate; venue?: string | null }

export interface PerMember {
  slot: number; cat: Cat; rate: Rate; venue: string | null;
  kind: Kind; amount: number; lookupKey: string;
}
export interface LineItem { lookupKey: string; quantity: number; unitAmount: number }
export interface PriceResult {
  period: PeriodId; months: number; perMember: PerMember[]; lineItems: LineItem[]; total: number;
}
export interface Catalog {
  version: string; effectiveFrom: string | null;
  periods: Record<string, { months: number }>;
  prices: Record<string, Record<string, { fee: number; base: number }>>;
  family: number;
  sc: Record<string, { adult?: number; youth?: number; minAge: number }>;
}
export interface Compare {
  [period: string]: { available: boolean; total?: number; months?: number; base?: number; saving?: number; reason?: string; result?: PriceResult };
}

interface PricingApi {
  PricingError: new (code: string, detail?: string) => Error & { code: string; detail: string | null };
  MAX_PEOPLE: number;
  catalog(fees: unknown): Catalog;
  price(sel: { period: string; members: Member[] }, cat: Catalog): PriceResult;
  compare(members: Member[], cat: Catalog): Compare;
  lookupKey(cat: Catalog, member: Member & { cat: Cat }, period: string, kind: Kind): string;
  nextAnchor(nowMs: number): number;
  addMonths(ms: number, n: number): number;
  prorated(total: number, nowMs: number, anchorMs: number, months: number): number;
  chargeMonths(anchorMs: number, months: number): number[];
  minAge(birthYear: number, birthMonth: number, nowMs: number): number;
  turns17(birthYear: number, birthMonth: number): number;
  madridDate(ms: number): { y: number; m: number; d: number };
  withdrawalDeadline(signupMs: number): number;
}

export const Pricing = PricingJs as PricingApi;

export function isPricingError(e: unknown): e is Error & { code: string; detail: string | null } {
  return e instanceof Error && e.name === 'PricingError';
}
