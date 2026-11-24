// Visual identity kit v1 (A cinema + B magazine). Renders one frame per component. Usage: node kit.js
const { chromium } = require('playwright');
const fs = require('fs');
const ROOT = __dirname, NM = ROOT + '/node_modules/@fontsource', PH = ROOT + '/assets/photos', OUT = ROOT + '/build/kit';
fs.mkdirSync(OUT, { recursive: true });
const ff = (fam, file, w = 400, st = 'normal') => `@font-face{font-family:'${fam}';font-weight:${w};font-style:${st};src:url(file://${NM}/${file})}`;
const FONTS = [
  ff('Serif', 'playfair-display/files/playfair-display-latin-400-normal.woff2'), ff('Serif', 'playfair-display/files/playfair-display-latin-700-normal.woff2', 700),
  ff('Serif', 'playfair-display/files/playfair-display-latin-400-italic.woff2', 400, 'italic'),
  ff('Cond', 'barlow-condensed/files/barlow-condensed-latin-600-normal.woff2', 600), ff('Cond', 'barlow-condensed/files/barlow-condensed-latin-800-normal.woff2', 800),
  ff('Mono', 'ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2'), ff('Mono', 'ibm-plex-mono/files/ibm-plex-mono-latin-600-normal.woff2', 600),
  ff('Inter', 'inter/files/inter-latin-400-normal.woff2'), ff('Inter', 'inter/files/inter-latin-600-normal.woff2', 600),
].join('');
// design tokens
const T = { lime: '#C6FF00', paper: '#ECE7DC', ink: '#111111', dim: '#BDBAB2', m: 120 };
const noise = (o, f = .85) => `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='${f}' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 ${o} 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")`;
const CSS = `*{margin:0;padding:0;box-sizing:border-box}html,body{width:1920px;height:1080px;overflow:hidden;background:#000;color:#fff}${FONTS}
.abs{position:absolute}.bg{position:absolute;inset:0;background-size:cover;background-position:center}
.grade{filter:contrast(1.08) saturate(.8) brightness(.95)}.bw{filter:grayscale(1) contrast(1.18) brightness(.9)}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 46%,transparent 48%,rgba(0,0,0,.62))}
.grain{position:absolute;inset:-50px;background-image:${noise(.55)};opacity:.22;mix-blend-mode:overlay}
.paper{background-color:${T.paper};background-image:${noise(.18, .6)}}.n25{background-image:${noise(.25, .7)}}.n30{background-image:${noise(.3, .7)}}.n35{background-image:${noise(.35, .5)}}
.mono{font-family:Mono;letter-spacing:.18em;text-transform:uppercase}
.slate{position:absolute;left:${T.m}px;top:96px;display:flex;align-items:center;gap:16px;font:400 20px Mono;letter-spacing:.2em;color:#eee;text-shadow:0 1px 8px rgba(0,0,0,.8)}
.slate i{width:9px;height:9px;border-radius:50%;background:${T.lime};box-shadow:0 0 12px ${T.lime}}
.l3{position:absolute;left:${T.m}px;bottom:210px}.l3 .r{width:44px;height:2px;background:${T.lime};margin-bottom:16px}
.l3 .n{font:400 52px Serif;letter-spacing:.01em;text-shadow:0 2px 18px rgba(0,0,0,.6)}.l3 .t{font:400 18px Mono;letter-spacing:.24em;color:${T.dim};margin-top:10px;text-transform:uppercase}
.sub{position:absolute;left:0;right:0;bottom:96px;text-align:center;font:600 42px/1.32 Inter;text-shadow:0 2px 3px rgba(0,0,0,.7),0 0 26px rgba(0,0,0,.6)}
.sub .who{display:block;font:400 16px Mono;letter-spacing:.24em;color:${T.dim};margin-bottom:10px;text-transform:uppercase}
.crop{position:absolute;width:34px;height:34px;border-color:rgba(255,255,255,.55);border-style:solid;border-width:0}`;
const img = n => `file://${PH}/${n}.jpg`;
const marks = (c = 'rgba(255,255,255,.5)') => ['left:60px;top:60px;border-left-width:1px;border-top-width:1px', 'right:60px;top:60px;border-right-width:1px;border-top-width:1px',
  'left:60px;bottom:60px;border-left-width:1px;border-bottom-width:1px', 'right:60px;bottom:60px;border-right-width:1px;border-bottom-width:1px'].map(s => `<div class="crop" style="${s};border-color:${c}"></div>`).join('');
const clip = `<svg width="120" height="150" viewBox="0 0 120 150" style="position:absolute;left:50%;top:-58px;transform:translateX(-50%)"><path d="M28 70 L40 8 Q60 -4 80 8 L92 70" fill="none" stroke="#9a9a9a" stroke-width="6" stroke-linecap="round"/><rect x="10" y="62" width="100" height="44" rx="6" fill="#151515"/><rect x="10" y="62" width="100" height="10" rx="5" fill="#2a2a2a"/></svg>`;
const torn = (w, seed = 7) => { let p = `M0 0 H${w} V22`, x = w, r = seed; while (x > 0) { r = (r * 9301 + 49297) % 233280; const dx = 10 + (r % 18), dy = 8 + ((r >> 3) % 16); x -= dx; p += ` L${Math.max(0, x)} ${dy}`; } return `${p} L0 22 Z`; };
const F = {
  K01_lowerthird: `<div class="bg grade" style="background-image:url(${img('arteta_face')});background-position:50% 40%"></div><div class="vig"></div>
    <div class="abs" style="inset:0;background:linear-gradient(to top,rgba(0,0,0,.72),transparent 42%)"></div><div class="grain"></div>
    <div class="slate"><i></i>01 · 08 · 2026 — ESTADI MONTILIVI, GIRONA</div>
    <div class="l3"><div class="r"></div><div class="n">Mikel Arteta</div><div class="t">Arsenal manager · Champions of England</div></div>
    <div class="sub"><span class="who">Reporter</span>“And I must ask you: when is Vini joining?”</div>`,
  K02_soundbite: `<div class="bg grade" style="background-image:url(${img('mou_a')});background-position:50% 30%"></div><div class="vig"></div>
    <div class="abs" style="inset:0;background:linear-gradient(to top,rgba(0,0,0,.72),transparent 40%)"></div><div class="grain"></div>
    <div class="l3" style="bottom:250px"><div class="r"></div><div class="n">José Mourinho</div><div class="t">Real Madrid · 17 October 2026</div></div>
    <div class="sub">“If I were in his place, <span style="color:${T.lime}">I probably wouldn't be here.</span>”</div>`,
  K03_chapter: `<div class="abs n25" style="inset:0;background-color:#0d0d0d"></div>
    <div class="abs bw" style="left:0;top:0;width:920px;height:1080px;background:url(${img('xabi_a')}) 32% center/cover"></div>
    <div class="abs" style="left:880px;top:0;width:80px;height:1080px;background:linear-gradient(90deg,transparent,#0d0d0d)"></div><div class="grain"></div>${marks()}
    <div class="abs" style="left:1010px;top:200px;width:780px">
      <div style="display:flex;align-items:baseline;gap:22px"><span style="font:italic 400 64px Serif;color:${T.lime}">01</span><span class="mono" style="font-size:20px;color:#9a978f">May 2025 — Madrid</span></div>
      <div style="font:800 190px/.86 Cond;text-transform:uppercase;margin:22px 0 34px;letter-spacing:-.01em">The<br>Request</div>
      <div style="width:60px;height:2px;background:${T.lime};margin-bottom:28px"></div>
      <div style="font:italic 400 36px/1.45 Serif;color:#dcd8cf;width:640px">Xabi Alonso arrives with one condition: all eleven defend.</div></div>`,
  K04_clipping: `<div class="bg" style="background-image:url(${img('arteta_smile')});filter:blur(14px) brightness(.35) saturate(.6);transform:scale(1.1)"></div><div class="grain"></div>
    <div class="abs paper" style="left:560px;top:250px;width:800px;padding:64px 70px 80px;color:${T.ink};transform:rotate(-1.6deg);box-shadow:0 30px 60px rgba(0,0,0,.55),0 4px 10px rgba(0,0,0,.4)">${clip}
      <div style="display:flex;justify-content:space-between" class="mono"><span style="font-size:18px;font-weight:600">Report · AS</span><span style="font-size:18px;color:#6b6860">August 2026</span></div>
      <div style="height:2px;background:${T.ink};margin:18px 0 34px"></div>
      <div style="font:400 50px/1.32 Serif">Arteta has taken charge of the operation himself:
        <span style="background:linear-gradient(transparent 52%, ${T.lime} 52%, ${T.lime} 92%, transparent 92%)">Vinicius would be the focal point</span> of Arsenal's project.</div>
      <div class="mono" style="font-size:16px;color:#6b6860;margin-top:34px">Paraphrased from the report · not a quote</div>
      <svg class="abs" style="left:0;bottom:-21px" width="800" height="22" viewBox="0 0 800 22"><path d="${torn(800)}" fill="${T.paper}"/></svg></div>`,
  K05_quote: `<div class="bg bw" style="background-image:url(${img('mou_b')});background-position:58% 30%;filter:grayscale(1) contrast(1.2) brightness(.45)"></div><div class="vig"></div><div class="grain"></div>${marks()}
    <div class="abs" style="left:${T.m}px;top:300px;width:1100px">
      <div style="font:400 220px/0.6 Serif;color:${T.lime};height:110px">“</div>
      <div style="font:italic 400 92px/1.15 Serif">Only the badge is untouchable.</div>
      <div style="width:60px;height:2px;background:${T.lime};margin:46px 0 20px"></div>
      <div class="mono" style="font-size:22px;color:#cfcbc2">José Mourinho · 20 October 2026</div></div>`,
  K06_scorebug: `<div class="bg grade" style="background-image:url(${img('vini_stand')});background-position:50% 40%"></div><div class="vig"></div><div class="grain"></div>
    <div class="abs" style="left:${T.m}px;top:92px;display:flex;align-items:stretch;font:600 40px Cond;letter-spacing:.04em;box-shadow:0 10px 30px rgba(0,0,0,.45)">
      <div style="background:rgba(12,12,12,.92);padding:10px 24px">BAR</div>
      <div style="background:${T.paper};color:${T.ink};padding:10px 22px;font-weight:800">1 – 2</div>
      <div style="background:rgba(12,12,12,.92);padding:10px 24px">RMA</div>
      <div style="background:rgba(12,12,12,.75);padding:16px 22px 0;font:400 18px Mono;letter-spacing:.2em;color:${T.dim}">FT · CAMP NOU · 25.10.2026</div></div>
    <div class="abs" style="left:${T.m}px;top:170px;font:400 18px Mono;letter-spacing:.2em;color:${T.lime};text-shadow:0 1px 8px #000">VINICIUS · SUSPENDED</div>`,
  K07_results: `<div class="bg" style="background-image:url(${img('diom_shirt')});filter:grayscale(.6) brightness(.38)"></div>
    <div class="abs" style="inset:0;background:linear-gradient(90deg,rgba(0,0,0,.85),rgba(0,0,0,.2) 70%)"></div><div class="grain"></div>
    <div class="abs" style="left:${T.m}px;top:230px;width:860px">
      <div class="mono" style="font-size:20px;color:${T.lime}">Without Vinicius · Oct–Nov 2026</div>
      <div style="margin-top:30px;border-top:1px solid rgba(255,255,255,.35)">
      ${[['Real Madrid', '4–1', 'Sevilla'], ['Barcelona', '1–2', 'Real Madrid'], ['Racing', '0–3', 'Real Madrid'], ['Valencia', '0–3', 'Real Madrid']].map(r => `<div style="display:grid;grid-template-columns:330px 140px 330px 40px;align-items:center;padding:20px 0;border-bottom:1px solid rgba(255,255,255,.2);font:400 44px Serif">
        <span>${r[0]}</span><span style="font:800 46px Cond;text-align:center;font-variant-numeric:tabular-nums">${r[1]}</span><span>${r[2]}</span><span style="color:${T.lime};font:600 30px Inter">✓</span></div>`).join('')}</div>
      <div class="mono" style="font-size:18px;color:${T.dim};margin-top:26px">12 scored · 2 conceded</div></div>`,
  K08_impact: `<div class="bg bw" style="background-image:url(${img('diom_face')});background-position:62% 30%"></div><div class="vig"></div><div class="grain"></div>
    <div class="abs" style="left:${T.m}px;top:130px;font:800 250px/.82 Cond;color:${T.lime};text-transform:uppercase;letter-spacing:-.01em">4 games.<br>4 wins.</div>
    <div class="abs paper" style="left:${T.m + 6}px;bottom:130px;color:${T.ink};padding:12px 22px;font:600 20px Mono;letter-spacing:.18em">REAL MADRID WITHOUT VINICIUS</div>`,
  K09_timeline: `<div class="abs n30" style="inset:0;background-color:#0e0e0e"></div><div class="grain"></div>
    <div class="abs mono" style="left:${T.m}px;top:110px;font-size:20px;color:${T.lime}">Two chances to change</div>
    <div class="abs" style="left:${T.m}px;right:${T.m}px;top:700px;height:2px;background:rgba(255,255,255,.35)"></div>
    ${[['xabi_a', 'MAY 2025', 'Xabi asks for more'], ['xabi_d', 'JAN 2026', 'Xabi is sacked'], ['arteta_smile', 'AUG 2026', 'Arteta calls. He stays'], ['vini_sub', 'OCT 2026', 'Red card. 4-game ban']].map((t, i) => {
      const x = T.m + i * 430; return `<div class="abs" style="left:${x}px;top:250px;width:360px">
      <div style="background:#f5f2ea;padding:12px 12px 46px;transform:rotate(${[-2, 1.5, -1, 2][i]}deg);box-shadow:0 18px 34px rgba(0,0,0,.6)"><div style="height:250px;background:url(${img(t[0])}) center/cover;filter:grayscale(${i == 2 ? 0 : 1}) contrast(1.1)"></div>
      <div style="font:italic 400 24px Serif;color:#222;margin-top:12px">${t[2]}</div></div></div>
      <div class="abs" style="left:${x + 170}px;top:692px;width:18px;height:18px;border-radius:50%;background:${i == 2 ? T.lime : '#fff'};box-shadow:0 0 0 6px rgba(255,255,255,.08)"></div>
      <div class="abs mono" style="left:${x + 110}px;top:736px;font-size:20px;color:${i == 2 ? T.lime : '#ddd'}">${t[1]}</div>`; }).join('')}`,
  K10_print: `<div class="abs n35" style="inset:0;background-color:#1a1916"></div><div class="grain"></div>
    <div class="abs" style="left:380px;top:110px;width:1160px;background:#f5f2ea;padding:24px 24px 90px;transform:rotate(-1.2deg);box-shadow:0 40px 70px rgba(0,0,0,.65)">
      <div style="height:690px;background:url(${img('vini_walk')}) 50% 30%/cover;filter:contrast(1.08) saturate(.75) sepia(.12)"></div>
      <div style="display:flex;justify-content:space-between;align-items:baseline;margin-top:26px;color:#222"><span style="font:italic 400 34px Serif">Booed by his own stadium.</span><span class="mono" style="font-size:18px;color:#6b6860">Bernabéu · 04.01.2026</span></div></div>`,
  K11_callout_cta: `<div class="bg grade" style="background-image:url(${img('diom_shirt')})"></div><div class="vig"></div><div class="grain"></div>
    <svg class="abs" style="left:0;top:0" width="1920" height="1080"><circle cx="985" cy="300" r="120" fill="none" stroke="${T.lime}" stroke-width="3"/><path d="M1090 240 L1290 150 L1480 150" fill="none" stroke="${T.lime}" stroke-width="2"/></svg>
    <div class="abs" style="left:1300px;top:92px;background:rgba(12,12,12,.78);padding:14px 22px 16px"><div style="font:400 44px Serif">Yan Diomande</div><div class="mono" style="font-size:18px;color:${T.dim};margin-top:8px">19 · From RB Leipzig</div></div>
    <div class="abs" style="right:${T.m}px;bottom:96px;display:flex;align-items:center;gap:16px;background:rgba(14,14,14,.82);backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,.15);border-radius:999px;padding:14px 30px 14px 16px;box-shadow:0 10px 30px rgba(0,0,0,.5)">
      <div style="width:46px;height:46px;border-radius:50%;background:${T.lime};display:flex;align-items:center;justify-content:center"><svg width="24" height="24" viewBox="0 0 24 24"><path d="M12 22a2.5 2.5 0 0 0 2.4-2h-4.8A2.5 2.5 0 0 0 12 22zm7-6V11a7 7 0 0 0-5-6.7V3a2 2 0 0 0-4 0v1.3A7 7 0 0 0 5 11v5l-2 2v1h18v-1z" fill="#111"/></svg></div>
      <div style="font:600 28px Inter">Subscribe</div><div class="mono" style="font-size:15px;color:${T.dim}">New story every week</div></div>`,
  K12_title: `<div class="bg bw" style="background-image:url(${img('vini_stand')});filter:grayscale(1) contrast(1.15) brightness(.42)"></div><div class="vig"></div><div class="grain"></div>${marks()}
    <div class="abs" style="inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center">
      <div class="mono" style="font-size:20px;color:${T.lime}">A football story</div>
      <div style="font:400 120px/1.05 Serif;margin:30px 0 10px">Arteta Tried<br><span style="font-style:italic">to Save</span> Vinicius</div>
      <div style="width:60px;height:2px;background:${T.lime};margin:30px 0 22px"></div>
      <div class="mono" style="font-size:18px;color:#cfcbc2">Two chances to change · One choice</div></div>`,
};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const [k, h] of Object.entries(F)) {
    const f = `${OUT}/${k}.html`; fs.writeFileSync(f, `<!doctype html><html><head><meta charset="utf-8"><style>${CSS}</style></head><body>${h}</body></html>`);
    await p.goto('file://' + f); await p.evaluate(() => document.fonts.ready); await p.screenshot({ path: `${OUT}/${k}.png` }); console.log(k);
  }
  await b.close();
})();
