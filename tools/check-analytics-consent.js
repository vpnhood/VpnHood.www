// Check what the website sends to Google and keeps in cookies, for each kind of visitor.
//
// The site has no ads and its privacy notice names none, so the Tag Manager loader in
// _includes/header.html sets Consent Mode to "analytics granted, ads denied" for every visitor;
// without that default Google also sends its ad signals to stats.g.doubleclick.net. A second
// GA4 tag in the container would count every visit twice. And the notice promises that
// declining removes the Google Analytics cookies, which assets/js/consent-banner.js does.
//
// Four visitors, in a headless browser:
// - outside the consent regions: one GA4 page view, no ad signal;
// - inside them, no choice yet: the banner, and nothing sent;
// - inside them, presses Accept on the banner: one page view, no ad signal;
// - then Decline under "Cookie settings": the page reloads with no _ga* cookie left.
//
// Every request to Google Analytics or DoubleClick is caught and aborted, so nothing reaches
// the GA4 property. Tag Manager loads only in a production build, so point it at the live
// site or at a local `JEKYLL_ENV=production` build.
//
// Usage: node tools/check-analytics-consent.js [base-url] [path ...]
//   default: https://www.vpnhood.com  /  /free-vpn/  /fa/free-vpn/download/
// Exits 1 when any check fails.
const { chromium } = require('playwright');

const MEASUREMENT_ID = 'G-DWH7NV15XQ';
const GOOGLE_HIT = /google-analytics\.com\/(g|j)\/collect|analytics\.google\.com\/g\/collect|doubleclick\.net|googleadservices/;
const base = (process.argv[2] || 'https://www.vpnhood.com').replace(/\/$/, '');
const paths = process.argv.length > 3 ? process.argv.slice(3) : ['/', '/free-vpn/', '/fa/free-vpn/download/'];
const wait = ms => new Promise(r => setTimeout(r, ms));
const url = (path, geo) => `${base}${path}${path.includes('?') ? '&' : '?'}geo=${geo}`;
let failed = false;

function report(ok, text) {
  failed = failed || !ok;
  console.log(`${ok ? 'ok  ' : 'FAIL'} ${text}`);
}

async function visitor(browser) {
  const ctx = await browser.newContext();
  const hits = [];
  await ctx.route(GOOGLE_HIT, route => {
    const u = new URL(route.request().url());
    const lines = (route.request().postData() || '').split('\n');
    const events = [u.searchParams.get('en'), ...lines.map(l => new URLSearchParams(l).get('en'))].filter(Boolean);
    hits.push({ host: u.host, tid: u.searchParams.get('tid'), events });
    return route.abort();
  });
  const count = () => ({
    pageViews: hits.filter(h => h.tid === MEASUREMENT_ID && h.events.includes('page_view')).length,
    adSignals: hits.filter(h => /doubleclick|googleadservices/.test(h.host)).length,
  });
  return { ctx, page: await ctx.newPage(), hits, count };
}

const clickConsent = (page, choice) =>
  page.evaluate(c => document.querySelector(`#vhConsent [data-vh-consent="${c}"]`).click(), choice);

(async () => {
  const browser = await chromium.launch();
  for (const path of paths) {
    // GA4 sends the page view a few seconds after Tag Manager starts.
    let v = await visitor(browser);
    await v.page.goto(url(path, 'US'), { waitUntil: 'load' });
    await wait(8000);
    let c = v.count();
    report(c.pageViews === 1 && c.adSignals === 0, `${path} outside the consent regions: ${c.pageViews} page view(s), ${c.adSignals} ad signal(s)`);
    await v.ctx.close();

    v = await visitor(browser);
    await v.page.goto(url(path, 'DE'), { waitUntil: 'load' });
    await wait(4000);
    const shown = await v.page.evaluate(() => !document.getElementById('vhConsent').hidden);
    report(shown && v.hits.length === 0, `${path} consent region, no choice yet: banner ${shown ? 'shown' : 'NOT shown'}, ${v.hits.length} hit(s)`);
    await clickConsent(v.page, 'granted');
    await wait(8000);
    c = v.count();
    report(c.pageViews === 1 && c.adSignals === 0, `${path} consent region, Accept: ${c.pageViews} page view(s), ${c.adSignals} ad signal(s)`);
    if (path === paths[0]) {
      v.hits.length = 0;
      await v.page.evaluate(() => document.getElementById('vhConsentSettings').click());
      await Promise.all([v.page.waitForNavigation({ waitUntil: 'load' }), clickConsent(v.page, 'denied')]);
      await wait(4000);
      const left = (await v.ctx.cookies()).filter(k => k.name.startsWith('_ga')).map(k => k.name);
      report(left.length === 0 && v.hits.length === 0, `${path} consent region, Decline after Accept: ${left.length ? left.join(', ') : 'no _ga cookie'} left, ${v.hits.length} hit(s)`);
    }
    await v.ctx.close();
  }
  await browser.close();
  process.exit(failed ? 1 : 0);
})().catch(e => { console.error(e.message); process.exit(1); });
