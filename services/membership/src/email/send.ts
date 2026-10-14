// Sending email, through Brevo's transactional API (decided 14 October 2026:
// French, EU-hosted, a DPA, a plain HTTP API a Worker can call).
//
// The provider is this one function. Changing provider is rewriting it and
// nothing else.
import type { Env } from '../env.ts';
import { SITE } from '../data.ts';

export interface Message {
  to: string;
  toName?: string;
  subject: string;
  html: string;
  text: string;
  tag: string;               // which template, for Brevo's statistics; never personal
  replyTo?: string;
}

// Tests collect messages here instead of sending them.
export const outbox: Message[] = [];

export async function send(env: Env, msg: Message): Promise<void> {
  // In test mode every member email can be redirected to one inbox, so a run
  // against Stripe's test clock never writes to a real person.
  const to = env.EMAIL_OVERRIDE && env.ENVIRONMENT !== 'live' ? env.EMAIL_OVERRIDE : msg.to;

  if (env.ENVIRONMENT === 'dev' || !env.BREVO_API_KEY) {
    outbox.push({ ...msg, to });
    if (env.ENVIRONMENT !== 'dev' && !env.BREVO_API_KEY) {
      console.log(JSON.stringify({ level: 'warn', msg: 'email not sent: no BREVO_API_KEY', tag: msg.tag }));
    }
    return;
  }

  const res = await fetch('https://api.brevo.com/v3/smtp/email', {
    method: 'POST',
    headers: { 'api-key': env.BREVO_API_KEY, 'content-type': 'application/json', accept: 'application/json' },
    body: JSON.stringify({
      sender: { name: SITE.title, email: env.FROM_EMAIL },
      to: [{ email: to, ...(msg.toName ? { name: msg.toName } : {}) }],
      replyTo: { email: msg.replyTo ?? env.REPLY_TO },
      subject: msg.subject,
      htmlContent: msg.html,
      textContent: msg.text,
      tags: [msg.tag]
    })
  });
  if (!res.ok) {
    // The status only: Brevo's error body can echo the recipient.
    throw new Error(`email provider answered ${res.status} for ${msg.tag}`);
  }
}
