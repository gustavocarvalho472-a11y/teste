// Style frames for 3 visual-identity directions (A cinema, B magazine, C classic TV). Usage: node styleframes.js
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const ROOT = __dirname, NM = ROOT + '/node_modules/@fontsource', PH = ROOT + '/assets/photos', OUT = ROOT + '/build/style';
fs.mkdirSync(OUT, { recursive: true });
const font = (fam, file, w = 400, st = 'normal') => `@font-face{font-family:'${fam}';font-weight:${w};font-style:${st};src:url(file://${NM}/${file})}`;
const FONTS = [
  font('Playfair', 'playfair-display/files/playfair-display-latin-400-normal.woff2'), font('Playfair', 'playfair-display/files/playfair-display-latin-700-normal.woff2', 700),
  font('Playfair', 'playfair-display/files/playfair-display-latin-400-italic.woff2', 400, 'italic'),
  font('Barlow', 'barlow-condensed/files/barlow-condensed-latin-600-normal.woff2', 600), font('Barlow', 'barlow-condensed/files/barlow-condensed-latin-800-normal.woff2', 800),
  font('Mono', 'ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2'), font('Mono', 'ibm-plex-mono/files/ibm-plex-mono-latin-600-normal.woff2', 600),
  font('Inter', 'inter/files/inter-latin-400-normal.woff2'), font('Inter', 'inter/files/inter-latin-600-normal.woff2', 600), font('Inter', 'inter/files/inter-latin-800-normal.woff2', 800),
  font('Oswald', 'oswald/files/oswald-latin-500-normal.woff2', 500), font('Oswald', 'oswald/files/oswald-latin-700-normal.woff2', 700),
  font('Anton', 'anton/files/anton-latin-400-normal.woff2'),
].join('');
const L = '#C6FF00';
const base = `*{margin:0;padding:0;box-sizing:border-box}html,body{width:1920px;height:1080px;overflow:hidden;background:#000;color:#fff}${FONTS}
.bg{position:absolute;inset:0;background-size:cover;background-position:center}.abs{position:absolute}
.grain{position:absolute;inset:0;opacity:.13;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}`;
const img = n => `file://${PH}/${n}.jpg`;
const F = {
  // ---------------- A · CINEMA (documentary): full-bleed picture, graded, small elegant type, almost no boxes
  A1: `<div class="bg" style="background-image:url(${img('mou_a')});filter:contrast(1.08) saturate(.78) sepia(.08) brightness(.92)"></div>
       <div class="abs" style="inset:0;background:radial-gradient(ellipse at 50% 45%,transparent 50%,rgba(0,0,0,.65));"></div>
       <div class="abs" style="inset:0;background:linear-gradient(to top,rgba(0,0,0,.7),transparent 38%)"></div><div class="grain"></div>
       <div class="abs" style="left:120px;top:110px"><div style="width:46px;height:3px;background:${L};margin-bottom:18px"></div>
         <div style="font:400 50px Playfair;letter-spacing:.5px">José Mourinho</div><div style="font:400 23px Inter;color:#d6d6d6;margin-top:8px;letter-spacing:1px">Real Madrid press room · 17 October 2026</div></div>
       <div class="abs" style="left:0;right:0;bottom:92px;text-align:center;font:600 46px/1.3 Inter;text-shadow:0 2px 14px #000">“If I were in his place, I probably wouldn't be here.”</div>`,
  A2: `<div class="bg" style="background-image:url(${img('xabi_a')});filter:grayscale(1) contrast(1.1) brightness(.35)"></div><div class="grain"></div>
       <div class="abs" style="inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center">
         <div style="font:600 24px Mono;color:${L};letter-spacing:8px">I · MAY 2025</div>
         <div style="font:400 140px Playfair;letter-spacing:22px;margin:26px 0 18px">THE REQUEST</div>
         <div style="font:italic 400 34px Playfair;color:#cfcfcf">Xabi Alonso arrives at the Bernabéu</div></div>`,
  A3: `<div class="bg" style="background-image:url(${img('bernabeu')});filter:contrast(1.05) saturate(.7) brightness(.62)"></div>
       <div class="abs" style="inset:0;background:linear-gradient(90deg,rgba(0,0,0,.78),transparent 55%)"></div><div class="grain"></div>
       <div class="abs" style="left:130px;top:250px"><div style="font:600 22px Mono;color:${L};letter-spacing:6px">WITHOUT VINICIUS · OCT–NOV 2026</div>
         <div style="margin-top:34px;font:400 52px/1.7 Playfair">Real Madrid 4–1 Sevilla<br>Barcelona 1–2 Real Madrid<br>Racing 0–3 Real Madrid<br>Valencia 0–3 Real Madrid</div>
         <div style="margin-top:26px;font:400 26px Inter;color:#cfcfcf">Four games, four wins · 12 scored, 2 conceded</div></div>`,
  // ---------------- B · MAGAZINE (editorial): black & white photos, big condensed lime headlines, caption labels
  B1: `<div class="bg" style="background-image:url(${img('mou_a')});filter:grayscale(.15) contrast(1.06)"></div><div class="grain"></div>
       <div class="abs" style="left:110px;bottom:120px;display:flex;flex-direction:column;align-items:flex-start;gap:0">
         <div style="background:#f3f1ea;color:#0a0a0a;font:800 74px/1 Barlow;padding:14px 26px 8px;text-transform:uppercase">José Mourinho</div>
         <div style="background:${L};color:#0a0a0a;font:600 22px Mono;padding:9px 26px;letter-spacing:2px">17.10.2026 — REAL MADRID PRESS ROOM</div></div>
       <div class="abs" style="left:0;right:0;bottom:40px;text-align:center;font:600 40px Inter;text-shadow:0 2px 12px #000">“If I were in his place, I probably wouldn't be here.”</div>`,
  B2: `<div class="abs" style="inset:0;background:#0b0b0b"></div>
       <div class="abs" style="left:0;top:0;width:900px;height:1080px;background:url(${img('xabi_a')}) 30% center/cover;filter:grayscale(1) contrast(1.25)"></div><div class="grain"></div>
       <div class="abs" style="left:990px;top:150px;width:820px">
         <div style="font:600 24px Mono;color:#9a9a9a;letter-spacing:4px">CHAPTER 01 — MAY 2025</div>
         <div style="font:800 210px/.86 Barlow;color:${L};margin:26px 0 30px;text-transform:uppercase">The<br>Request</div>
         <div style="font:400 30px/1.5 Inter;color:#e6e6e6;width:640px">Xabi Alonso arrives at Real Madrid with one condition: all eleven defend. Vinicius included.</div></div>`,
  B3: `<div class="bg" style="background-image:url(${img('diom_face')});background-position:60% 30%;filter:grayscale(1) contrast(1.2) brightness(.8)"></div><div class="grain"></div>
       <div class="abs" style="left:110px;top:120px;font:800 230px/.84 Barlow;color:${L};text-transform:uppercase">4 games.<br>4 wins.</div>
       <div class="abs" style="left:116px;bottom:120px;background:#f3f1ea;color:#0a0a0a;font:600 24px Mono;padding:10px 20px">REAL MADRID WITHOUT VINICIUS · 12 SCORED · 2 CONCEDED</div>`,
  // ---------------- C · CLASSIC TV (broadcast): clean bars and a score bug, like a Sunday-night football show
  C1: `<div class="bg" style="background-image:url(${img('mou_a')})"></div>
       <div class="abs" style="left:110px;bottom:120px;display:flex;height:120px;box-shadow:0 8px 30px rgba(0,0,0,.5)">
         <div style="width:16px;background:${L}"></div><div style="background:rgba(10,10,10,.92);padding:16px 36px">
         <div style="font:700 50px Oswald;letter-spacing:1px;text-transform:uppercase">José Mourinho</div><div style="font:500 24px Oswald;color:#bdbdbd;letter-spacing:2px">REAL MADRID COACH · 17 OCT 2026</div></div></div>
       <div class="abs" style="left:0;right:0;bottom:40px;text-align:center;font:600 40px Inter;text-shadow:0 2px 12px #000">“If I were in his place, I probably wouldn't be here.”</div>`,
  C2: `<div class="bg" style="background-image:url(${img('xabi_a')})"></div>
       <div class="abs" style="left:80px;top:70px;display:flex;align-items:stretch;font:700 30px Oswald;letter-spacing:2px">
         <div style="background:${L};color:#0a0a0a;padding:10px 20px">PART 1</div><div style="background:rgba(10,10,10,.9);padding:10px 24px">THE REQUEST · MAY 2025</div></div>`,
  C3: `<div class="bg" style="background-image:url(${img('vini_stand')});filter:brightness(.85)"></div>
       <div class="abs" style="left:80px;top:70px;display:flex;font:700 34px Oswald;letter-spacing:1px;box-shadow:0 6px 20px rgba(0,0,0,.5)">
         <div style="background:#0a0a0a;padding:10px 22px">BAR</div><div style="background:${L};color:#0a0a0a;padding:10px 22px">1 – 2</div><div style="background:#0a0a0a;padding:10px 22px">RMA</div>
         <div style="background:rgba(10,10,10,.8);color:#bdbdbd;padding:10px 22px;font-weight:500">25 OCT · CAMP NOU</div></div>
       <div class="abs" style="right:90px;top:240px;width:600px;background:rgba(10,10,10,.88);border-top:6px solid ${L};padding:26px 32px;font:500 32px/1.75 Oswald">
         <div style="font:700 26px Oswald;color:${L};letter-spacing:3px">WITHOUT VINICIUS</div>Real Madrid 4–1 Sevilla<br>Barcelona 1–2 Real Madrid<br>Racing 0–3 Real Madrid<br>Valencia 0–3 Real Madrid</div>`,
};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const [k, h] of Object.entries(F)) {
    const f = `${OUT}/${k}.html`; fs.writeFileSync(f, `<!doctype html><html><head><meta charset="utf-8"><style>${base}</style></head><body>${h}</body></html>`);
    await p.goto('file://' + f); await p.evaluate(() => document.fonts.ready); await p.screenshot({ path: `${OUT}/${k}.png` }); console.log(k);
  }
  await b.close();
})();
