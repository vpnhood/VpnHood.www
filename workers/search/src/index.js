// The site search API behind www.vpnhood.com/search/ (assets/js/search.js), served at
// search.vpnhood.com. Each search Google answers is billed (Vertex AI Search, Enterprise
// edition), so every request passes, in order:
//   1. a Cloudflare Turnstile token, single-use, for the search action on our hostname;
//   2. a day's cache per language and query, which answers repeats for free;
//   3. the SearchBudget Durable Object: a per-visitor limit per minute and a global daily
//      cap (DAILY_CAP), the only hard limit on what Google can bill; the first search the
//      cap turns away each day emails ALERT_TO;
//   4. Google's searchLite with an API key restricted to the Discovery Engine API.
// The page posts {q, lang, token} as text/plain, which keeps it a simple CORS request with
// no preflight, and gets {results: [{link, title, snippet}]} or a bare error status. Results
// are kept to the page's own language tree. See .docs/components.md.
import { DurableObject } from 'cloudflare:workers';

const SITE = 'https://www.vpnhood.com';
// The 12 prefixed trees (_data/i18n/<lang>/); English is unprefixed.
const PREFIXED = ['ar', 'de', 'es', 'fa', 'fr', 'hi', 'it', 'pt', 'pt-BR', 'ru', 'tr', 'zh'];
const LANGS = ['en', ...PREFIXED];

export default {
  async fetch(request, env, ctx) {
    const origin = request.headers.get('Origin') || '';
    const cors = env.ALLOWED_ORIGINS.split(',').includes(origin)
      ? { 'Access-Control-Allow-Origin': origin, 'Vary': 'Origin' }
      : { 'Vary': 'Origin' };
    if (request.method === 'OPTIONS')
      return new Response(null, { status: 204, headers: { ...cors, 'Access-Control-Allow-Methods': 'POST', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '86400' } });
    if (request.method !== 'POST') return reply(405, cors);

    let input;
    try { input = JSON.parse(await request.text()); } catch { return reply(400, cors); }
    const query = String(input.q || '').trim().replace(/\s+/g, ' ').slice(0, 200);
    const lang = LANGS.includes(input.lang) ? input.lang : '';
    if (!query || !lang || typeof input.token !== 'string') return reply(400, cors);

    const ip = request.headers.get('CF-Connecting-IP') || '';
    if (!(await turnstilePassed(env, input.token, ip))) return reply(403, cors);

    // The version changes whenever the answers do (another app, another format), or the
    // cache would go on serving the old ones for a day
    const cacheKey = new Request(`https://search.vpnhood.com/cache/v3/${lang}?q=${encodeURIComponent(query.toLowerCase())}`);
    const cached = await caches.default.match(cacheKey);
    if (cached) return reply(200, cors, await cached.text());

    const budget = env.BUDGET.get(env.BUDGET.idFromName('global'));
    const taken = await budget.take(ip, Number(env.DAILY_CAP), Number(env.PER_VISITOR_PER_MINUTE));
    if (taken.alert) ctx.waitUntil(sendCapAlert(env, taken.day));
    if (taken.verdict !== 'ok') return reply(taken.verdict === 'visitor' ? 429 : 503, cors);

    let results;
    try {
      results = await search(env, query, lang);
    } catch (e) {
      console.error(e.message);
      return reply(502, cors);
    }
    const body = JSON.stringify({ results });
    ctx.waitUntil(caches.default.put(cacheKey, new Response(body, { headers: { 'Cache-Control': 'public, max-age=86400' } })));
    return reply(200, cors, body);
  }
};

function reply(status, cors, body = null) {
  const headers = { ...cors, 'Cache-Control': 'no-store' };
  if (body) headers['Content-Type'] = 'application/json; charset=utf-8';
  return new Response(body, { status, headers });
}

async function turnstilePassed(env, token, ip) {
  try {
    const response = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST',
      body: new URLSearchParams({ secret: env.TURNSTILE_SECRET, response: token, remoteip: ip }),
      signal: AbortSignal.timeout(10000)
    });
    const result = await response.json();
    // A test key's answer has no action and the hostname example.com (.dev.vars)
    return result.success === true
      && (result.action || '') === env.TURNSTILE_ACTION
      && env.TURNSTILE_HOSTNAMES.split(',').includes(result.hostname);
  } catch {
    return false;
  }
}

// A page belongs to the tree whose prefix starts its path; English is every path that
// starts with no other language's prefix, the legal pages included.
function inTree(link, lang) {
  let url;
  try { url = new URL(link); } catch { return false; }
  if (url.origin !== SITE) return false;
  const first = url.pathname.split('/')[1];
  return lang === 'en' ? !PREFIXED.includes(first) : first === lang;
}

async function search(env, query, lang) {
  const request = {
    servingConfig: env.SERVING_CONFIG,
    query,
    pageSize: 25,
    languageCode: lang === 'zh' ? 'zh-CN' : lang,
    userPseudoId: crypto.randomUUID(),
    // The app's one store holds all 13 trees: a language is its folder, and English, which
    // has none, every page outside the 12 folders
    filter: lang === 'en'
      ? PREFIXED.map(other => `NOT siteSearch:"${SITE}/${other}/*"`).join(' AND ')
      : `siteSearch:"${SITE}/${lang}/*"`,
    contentSearchSpec: { snippetSpec: { returnSnippet: true } },
    spellCorrectionSpec: { mode: 'AUTO' },
    queryExpansionSpec: { condition: 'AUTO' }
  };
  const response = await fetch(`https://discoveryengine.googleapis.com/v1/${env.SERVING_CONFIG}:searchLite?key=${env.GOOGLE_API_KEY}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
    signal: AbortSignal.timeout(10000)
  });
  if (!response.ok) throw new Error(`Google answered ${response.status}: ${(await response.text()).slice(0, 500)}`);
  const data = await response.json();
  return (data.results || [])
    .map(result => result.document?.derivedStructData || {})
    .filter(page => inTree(page.link, lang))
    .slice(0, 10)
    .map(page => ({
      link: page.link,
      title: page.title || '',
      // HTML already: the words that matched in <b>, the rest escaped
      snippet: ((page.snippets || [])[0] || {}).snippet || ''
    }));
}

// The day's one email, sent when DAILY_CAP first turns a search away. ALERT_EMAIL can only
// reach the verified address in its binding; it sends through Email Routing on
// alerts.vpnhood.com, which leaves vpnhood.com's own mail alone.
async function sendCapAlert(env, day) {
  try {
    await env.ALERT_EMAIL.send({
      from: { email: env.ALERT_FROM, name: 'VpnHood site search' },
      to: env.ALERT_TO,
      subject: `Site search reached its daily cap of ${env.DAILY_CAP} searches`,
      text: [
        `www.vpnhood.com/search/ answered ${env.DAILY_CAP} searches on ${day} (UTC), its daily cap,`,
        'and has just turned the next one away. Until 00:00 UTC every visitor sees',
        '"Search isn\'t available right now".',
        '',
        'If this is real traffic, raise DAILY_CAP in workers/search/wrangler.jsonc and deploy',
        '(.docs/build-and-deploy.md). Google answers 10,000 searches a month for free, then',
        'bills $4 per 1,000. If it looks like abuse, check the vpnhood-search Worker in Cloudflare.'
      ].join('\n')
    });
  } catch (e) {
    console.error(`Alert email failed: ${e.code || ''} ${e.message}`);
  }
}

// One instance for the whole Worker, so its counts are exact: searches per visitor (by IP)
// in the current minute, held in memory, and searches per UTC day, in SQLite, with whether
// that day's cap alert has gone out.
export class SearchBudget extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.minute = 0;
    this.visitors = new Map();
    ctx.storage.sql.exec('CREATE TABLE IF NOT EXISTS days (day TEXT PRIMARY KEY, count INTEGER NOT NULL, alerted INTEGER NOT NULL DEFAULT 0)');
  }

  // { verdict: 'ok' | 'visitor' | 'cap', day, alert }: alert is true once a day, for the
  // first search the cap turns away
  take(ip, dailyCap, perVisitorPerMinute) {
    const now = Date.now();
    const minute = Math.floor(now / 60000);
    if (minute !== this.minute) {
      this.minute = minute;
      this.visitors.clear();
    }
    const day = new Date(now).toISOString().slice(0, 10);
    const visitor = this.visitors.get(ip) || 0;
    if (visitor >= perVisitorPerMinute) return { verdict: 'visitor', day };

    const sql = this.ctx.storage.sql;
    sql.exec('INSERT OR IGNORE INTO days (day, count) VALUES (?, 0)', day);
    const row = sql.exec('SELECT count, alerted FROM days WHERE day = ?', day).toArray()[0];
    if (row.count >= dailyCap) {
      if (row.alerted) return { verdict: 'cap', day };
      sql.exec('UPDATE days SET alerted = 1 WHERE day = ?', day);
      return { verdict: 'cap', day, alert: true };
    }

    sql.exec('UPDATE days SET count = count + 1 WHERE day = ?', day);
    this.visitors.set(ip, visitor + 1);
    return { verdict: 'ok', day };
  }
}
