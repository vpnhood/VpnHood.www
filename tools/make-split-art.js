// The bubbles of each split-tunneling art variant, for tools/make-split-art.py: teal coins turned in 3D with a
// white line glyph, and tilted 3D pills holding text, in the style of the two original variants. Drawn on a
// transparent 468x480 canvas at 3x; the Python script scales them down over the clean gate. Also draws the hood
// mask the Python script carves into the gate's door.
//
//   node tools/make-split-art.js <playwright module dir> <out dir> <variants json>
const [, , PLAYWRIGHT, OUT, VARIANTS_JSON] = process.argv;
const { chromium } = require(PLAYWRIGHT);
const fs = require('fs');
const path = require('path');
const FONT = path.join(__dirname, '..', 'assets', 'fonts', 'poppins', 'poppins-latin-700.woff2');

// Line glyphs on a 24-unit grid, drawn like the site's own icons.
const G = {
  bank: '<path d="M3.5 9.5 12 4.5l8.5 5"/><path d="M6 10.5v7M10 10.5v7M14 10.5v7M18 10.5v7"/><path d="M4 19.5h16"/>',
  play: '<rect x="3.5" y="5.5" width="17" height="13" rx="3"/><path d="M10.2 9.3v5.4l4.6-2.7z" fill="#fff" stroke="none"/>',
  chat: '<path d="M4.5 7A2.5 2.5 0 0 1 7 4.5h10A2.5 2.5 0 0 1 19.5 7v6.5A2.5 2.5 0 0 1 17 16h-6.5L6.5 19.5V16H7a2.5 2.5 0 0 1-2.5-2.5z"/>',
  flag: '<path d="M6 20.5v-16"/><path d="M6 5h11l-2.2 3.6L17 12.2H6"/>',
  pin: '<path d="M12 20.5s-6-5.5-6-10.3a6 6 0 0 1 12 0c0 4.8-6 10.3-6 10.3z"/><circle cx="12" cy="10.2" r="2.2"/>',
  map: '<path d="M3.5 6.8 9 4.5l6 2.3 5.5-2.3v12.7L15 19.5l-6-2.3-5.5 2.3z"/><path d="M9 4.5v12.7M15 6.8v12.7"/>',
  www: '<text x="12" y="15.2" text-anchor="middle" font-family="vh" font-size="8.6" fill="#fff" stroke="none">www</text>',
};

const coin = (b, g) => `<div class="coin" style="left:${b.x}px;top:${b.y}px;width:${b.w}px;height:${b.h}px">
  <div class="rim"></div><div class="face"><svg viewBox="0 0 24 24" fill="rgba(255,255,255,.14)" stroke="#f4fffb" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round">${G[g]}</svg></div></div>`;
const pill = (p, text, tone) => `<div class="pill ${tone}" style="left:${p.x}px;top:${p.y}px;width:${p.w}px"><div class="edge"></div><div class="top"><span>${text}</span></div></div>`;

const CSS = `
@font-face { font-family: vh; src: url(data:font/woff2;base64,${fs.readFileSync(FONT).toString('base64')}) format('woff2'); font-weight: 700; }
html, body { margin: 0; background: transparent; }
.stage { position: relative; width: 468px; height: 480px; }
.coin { position: absolute; }
.coin .rim, .coin .face { position: absolute; inset: 0; border-radius: 50%; }
.coin .rim { transform: translate(9%, 2%); background: linear-gradient(160deg, #e3fbf3, #8fe6cd 45%, #3bb193); }
.coin .face { background: radial-gradient(120% 90% at 30% 22%, #7debd0 0%, #3cc9a8 45%, #23a68b 100%);
  box-shadow: inset 0 0 0 1.5px rgba(10,90,75,.55), inset 0 0 0 3.5px rgba(255,255,255,.22), inset -4px -6px 10px rgba(9,70,62,.4); display: grid; place-items: center; }
.coin svg { width: 74%; transform: skewY(7deg); filter: drop-shadow(0 1.2px 0 rgba(10,70,60,.5)); }
.pill { position: absolute; height: 35px; transform: rotate(27deg) skewX(-14deg); transform-origin: left center; }
.pill .edge, .pill .top { position: absolute; inset: 0; border-radius: 17.5px; }
.pill .edge { transform: translate(4px, 5px); background: linear-gradient(90deg, #ede6ff, #cfc2f7); }
.pill.teal .edge { background: linear-gradient(90deg, #d9d2ff, #b9f3e3); }
.pill .top { display: grid; place-items: center; box-shadow: inset 0 1px 0 rgba(255,255,255,.55), inset 0 -2px 5px rgba(40,20,110,.25); }
.pill.violet .top { background: linear-gradient(90deg, #c7b6f4 0%, #8f74e6 45%, #6a4fd6 100%); }
.pill.teal .top { background: linear-gradient(90deg, #8a72e4 0%, #5aa9d6 45%, #3fd0ad 100%); }
.pill span { font: 700 18px/1 vh; color: #fff; letter-spacing: .8px; text-shadow: 0 1px 0 rgba(40,20,110,.45), 0 0 6px rgba(255,255,255,.25); transform: skewX(6deg); }
`;

(async () => {
  const variants = JSON.parse(fs.readFileSync(VARIANTS_JSON, 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 468, height: 480 }, deviceScaleFactor: 3 });
  for (const [name, parts] of Object.entries(variants)) {
    const body = parts.map(([kind, at, a, b]) => kind === 'coin' ? coin(at, a) : pill(at, a, b)).join('');
    await page.setContent(`<style>${CSS}</style><div class="stage">${body}</div>`);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(OUT, `${name}-bubbles.png`), omitBackground: true, clip: { x: 0, y: 0, width: 468, height: 480 } });
  }
  // The hood carved into the door: the site's own mark, the favicon's path, white on black, 1024 px square.
  const favicon = fs.readFileSync(path.join(__dirname, '..', 'assets', 'images', 'favicon.svg'), 'utf8');
  const d = favicon.match(/ d="([^"]+)"/)[1];
  const mask = await browser.newPage({ viewport: { width: 1024, height: 1024 } });
  await mask.setContent(`<style>html,body{margin:0;background:#000}</style><svg width="1024" height="1024" viewBox="0 0 32 32"><path fill="#fff" d="${d}"/></svg>`);
  await mask.screenshot({ path: path.join(OUT, 'hood-mask.png') });
  await browser.close();
})().catch(e => { console.error(e.message); process.exit(1); });
