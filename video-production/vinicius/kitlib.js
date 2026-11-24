// kitlib.js — "Cinema + Revista" identity kit (channel style v2, approved nov/2026).
// Every component is a function(params) -> HTML. Overlays are transparent 1920x1080 PNGs; plates are full-frame
// pictures rendered at 2x (3840x2160) so the camera can push in on them without softening the type.
// Text conventions: *word* = lime highlight (overlays) or lime marker (paper). Keep text short: the picture leads.
const path = require('path');
const NM = path.join(__dirname, 'node_modules/@fontsource');
const K = { PH: path.join(__dirname, 'assets/photos') };
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
const CSS = `*{margin:0;padding:0;box-sizing:border-box}html,body{width:1920px;height:1080px;overflow:hidden;color:#fff}${FONTS}
body.plate{background:#000}body.ov{background:transparent}
.abs{position:absolute}.bg{position:absolute;inset:0;background-size:cover;background-position:center}
.grade{filter:contrast(1.08) saturate(.8) brightness(.95)}.bw{filter:grayscale(1) contrast(1.18) brightness(.9)}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 46%,transparent 48%,rgba(0,0,0,.62))}
.grain{position:absolute;inset:-50px;background-image:${noise(.55)};opacity:.22;mix-blend-mode:overlay}
.paper{background-color:${T.paper};background-image:${noise(.18, .6)}}.n25{background-image:${noise(.25, .7)}}.n30{background-image:${noise(.3, .7)}}.n35{background-image:${noise(.35, .5)}}
.mono{font-family:Mono;letter-spacing:.18em;text-transform:uppercase}
.slate{position:absolute;left:${T.m}px;top:96px;display:flex;align-items:center;gap:16px;font:400 21px Mono;letter-spacing:.2em;color:#f2f2f2;text-transform:uppercase;text-shadow:0 1px 3px rgba(0,0,0,.9),0 0 18px rgba(0,0,0,.7)}
.slate i{width:9px;height:9px;border-radius:50%;background:${T.lime};box-shadow:0 0 12px ${T.lime}}
.shade-t{position:absolute;left:0;right:0;top:0;height:300px;background:linear-gradient(to bottom,rgba(0,0,0,.5),transparent)}
.shade-b{position:absolute;left:0;right:0;bottom:0;height:520px;background:linear-gradient(to top,rgba(0,0,0,.66),rgba(0,0,0,.3) 45%,transparent)}
.l3{position:absolute;left:${T.m}px;bottom:210px}.l3 .r{width:44px;height:2px;background:${T.lime};margin-bottom:16px}
.l3 .n{font:400 54px Serif;letter-spacing:.01em;text-shadow:0 2px 18px rgba(0,0,0,.6)}.l3 .t{font:400 19px Mono;letter-spacing:.22em;color:#d4d1c9;margin-top:10px;text-transform:uppercase;text-shadow:0 1px 6px rgba(0,0,0,.8)}
.sub{position:absolute;left:160px;right:160px;bottom:92px;text-align:center;font:600 44px/1.3 Inter;text-shadow:0 2px 3px rgba(0,0,0,.75),0 0 26px rgba(0,0,0,.6)}
.sub .who{display:block;font:400 17px Mono;letter-spacing:.24em;color:#d4d1c9;margin-bottom:12px;text-transform:uppercase}
.hl{color:${T.lime}}.mk{background:linear-gradient(transparent 52%, ${T.lime} 52%, ${T.lime} 92%, transparent 92%)}
.crop{position:absolute;width:34px;height:34px;border-color:rgba(255,255,255,.55);border-style:solid;border-width:0}`;
const img = n => n.startsWith('/') ? `file://${n}` : `file://${K.PH}/${n}.jpg`;
const hl = s => String(s).replace(/\*(.+?)\*/g, '<span class="hl">$1</span>');
const mk = s => String(s).replace(/\*(.+?)\*/g, '<span class="mk">$1</span>');
const marks = (c = 'rgba(255,255,255,.5)') => ['left:60px;top:60px;border-left-width:1px;border-top-width:1px', 'right:60px;top:60px;border-right-width:1px;border-top-width:1px',
  'left:60px;bottom:60px;border-left-width:1px;border-bottom-width:1px', 'right:60px;bottom:60px;border-right-width:1px;border-bottom-width:1px'].map(s => `<div class="crop" style="${s};border-color:${c}"></div>`).join('');
const clip = `<svg width="120" height="150" viewBox="0 0 120 150" style="position:absolute;left:50%;top:-58px;transform:translateX(-50%)"><path d="M28 70 L40 8 Q60 -4 80 8 L92 70" fill="none" stroke="#9a9a9a" stroke-width="6" stroke-linecap="round"/><rect x="10" y="62" width="100" height="44" rx="6" fill="#151515"/><rect x="10" y="62" width="100" height="10" rx="5" fill="#2a2a2a"/></svg>`;
const torn = (w, seed = 7) => { let p = `M0 0 H${w} V22`, x = w, r = seed; while (x > 0) { r = (r * 9301 + 49297) % 233280; const dx = 10 + (r % 18), dy = 8 + ((r >> 3) % 16); x -= dx; p += ` L${Math.max(0, x)} ${dy}`; } return `${p} L0 22 Z`; };
const bell = `<svg width="24" height="24" viewBox="0 0 24 24"><path d="M12 22a2.5 2.5 0 0 0 2.4-2h-4.8A2.5 2.5 0 0 0 12 22zm7-6V11a7 7 0 0 0-5-6.7V3a2 2 0 0 0-4 0v1.3A7 7 0 0 0 5 11v5l-2 2v1h18v-1z" fill="#111"/></svg>`;
const bubble = `<svg width="24" height="24" viewBox="0 0 24 24"><path d="M4 4h16a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H9l-5 4v-4H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1z" fill="#111"/></svg>`;

// ---------------------------------------------------------------- OVERLAYS (transparent, over moving footage)
const OV = {
  // date / place stamp, top-left. Use it instead of a title card whenever a scene needs "when and where".
  slate: p => `<div class="shade-t"></div><div class="slate"><i></i>${p.text}</div>`,
  // name super: serif name + mono role. Once per person, the first time we see them.
  l3: p => `${p.shade === false ? '' : '<div class="shade-b"></div>'}<div class="l3" style="bottom:${p.bottom || 210}px"><div class="r"></div><div class="n">${p.name}</div><div class="t">${p.role}</div></div>`,
  // soundbite subtitle (one phrase per PNG). The scene gets one 'shade' overlay for its whole length.
  sub: p => `<div class="sub">${p.who ? `<span class="who">${p.who}</span>` : ''}${hl(p.text)}</div>`,
  shade: () => `<div class="shade-b"></div>`,
  // final score, top-left, with an optional lime note under it.
  score: p => `<div class="shade-t"></div><div class="abs" style="left:${T.m}px;top:92px;display:flex;align-items:stretch;font:600 40px Cond;letter-spacing:.04em;box-shadow:0 10px 30px rgba(0,0,0,.45)">
      <div style="background:rgba(12,12,12,.92);padding:10px 24px">${p.home}</div>
      <div style="background:${T.paper};color:${T.ink};padding:10px 22px;font-weight:800">${p.score}</div>
      <div style="background:rgba(12,12,12,.92);padding:10px 24px">${p.away}</div>
      <div style="background:rgba(12,12,12,.75);padding:17px 22px 0;font:400 18px Mono;letter-spacing:.2em;color:${T.dim}">${p.info}</div></div>
    ${p.note ? `<div class="abs" style="left:${T.m}px;top:172px;font:400 19px Mono;letter-spacing:.2em;color:${T.lime};text-shadow:0 1px 8px #000">${p.note}</div>` : ''}`,
  // call to action pill, bottom-right (bell = subscribe, bubble = comment)
  cta: p => `<div class="abs" style="right:${T.m}px;bottom:96px;display:flex;align-items:center;gap:16px;background:rgba(14,14,14,.84);border:1px solid rgba(255,255,255,.15);border-radius:999px;padding:14px 32px 14px 16px;box-shadow:0 10px 30px rgba(0,0,0,.5)">
      <div style="width:48px;height:48px;border-radius:50%;background:${T.lime};display:flex;align-items:center;justify-content:center">${p.icon === 'bubble' ? bubble : bell}</div>
      <div style="font:600 30px Inter">${p.main}</div>${p.small ? `<div class="mono" style="font-size:15px;color:${T.dim}">${p.small}</div>` : ''}</div>`,
};

// ---------------------------------------------------------------- PLATES (full frame, the camera moves over them)
const PL = {
  title: p => `<div class="bg bw" style="background-image:url(${img(p.photo)});background-position:${p.pos || '50% 40%'};filter:grayscale(1) contrast(1.15) brightness(.42)"></div><div class="vig"></div><div class="grain"></div>${marks()}
    <div class="abs" style="inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center">
      <div class="mono" style="font-size:20px;color:${T.lime}">${p.kicker || 'A football story'}</div>
      <div style="font:400 124px/1.05 Serif;margin:30px 0 10px">${p.l1}<br>${p.l2}</div>
      <div style="width:60px;height:2px;background:${T.lime};margin:30px 0 22px"></div>
      <div class="mono" style="font-size:19px;color:#cfcbc2">${p.sub}</div></div>`,
  chapter: p => `<div class="abs n25" style="inset:0;background-color:#0d0d0d"></div>
    <div class="abs bw" style="left:0;top:0;width:920px;height:1080px;background:url(${img(p.photo)}) ${p.pos || '32% center'}/cover"></div>
    <div class="abs" style="left:860px;top:0;width:100px;height:1080px;background:linear-gradient(90deg,transparent,#0d0d0d)"></div><div class="grain"></div>${marks()}
    <div class="abs" style="left:1010px;top:${p.top || 220}px;width:800px">
      <div style="display:flex;align-items:baseline;gap:22px">${p.num ? `<span style="font:italic 400 64px Serif;color:${T.lime}">${p.num}</span>` : ''}<span class="mono" style="font-size:20px;color:#9a978f">${p.date}</span></div>
      <div style="font:800 ${p.size || 180}px/.86 Cond;text-transform:uppercase;margin:22px 0 34px;letter-spacing:-.01em">${p.title}</div>
      <div style="width:60px;height:2px;background:${T.lime};margin-bottom:28px"></div>
      <div style="font:italic 400 36px/1.45 Serif;color:#dcd8cf;width:660px">${p.synopsis}</div></div>`,
  clipping: p => `<div class="bg" style="background-image:url(${img(p.bg)});filter:blur(14px) brightness(.35) saturate(.6);transform:scale(1.1)"></div><div class="grain"></div>
    <div class="abs paper" style="left:560px;top:${p.top || 250}px;width:800px;padding:64px 70px 80px;color:${T.ink};transform:rotate(${p.rot || -1.6}deg);box-shadow:0 30px 60px rgba(0,0,0,.55),0 4px 10px rgba(0,0,0,.4)">${clip}
      <div style="display:flex;justify-content:space-between" class="mono"><span style="font-size:18px;font-weight:600">${p.source}</span><span style="font-size:18px;color:#6b6860">${p.date}</span></div>
      <div style="height:2px;background:${T.ink};margin:18px 0 34px"></div>
      <div style="font:400 ${p.size || 50}px/1.32 Serif">${mk(p.text)}</div>
      <div class="mono" style="font-size:16px;color:#6b6860;margin-top:34px">${p.note || 'Paraphrased from the report · not a quote'}</div>
      <svg class="abs" style="left:0;bottom:-21px" width="800" height="22" viewBox="0 0 800 22"><path d="${torn(800)}" fill="${T.paper}"/></svg></div>`,
  quote: p => `<div class="bg bw" style="background-image:url(${img(p.photo)});background-position:${p.pos || '58% 30%'};filter:grayscale(1) contrast(1.2) brightness(.42)"></div><div class="vig"></div><div class="grain"></div>${marks()}
    <div class="abs" style="left:${T.m}px;top:${p.top || 300}px;width:${p.w || 1150}px">
      <div style="font:400 220px/0.6 Serif;color:${T.lime};height:110px">“</div>
      <div style="font:italic 400 ${p.size || 88}px/1.17 Serif">${p.text}</div>
      <div style="width:60px;height:2px;background:${T.lime};margin:46px 0 20px"></div>
      <div class="mono" style="font-size:22px;color:#cfcbc2">${p.who}</div></div>`,
  results: p => `<div class="bg" style="background-image:url(${img(p.photo)});background-position:${p.pos || 'center'};filter:grayscale(.6) brightness(.38)"></div>
    <div class="abs" style="inset:0;background:linear-gradient(90deg,rgba(0,0,0,.85),rgba(0,0,0,.2) 70%)"></div><div class="grain"></div>
    <div class="abs" style="left:${T.m}px;top:230px;width:880px">
      <div class="mono" style="font-size:20px;color:${T.lime}">${p.tag}</div>
      <div style="margin-top:30px;border-top:1px solid rgba(255,255,255,.35)">
      ${p.rows.map((r, i) => `<div style="display:grid;grid-template-columns:330px 150px 340px 40px;align-items:center;padding:20px 0;border-bottom:1px solid rgba(255,255,255,.2);font:400 44px Serif;opacity:${i < (p.n ?? 99) ? 1 : 0}">
        <span>${r[0]}</span><span style="font:800 46px Cond;text-align:center;font-variant-numeric:tabular-nums">${r[1]}</span><span>${r[2]}</span><span style="color:${T.lime};font:600 30px Inter">✓</span></div>`).join('')}</div>
      <div class="mono" style="font-size:19px;color:${T.dim};margin-top:26px;opacity:${p.f === false ? 0 : ((p.n ?? 99) >= p.rows.length ? 1 : 0)}">${p.foot}</div></div>`,
  impact: p => `<div class="bg bw" style="background-image:url(${img(p.photo)});background-position:${p.pos || '62% 30%'}"></div><div class="vig"></div><div class="grain"></div>
    <div class="abs" style="left:${T.m}px;top:${p.top || 130}px;font:800 ${p.size || 250}px/.82 Cond;color:${T.lime};text-transform:uppercase;letter-spacing:-.01em">${p.big}</div>
    <div class="abs paper" style="left:${T.m + 6}px;bottom:130px;color:${T.ink};padding:12px 22px;font:600 20px Mono;letter-spacing:.18em">${p.label}</div>`,
  timeline: p => `<div class="abs n30" style="inset:0;background-color:#0e0e0e"></div><div class="grain"></div>
    <div class="abs mono" style="left:${T.m}px;top:110px;font-size:20px;color:${T.lime}">${p.title}</div>
    <div class="abs" style="left:${T.m}px;right:${T.m}px;top:700px;height:2px;background:rgba(255,255,255,.35)"></div>
    ${p.items.map((t, i) => { const x = T.m + i * 430, on = i === p.hi; return `<div class="abs" style="left:${x}px;top:250px;width:360px">
      <div style="background:#f5f2ea;padding:12px 12px 46px;transform:rotate(${[-2, 1.5, -1, 2][i % 4]}deg);box-shadow:0 18px 34px rgba(0,0,0,.6)"><div style="height:250px;background:url(${img(t[0])}) ${t[3] || 'center'}/cover;filter:grayscale(${on ? 0 : 1}) contrast(1.1)"></div>
      <div style="font:italic 400 25px Serif;color:#222;margin-top:12px">${t[2]}</div></div></div>
      <div class="abs" style="left:${x + 170}px;top:692px;width:18px;height:18px;border-radius:50%;background:${on ? T.lime : '#fff'};box-shadow:0 0 0 6px rgba(255,255,255,.08)"></div>
      <div class="abs mono" style="left:${x + 110}px;top:736px;font-size:20px;color:${on ? T.lime : '#ddd'}">${t[1]}</div>`; }).join('')}`,
  print: p => `<div class="abs n35" style="inset:0;background-color:#1a1916"></div><div class="grain"></div>
    <div class="abs" style="left:380px;top:110px;width:1160px;background:#f5f2ea;padding:24px 24px 90px;transform:rotate(${p.rot ?? -1.2}deg);box-shadow:0 40px 70px rgba(0,0,0,.65)">
      <div style="height:690px;background:url(${img(p.photo)}) ${p.pos || '50% 30%'}/cover;filter:contrast(1.08) saturate(.75) sepia(.12)${p.bw ? ' grayscale(1)' : ''}"></div>
      ${p.caption ? `<div style="display:flex;justify-content:space-between;align-items:baseline;margin-top:26px;color:#222"><span style="font:italic 400 36px Serif">${p.caption}</span><span class="mono" style="font-size:18px;color:#6b6860">${p.meta || ''}</span></div>` : ''}</div>`,
  // photo + lime circle on a face + leader line + label. cx, cy, r in 1920x1080 px (photo is full-bleed 16:9).
  callout: p => { const s = p.side === 'left' ? -1 : 1, bw = p.boxw || 470;
    const ax = p.cx + s * p.r * 0.72, ay = p.cy - p.r * 0.69, ly = Math.max(150, p.cy - p.r - 60);
    const bx = Math.max(120, Math.min(1920 - 120 - bw, s > 0 ? p.cx + p.r + 240 : p.cx - p.r - 240 - bw)), ex = s > 0 ? bx : bx + bw, kx = ex - s * 110;
    return `<div class="bg ${p.bw ? 'bw' : 'grade'}" style="background-image:url(${img(p.photo)});background-position:${p.pos || 'center'}"></div><div class="vig"></div><div class="grain"></div>
    <svg class="abs" style="left:0;top:0" width="1920" height="1080"><circle cx="${p.cx}" cy="${p.cy}" r="${p.r}" fill="none" stroke="${T.lime}" stroke-width="3"/>
      <path d="M${ax} ${ay} L${kx} ${ly} L${ex} ${ly}" fill="none" stroke="${T.lime}" stroke-width="2"/></svg>
    <div class="abs" style="left:${bx}px;top:${ly - 52}px;width:${bw}px;background:rgba(12,12,12,.82);padding:14px 22px 16px"><div style="font:400 46px Serif">${p.name}</div><div class="mono" style="font-size:17px;color:${T.dim};margin-top:8px">${p.meta}</div></div>`; },
  // two or three photos side by side (vertical photos in a 16:9 film). n = how many are revealed so far.
  duo: p => panels(p, 2), trio: p => panels(p, 3),
  end: p => `<div class="abs n30" style="inset:0;background-color:#0d0d0d"></div><div class="grain"></div>${marks()}
    <div class="abs" style="inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center">
      <div class="mono" style="font-size:20px;color:${T.lime}">${p.kicker || 'Thanks for watching'}</div>
      <div style="font:400 96px/1.08 Serif;margin:28px 0 8px">${p.title}</div>
      <div style="width:60px;height:2px;background:${T.lime};margin:30px 0 26px"></div>
      <div style="display:flex;align-items:center;gap:16px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.15);border-radius:999px;padding:14px 32px 14px 16px">
        <div style="width:48px;height:48px;border-radius:50%;background:${T.lime};display:flex;align-items:center;justify-content:center">${bell}</div><div style="font:600 30px Inter">Subscribe for the next story</div></div>
      <div class="mono" style="font-size:15px;color:#8d8a83;margin-top:70px;line-height:2;max-width:1400px">${p.credits}</div></div>`,
};
function panels(p, k) {
  const g = 10, w = (1920 - g * (k - 1)) / k;
  return `<div class="abs" style="inset:0;background:#0b0b0b"></div>` + p.photos.slice(0, k).map((ph, i) => `<div class="abs" style="left:${i * (w + g)}px;top:0;width:${w}px;height:1080px;overflow:hidden;opacity:${i < (p.n ?? k) ? 1 : 0}">
      <div class="abs" style="inset:0;background:url(${img(ph.photo)}) ${ph.pos || 'center'}/cover;filter:contrast(1.07) saturate(.84) brightness(.96)${ph.bw ? ' grayscale(1)' : ''}"></div>
      <div class="abs" style="inset:0;background:radial-gradient(ellipse at 50% 42%,transparent 55%,rgba(0,0,0,.5))"></div>
      ${ph.cap ? `<div class="abs mono" style="left:28px;bottom:34px;font-size:16px;color:#e6e3da;text-shadow:0 1px 6px #000">${ph.cap}</div>` : ''}</div>`).join('') + `<div class="grain"></div>`;
}
const page = (body, kind) => `<!doctype html><html><head><meta charset="utf-8"><style>${CSS}</style></head><body class="${kind}">${body}</body></html>`;
module.exports = { K, T, CSS, OV, PL, page, hl, mk };
