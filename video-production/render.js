// Renders every scene's graphics layer frame-by-frame with headless Chromium.
// Full-frame studio graphics -> JPEG; overlays for stock footage -> transparent PNG.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const ROOT = __dirname, NM = ROOT + '/node_modules', B = ROOT + '/build';
const TL = JSON.parse(fs.readFileSync(B + '/timeline.json'));
const FPS = TL.fps;
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const d = x => `animation-delay:${(+x).toFixed(2)}s`;
const fit = (txt, max, width, k = 0.42) => Math.round(Math.min(max, width / (Math.max(...[].concat(txt).map(t => t.length)) * k)));

const CSS = `
@font-face{font-family:Bebas;src:url(file://${NM}/@fontsource/bebas-neue/files/bebas-neue-latin-400-normal.woff2)}
@font-face{font-family:Bebas;src:url(file://${NM}/@fontsource/bebas-neue/files/bebas-neue-latin-ext-400-normal.woff2);unicode-range:U+0100-024F}
@font-face{font-family:Osw;font-weight:500;src:url(file://${NM}/@fontsource/oswald/files/oswald-latin-500-normal.woff2)}
@font-face{font-family:Osw;font-weight:700;src:url(file://${NM}/@fontsource/oswald/files/oswald-latin-700-normal.woff2)}
@font-face{font-family:Osw;font-weight:500;src:url(file://${NM}/@fontsource/oswald/files/oswald-latin-ext-500-normal.woff2);unicode-range:U+0100-024F}
@font-face{font-family:Osw;font-weight:700;src:url(file://${NM}/@fontsource/oswald/files/oswald-latin-ext-700-normal.woff2);unicode-range:U+0100-024F}
:root{--amber:#C6FF00;--navy:#0A0A0A;--sky:#FFFFFF;--red:#FF5247;--ink:#CFCFCF}
*{box-sizing:border-box;animation-fill-mode:both!important}
html,body{margin:0;width:1920px;height:1080px;overflow:hidden;color:#fff;font-family:Inter,sans-serif}
.abs{position:absolute;inset:0}
.studio{background:radial-gradient(ellipse at 50% 32%,#1d1d1d 0%,#0b0b0b 46%,#000 100%)}
.grid{position:absolute;inset:-60px;background-image:radial-gradient(rgba(198,255,0,.10) 1.4px,transparent 1.7px);background-size:28px 28px;-webkit-mask-image:radial-gradient(ellipse at 50% 42%,#000 18%,transparent 74%);animation:drift calc(var(--D)*1s) linear}
@keyframes drift{to{transform:translate(-42px,-21px)}}
.blob{position:absolute;width:1300px;height:1300px;border-radius:50%}
.b1{left:-500px;bottom:-700px;background:radial-gradient(circle,rgba(198,255,0,.20),transparent 62%);animation:bl1 calc(var(--D)*1s) linear}
.b2{right:-450px;top:-650px;background:radial-gradient(circle,rgba(198,255,0,.10),transparent 62%);animation:bl2 calc(var(--D)*1s) linear}
@keyframes bl1{to{transform:translate(160px,-60px)}}@keyframes bl2{to{transform:translate(-160px,70px)}}
.panel{position:absolute;top:-10%;width:240px;height:120%;background:linear-gradient(90deg,transparent,rgba(255,255,255,.05),transparent);transform:skewX(-14deg)}
.floor{position:absolute;left:0;right:0;bottom:0;height:300px;background:linear-gradient(transparent,rgba(198,255,0,.05))}
.vig{background:radial-gradient(ellipse at 50% 50%,transparent 55%,rgba(0,0,0,.55) 100%)}
.ovig{background:linear-gradient(to bottom,rgba(0,0,0,.62),rgba(0,0,0,.12) 24%,rgba(0,0,0,.18) 52%,rgba(0,0,0,.9))}
.flash{background:#fff;animation:flash .3s ease-out;z-index:99}@keyframes flash{from{opacity:.5}to{opacity:0}}
.hud{font:700 25px Osw;letter-spacing:5px}
.hud .tl{position:absolute;left:70px;top:52px;display:flex;align-items:center;gap:14px;color:#f0f0f0}
.hud .tl i{width:14px;height:14px;background:var(--red);border-radius:50%;animation:blink 1.2s steps(2) infinite}
@keyframes blink{50%{opacity:.25}}
.hud .tr{position:absolute;right:70px;top:44px;border:2px solid rgba(255,255,255,.75);padding:6px 16px 5px;color:#fff;font-size:27px}
.hud .tr b{color:var(--amber)}
.hud .bl{position:absolute;left:70px;right:70px;bottom:44px;display:flex;justify-content:space-between;color:#a8a8a8;font-size:23px}
.hud .ln{position:absolute;left:70px;right:70px;bottom:84px;height:2px;background:linear-gradient(90deg,var(--amber) 0 180px,rgba(255,255,255,.22) 180px);transform-origin:left;animation:gl .8s cubic-bezier(.2,.8,.2,1)}
.c{position:absolute;inset:120px 150px 140px 150px;display:flex;flex-direction:column;justify-content:center}
.bebas{font-family:Bebas;font-weight:400;line-height:.92;letter-spacing:2px}
.kick{font:700 30px Osw;letter-spacing:9px;color:var(--amber)}
.sub{font:500 36px Osw;letter-spacing:6px;color:var(--ink)}
.pill{display:inline-block;align-self:flex-start;background:var(--amber);color:#0a0a0a;font:700 27px Osw;letter-spacing:6px;padding:8px 20px 7px}
.fu{animation:fu .65s cubic-bezier(.2,.8,.2,1)}@keyframes fu{from{opacity:0;transform:translateY(46px)}to{opacity:1;transform:none}}
.fi{animation:fi .6s ease-out}@keyframes fi{from{opacity:0}to{opacity:1}}
.wr{animation:wr .7s cubic-bezier(.2,.8,.2,1)}@keyframes wr{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 -5% 0 0)}}
.gl{transform-origin:left;animation:gl .7s cubic-bezier(.2,.8,.2,1)}@keyframes gl{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.gu{transform-origin:bottom;animation:gu .8s cubic-bezier(.2,.8,.2,1)}@keyframes gu{from{transform:scaleY(0)}to{transform:scaleY(1)}}
.pop{animation:pop .5s cubic-bezier(.2,1.6,.4,1)}@keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:scale(1)}}
.trk{animation:trk 1.1s cubic-bezier(.2,.8,.2,1)}@keyframes trk{from{opacity:0;letter-spacing:.35em}to{opacity:1}}
.stampA{animation:stampA .32s cubic-bezier(.3,1.5,.5,1)}@keyframes stampA{from{opacity:0;transform:rotate(-9deg) scale(2.6)}to{opacity:1;transform:rotate(-9deg) scale(1)}}
.stamp{display:inline-block;font:400 120px Bebas;letter-spacing:8px;color:var(--red);border:9px solid var(--red);padding:6px 34px 0;border-radius:8px;transform:rotate(-9deg)}
.push{animation:push calc(var(--D)*1s) linear}@keyframes push{from{transform:scale(1)}to{transform:scale(1.045)}}
.bar{height:8px;background:var(--amber)}
.box{background:rgba(16,16,16,.88);border:2px solid rgba(255,255,255,.35);padding:26px 40px;box-shadow:0 20px 60px rgba(0,0,0,.45)}
.hot{border-color:var(--amber)!important}
.mono{font-family:'JetBrains Mono',monospace}
`;

const STUDIO = `<div class="abs studio"><div class="grid"></div><div class="blob b1"></div><div class="blob b2"></div><div class="panel" style="left:5%"></div><div class="panel" style="right:5%"></div><div class="floor"></div><div class="abs vig"></div></div>`;
let studio = STUDIO;
const SCRIM = (o) => `<div class="abs" style="background:linear-gradient(to bottom,rgba(0,0,0,${o}),rgba(0,0,0,${o - .1}) 45%,rgba(0,0,0,${o}))"></div>`;
const hud = s => s.label ? `<div class="abs hud"><div class="tl"><i></i>SPECIAL REPORT</div><div class="tr">THE <b>115</b> FILES</div><div class="ln"></div><div class="bl"><span>${esc(s.label)}</span><span>FOOTBALL LEAKS · CASE FILE</span></div></div>` : '';
const trophy = `<svg viewBox="0 0 100 116" width="170"><g fill="#C6FF00"><path d="M26 6h48v32a24 24 0 0 1-48 0z"/><rect x="44" y="60" width="12" height="24"/><rect x="28" y="84" width="44" height="10" rx="2"/><rect x="20" y="96" width="60" height="14" rx="2"/></g><g fill="none" stroke="#C6FF00" stroke-width="7"><path d="M26 14H10v8a18 18 0 0 0 18 18"/><path d="M74 14h16v8a18 18 0 0 1-18 18"/></g></svg>`;
const person = `<svg viewBox="0 0 100 100" width="150"><circle cx="50" cy="50" r="48" fill="#151515" stroke="#9a9a9a" stroke-width="2"/><circle cx="50" cy="40" r="17" fill="#9a9a9a"/><path d="M18 88a32 28 0 0 1 64 0z" fill="#9a9a9a"/></svg>`;
const hl = t => esc(t).replace(/\*(.+?)\*/g, '<span class="hl">$1</span>');

const T = {
  quote: (g, D) => `<div class="abs" style="background:radial-gradient(ellipse at 50% 45%,#161616,#000 75%)"></div><div class="c" style="align-items:center;text-align:center">
    <div class="bebas fi" style="font-size:300px;color:var(--amber);height:150px;${d(.2)}">“</div>
    <div style="font:600 82px/1.22 'Inter Display',Inter"><div class="fu" style="${d(.6)}">Football is not for sale.</div><div class="fu" style="${d(2.7)}">Not today, not tomorrow,</div><div class="fu" style="color:var(--amber);${d(4.3)}">and not ever.</div></div>
    <div class="bar gl" style="width:160px;margin:54px 0 26px;${d(5.2)}"></div><div class="sub fi" style="${d(5.4)}">${esc(g.by)}</div></div>`,
  sting: (g, D) => `<div class="abs" style="background:#000000"></div><div class="abs studio fi" style="${d(.9)}"><div class="grid"></div><div class="blob b2"></div><div class="abs vig"></div></div>
    <div class="abs bebas fi" style="display:flex;align-items:center;justify-content:center;font-size:980px;color:transparent;-webkit-text-stroke:3px rgba(198,255,0,.16);${d(1)}"><span class="push">115</span></div>
    <div class="c" style="align-items:center;text-align:center"><div class="bar gl" style="width:1300px;height:6px;animation-duration:.9s;transform-origin:center"></div>
    <div class="bebas trk" style="font-size:270px;margin:34px 0 10px;text-shadow:0 0 60px rgba(198,255,0,.3);${d(.9)}">${esc(g.title)}</div>
    <div class="bar gl" style="width:1300px;height:6px;transform-origin:center;${d(1.2)}"></div><div class="sub fu" style="margin-top:40px;font-size:40px;${d(1.9)}">${esc(g.sub)}</div></div>
    <div class="abs flash" style="${d(.9)}"></div>`,
  bumper: (g, D) => `${studio}<div class="abs" style="display:flex;align-items:center;padding:0 150px;gap:70px">
    <div class="bebas fu" style="font-size:560px;color:transparent;-webkit-text-stroke:5px var(--amber);${d(.1)}">${g.num}</div>
    <div><div class="kick fi" style="${d(.45)}">CHAPTER ${g.num}</div><div class="bebas wr" style="font-size:${fit(g.title, 190, 1050)}px;margin:14px 0 24px;${d(.5)}">${esc(g.title)}</div><div class="bar gl" style="width:520px;${d(.8)}"></div></div></div>`,
  bigtext: (g, D) => { const t0 = (g.late || 0) * D, fs = fit(g.lines, 330, 1640);
    return `${g.bare ? SCRIM(.9) : studio}<div class="c" style="align-items:center;text-align:center">
    ${g.kicker ? `<div class="pill fu" style="align-self:center;margin-bottom:34px;${d(.2)}">${esc(g.kicker)}</div>` : ''}
    ${g.lines.map((l, i) => `<div class="bebas ${g.bare ? 'fi' : 'trk'}" style="font-size:${fs}px;${g.sky && i ? 'color:var(--sky);' : ''}${d(t0 + .15 + i * .35)}">${esc(l)}</div>`).join('')}
    ${g.sub ? `<div class="bar gl" style="width:200px;margin:34px 0 22px;${d(t0 + .9)}"></div><div class="sub fu" style="${d(t0 + 1)}">${esc(g.sub)}</div>` : ''}</div>`; },
  counter: (g, D) => { const t0 = (g.t0 || .08) * D, t1 = t0 + Math.min(2.4, D * .3), txt = (g.prefix || '') + g.value.toLocaleString('en-US') + (g.suffix || ''), fs = fit(txt, 340, 1640, .44);
    return `${studio}<div class="c" style="align-items:center;text-align:center"><div class="kick fu" style="font-size:38px;${d(Math.max(.2, t0 - .5))}">${esc(g.label)}</div>
    <div class="bebas fi" style="font-size:${fs}px;margin:26px 0 8px;font-variant-numeric:tabular-nums;text-shadow:0 0 70px rgba(198,255,0,.28);${d(t0)}">${g.prefix || ''}<span data-count="${g.value}" data-t0="${t0}" data-t1="${t1}">0</span><span style="color:var(--amber)">${esc(g.suffix || '')}</span></div>
    <div class="bar gl" style="width:520px;${d(t1)}"></div>${g.sub ? `<div class="sub fu" style="margin-top:34px;font-size:42px;color:#fff;${d(Math.max(t1 + .2, (g.sublate || 0) * D))}">${esc(g.sub)}</div>` : ''}</div>`; },
  icons: (g, D) => `${studio}<div class="c" style="align-items:center"><div style="display:flex;gap:60px">${Array.from({ length: g.count }, (_, i) => `<div class="pop" style="${d(.2 + i * .28)}">${trophy}</div>`).join('')}</div>
    <div class="bebas fu" style="font-size:150px;margin-top:54px;${d(.5)}"><span style="color:var(--amber)">${g.count}</span> ${esc(g.label)}</div><div class="sub fu" style="${d(1.3)}">${esc(g.sub)}</div></div>`,
  trend: (g, D) => { const n = g.data.length, mx = Math.max(...g.data.map(x => x[1])); return `${studio}<div class="c"><div class="kick fu" style="${d(.2)}">RECORD AFTER RECORD</div><div class="bebas fu" style="font-size:120px;margin:10px 0 20px;${d(.3)}">${esc(g.title)}</div>
    <div style="display:flex;align-items:flex-end;gap:40px;height:500px;border-bottom:3px solid rgba(255,255,255,.4);padding:0 20px">${g.data.map((x, i) => `<div style="flex:1;height:100%;display:flex;flex-direction:column;justify-content:flex-end"><div class="bebas fu" style="font-size:76px;text-align:center;${i === n - 1 ? 'color:var(--amber);' : ''}${d(1.1 + i * (D * .6 / n))}">£${x[1]}M</div><div class="gu" style="height:${Math.round(78 * x[1] / mx)}%;background:linear-gradient(${i === n - 1 ? '#C6FF00,#86ad00' : '#f4f4f4,#8c8c8c'});${d(.8 + i * (D * .6 / n))}"></div></div>`).join('')}</div>
    <div style="display:flex;gap:40px;padding:10px 20px 0">${g.data.map(x => `<div class="sub" style="flex:1;text-align:center;font-size:30px;color:#fff">${x[0]}</div>`).join('')}</div>
    <div class="fi" style="font:500 22px Osw;letter-spacing:4px;color:#9a9a9a;margin-top:14px;text-align:right;${d(1)}">${esc(g.note)}</div></div>`; },
  list: (g, D) => { const n = g.items.length, at = i => (g.ats ? g.ats[i] : (g.t0 || .2) + (.88 - (g.t0 || .2)) * i / n) * D;
    return `${studio}<div class="c"><div class="pill fu" style="${d(.2)}">${esc(g.tag)}</div><div class="bebas fu" style="font-size:${fit(g.title, 170, 1500, .46)}px;margin:22px 0 14px;${d(.35)}">${esc(g.title)}</div><div class="bar gl" style="width:260px;margin-bottom:34px;${d(.6)}"></div>
    ${g.items.map((it, i) => `<div class="fu" style="display:flex;align-items:baseline;gap:30px;margin:13px 0;${d(at(i))}"><span class="bebas" style="font-size:54px;color:var(--amber);width:70px">0${i + 1}</span><span style="font:600 ${n > 3 ? 54 : 58}px 'Inter Display',Inter;${g.lasthot && i === n - 1 ? 'color:var(--amber)' : ''}">${esc(it)}</span></div>`).join('')}
    ${g.stamp ? `<div style="position:absolute;right:0;bottom:70px"><div class="stamp stampA" style="${d((g.stampat || .7) * D)}">${esc(g.stamp)}</div></div>` : ''}</div>`; },
  define: (g, D) => `${studio}<div class="c" style="flex-direction:row;align-items:center;gap:80px"><div class="bebas trk" style="font-size:${g.small ? 210 : 400}px;color:var(--amber);flex:none;${g.small ? 'width:640px;line-height:.86;' : ''}${d(.25)}">${esc(g.term)}</div>
    <div style="border-left:4px solid rgba(255,255,255,.35);padding-left:70px"><div class="kick fu" style="font-size:34px;${d(.7)}">${esc(g.full)}</div><div class="fu" style="font:600 62px/1.22 'Inter Display',Inter;margin-top:26px;${d(Math.max(1.1, D * .3))}">${esc(g.body)}</div>
    ${g.stamp ? `<div style="margin-top:50px"><div class="stamp stampA" style="${d(D * .68)}">${esc(g.stamp)}</div></div>` : ''}</div></div>`,
  doc: (g, D) => `${studio}<style>.hl{background:linear-gradient(#C6FF00,#C6FF00) no-repeat 0 60%/0% 78%;animation:hlA .9s ease-out ${(D * .42).toFixed(2)}s both;padding:0 6px}@keyframes hlA{to{background-size:100% 78%}}</style>
    <div class="abs" style="display:flex;flex-direction:column;align-items:center;justify-content:center"><div class="push"><div class="fu" style="width:1320px;background:#f2efe6;color:#1a1d26;padding:60px 80px 70px;transform:rotate(-1.4deg);box-shadow:0 40px 90px rgba(0,0,0,.6);${d(.15)}">
    <div style="display:flex;justify-content:space-between;font:700 22px 'JetBrains Mono';letter-spacing:3px;color:#666b7a;border-bottom:2px solid #c9c5b8;padding-bottom:18px;margin-bottom:40px"><span>${esc(g.head)}</span><span style="color:#b3261e">ILLUSTRATIVE RECREATION</span></div>
    <div style="font:400 62px/1.42 'Liberation Serif',serif">${g.lines.map(l => `<div>${hl(l)}</div>`).join('')}</div></div></div>
    ${g.foot ? `<div class="bebas fu" style="font-size:84px;color:var(--amber);margin-top:50px;${d(D * .76)}">${esc(g.foot)}</div>` : ''}</div>`,
  flow: (g, D) => `${studio}<div class="c"><div class="kick fu" style="${d(.2)}">${esc(g.title)}</div><div style="display:flex;align-items:center;justify-content:space-between;margin-top:50px">
    ${g.nodes.map((n, i) => `<div class="box fu" style="width:480px;text-align:center;padding:50px 20px;${d(.3 + i * .3)}"><div class="bebas" style="font-size:92px">${esc(n.l)}</div><div class="sub" style="font-size:26px;margin-top:8px">${esc(n.s)}</div></div>`).join(`<div style="flex:1;padding:0 30px;text-align:center">
      <div class="bebas fu" style="font-size:74px;white-space:nowrap;color:var(--amber);${d(D * .22)}">${esc(g.fwd)}</div><div class="gl" style="height:8px;background:var(--amber);position:relative;${d(D * .22)}"><i style="position:absolute;right:-4px;top:-14px;border:18px solid transparent;border-left-color:var(--amber);border-right:0"></i></div>
      <div class="gl" style="height:8px;background:var(--sky);position:relative;margin-top:70px;transform-origin:right;${d(D * .55)}"><i style="position:absolute;left:-4px;top:-14px;border:18px solid transparent;border-right-color:var(--sky);border-left:0"></i></div><div class="fu" style="font:700 27px Osw;letter-spacing:2px;white-space:nowrap;color:var(--sky);margin-top:20px;${d(D * .55)}">${esc(g.back)}</div></div>`)}</div></div>`,
  flow3: (g, D) => { const t0 = (g.late || .08) * D, st = Math.min(1.6, D * .16);
    return `${studio}<div class="c"><div class="kick fu" style="${d(.2)}">${esc(g.title)}</div><div style="display:flex;align-items:center;margin-top:50px">
    ${g.nodes.map((n, i) => `<div class="box fu ${i === 2 ? 'hot' : ''}" style="flex:1;text-align:center;padding:54px 10px;${d(t0 + i * st)}"><div class="bebas" style="font-size:${fit(n, 88, 430)}px">${esc(n)}</div></div>`).join('|').split('|').map((x, i) => i ? `<div class="gl" style="width:120px;height:8px;background:var(--amber);position:relative;margin:0 22px 0 8px;${d(t0 + i * st - .3)}"><i style="position:absolute;right:-16px;top:-14px;border:18px solid transparent;border-left-color:var(--amber);border-right:0"></i></div>` + x : x).join('')}</div>
    <div class="bebas fu" style="font-size:${fit(g.foot, 96, 1300)}px;color:var(--amber);text-align:center;margin-top:70px;${d(Math.max(t0 + 3 * st, D * .7))}">${esc(g.foot)}</div></div>`; },
  org: (g, D) => `${studio}<div class="c" style="align-items:center">${g.nodes.map((n, i) => `${i ? `<div class="gu" style="width:6px;height:44px;background:var(--amber);transform-origin:top;${d(.2 + i * .55)}"></div>` : ''}<div class="box fu ${i === g.nodes.length - 1 ? 'hot' : ''}" style="width:760px;text-align:center;padding:20px;${d(.3 + i * .55)}"><div class="bebas" style="font-size:78px;${i === g.nodes.length - 1 ? 'color:var(--sky)' : ''}">${esc(n)}</div></div>`).join('')}
    <div class="fu" style="position:absolute;right:0;top:54%;width:330px;font:700 30px/1.4 Osw;letter-spacing:4px;color:var(--amber);border-left:4px solid var(--amber);padding-left:22px;${d(D * .5)}">${esc(g.side).replace(' · ', '<br><span style="color:#fff">')}</span></div></div>`,
  names: (g, D) => `${studio}<div class="c"><div class="kick fu" style="${d(.2)}">${esc(g.title)}</div><div style="display:flex;gap:44px;margin-top:50px">${g.people.map((p, i) => `<div class="box fu ${p.hot ? 'hot' : ''}" style="flex:1;text-align:center;padding:50px 16px;${d(([.3, .42, .74][i]) * D)}">${p.hot ? `<div class="bebas" style="font-size:150px;color:var(--amber);height:150px">115</div>` : person}<div class="bebas" style="font-size:${fit(p.n, 76, 470)}px;margin-top:28px">${esc(p.n)}</div><div class="sub" style="font-size:26px;margin-top:8px;${p.hot ? 'color:var(--amber)' : ''}">${esc(p.r)}</div></div>`).join('')}</div></div>`,
  terminal: (g, D) => { const n = g.lines.length, st = D * .78 / n;
    return `${studio}<div class="c" style="align-items:center"><div class="fu" style="width:1400px;background:rgba(0,0,0,.93);border:2px solid #3a3a3a;box-shadow:0 30px 90px rgba(0,0,0,.6);${d(.1)}">
    <div class="mono" style="display:flex;gap:10px;align-items:center;padding:16px 22px;background:#151515;font-size:22px;letter-spacing:4px;color:#a8a8a8"><i style="width:14px;height:14px;border-radius:50%;background:var(--red)"></i><i style="width:14px;height:14px;border-radius:50%;background:var(--amber)"></i><i style="width:14px;height:14px;border-radius:50%;background:#3ddc84"></i><span style="margin-left:16px">${esc(g.title)}</span></div>
    <div class="mono" style="padding:40px 50px 50px;font-size:42px;line-height:1.7;color:#C6FF00;min-height:${n * 72 + 90}px">${g.lines.map((l, i) => `<div style="${i === n - 1 ? 'color:#fff' : ''}" data-type="${esc(l)}" data-t0="${(.4 + i * st).toFixed(2)}" data-cps="${Math.max(30, l.length / (st * .7)).toFixed(0)}"></div>`).join('')}</div></div></div>`; },
  bars: (g, D) => { const mx = Math.max(...g.items.map(i => i.v));
    return `${studio}<div class="c"><div class="kick fu" style="${d(.2)}">${esc(g.title)}</div>${g.items.map(it => `<div class="fu" style="margin-top:56px;${d(it.at * D)}"><div class="sub" style="font-size:34px;margin-bottom:14px">${esc(it.l)}</div><div style="display:flex;align-items:center;gap:36px"><div class="gl" style="height:120px;width:${Math.max(18, Math.round(1150 * it.v / mx))}px;background:${it.hot ? 'var(--red)' : 'linear-gradient(90deg,#8c8c8c,#f4f4f4)'};animation-duration:1.1s;${d(it.at * D + .2)}"></div><div class="bebas" style="font-size:170px;${it.hot ? 'color:var(--red)' : ''}">${esc(it.d)}</div></div></div>`).join('')}</div>`; },
  pitch: (g, D) => { const t0 = (g.late || .06) * D, two = g.parts.length > 1, fs = two ? 170 : fit(g.parts[0].t, 520, 860, .42);
    return `<div class="abs" style="background:#000000"></div><div class="abs" style="perspective:1500px"><div class="abs" style="transform:rotateX(46deg) scale(1.75) translateY(-40px);transform-style:preserve-3d"><div class="abs push" style="background:url(file://${B}/pitch.jpg) center/cover;animation-name:pp"></div>
    <div class="abs" style="display:flex;align-items:center;justify-content:center;gap:${two ? 70 : 0}px">${g.parts.map((p, i) => `<div class="bebas wr" style="font-size:${fs}px;letter-spacing:10px;color:${p.hot ? '#C6FF00' : 'rgba(255,255,255,.93)'};text-shadow:0 0 30px rgba(0,0,0,.35);${d(t0 + i * Math.min(2.2, D * .3))}">${esc(p.t)}</div>`).join('')}</div></div></div>
    <style>@keyframes pp{from{transform:scale(1.02)}to{transform:scale(1.12) rotate(1.5deg)}}</style>
    <div class="abs" style="background:linear-gradient(to bottom,rgba(0,0,0,.96) 0%,rgba(0,0,0,.2) 34%,transparent 60%,rgba(0,0,0,.9) 100%)"></div>
    <div class="abs" style="display:flex;justify-content:${two ? 'space-around' : 'center'};align-items:flex-end;padding:0 200px 150px">${g.parts.map((p, i) => `<div class="fu" style="text-align:center;${d(t0 + .5 + i * Math.min(2.2, D * .3))}"><div class="bar" style="width:140px;margin:0 auto 18px;${p.hot ? '' : 'background:#fff'}"></div><div class="sub" style="font-size:36px;color:${p.hot ? 'var(--amber)' : '#fff'}">${esc(p.s)}</div></div>`).join('')}</div>`; },
  map: (g, D) => `${studio}<div id="mw" class="abs" style="transform-origin:0 0"><svg id="map" width="1920" height="1080"></svg></div><div class="abs" style="background:linear-gradient(to bottom,rgba(0,0,0,.85),transparent 26%,transparent 70%,rgba(0,0,0,.9))"></div>
    <div style="position:absolute;left:150px;top:120px"><div class="kick fu" style="${d(.2)}">LOCATION</div><div class="bebas fu" style="font-size:${fit(g.title, 130, 1300)}px;margin-top:6px;${d(.3)}">${esc(g.title)}</div>${g.foot ? `<div class="bebas fu" style="font-size:72px;color:var(--amber);margin-top:6px;${d((g.footlate || .6) * D)}">${esc(g.foot)}</div>` : ''}</div>
    
    <script src="file://${NM}/d3-array/dist/d3-array.min.js"></script><script src="file://${NM}/d3-geo/dist/d3-geo.min.js"></script><script src="file://${NM}/topojson-client/dist/topojson-client.min.js"></script><script src="file://${B}/world.js"></script>
    <script>(()=>{const g=${JSON.stringify(g)},D=${D};const pr=d3.geoMercator().center(g.center).scale(g.scale).translate([1100,570]),pa=d3.geoPath(pr);
    const fs=topojson.feature(WORLD,WORLD.objects.countries).features;let h='<path d="'+pa(d3.geoGraticule10())+'" fill="none" stroke="rgba(255,255,255,.07)"/>';
    for(const f of fs){const p=pa(f);if(p)h+='<path d="'+p+'" fill="#1b1b1b" stroke="#4a4a4a" stroke-width="1.2"/>'}
    const P=g.pins.map(p=>pr([p.lon,p.lat]));const rt=(g.late||.12)*D;
    if(g.route){const[a,b]=[P[g.route[0]],P[g.route[1]]],mx=(a[0]+b[0])/2,my=(a[1]+b[1])/2-Math.hypot(b[0]-a[0],b[1]-a[1])*.22;
      h+='<path pathLength="1" d="M'+a+' Q'+mx+' '+my+' '+b+'" fill="none" stroke="#C6FF00" stroke-width="6" stroke-linecap="round" stroke-dasharray="1" style="animation:dash 1.7s ease-in-out '+rt+'s both"/>'}
    g.pins.forEach((p,i)=>{const[x,y]=P[i],t=g.route?(i===g.route[0]?Math.max(.3,rt-.6):rt+1.5):.5+i*Math.min(1.6,D*.16),left=x>1380,w=p.n.length*24+50;
      const lx=p.below?x-w/2:(left?x-w-34:x+34),ly=p.below?y+40:y-36;
      h+='<g style="animation:fi .5s ease-out '+t+'s both"><circle cx="'+x+'" cy="'+y+'" r="34" fill="none" stroke="#C6FF00" stroke-width="3" style="transform-origin:'+x+'px '+y+'px;animation:ring 1.6s ease-out '+t+'s infinite"/><circle cx="'+x+'" cy="'+y+'" r="13" fill="#C6FF00" stroke="#fff" stroke-width="4"/>'
       +'<rect x="'+lx+'" y="'+ly+'" width="'+w+'" height="72" fill="#0c0c0c" stroke="#C6FF00" stroke-width="2"/><text x="'+(lx+22)+'" y="'+(ly+51)+'" fill="#fff" font-family="Osw" font-weight="700" font-size="40" letter-spacing="3">'+p.n.replace(/&/g,'&amp;')+'</text></g>'});
    document.getElementById('map').innerHTML=h;const st=document.createElement('style');let css='@keyframes dash{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}@keyframes ring{from{transform:scale(.4);opacity:1}to{transform:scale(1.9);opacity:0}}';
    const mw=document.getElementById('mw');
    if(g.zoom!=null){const[x,y]=P[g.zoom],k=g.k||2;css+='@keyframes mz{to{transform:translate('+(960-x*k)+'px,'+(600-y*k)+'px) scale('+k+')}}';mw.style.animation='mz '+D+'s cubic-bezier(.3,.5,.2,1) both'}
    else if(g.shake){css+='@keyframes mz{0%,100%{transform:none}10%{transform:translate(-14px,9px)}20%{transform:translate(12px,-10px)}30%{transform:translate(-10px,-8px)}40%{transform:translate(9px,11px)}50%{transform:translate(-7px,5px)}60%{transform:translate(6px,-5px)}70%{transform:translate(-4px,3px)}85%{transform:translate(2px,-2px)}}';mw.style.animation='mz 1.5s linear 1.1s both'}
    else{css+='@keyframes mz{from{transform:scale(1)}to{transform:translate(-48px,-27px) scale(1.05)}}';mw.style.animation='mz '+D+'s linear both'}
    st.textContent=css;document.head.appendChild(st)})()</script>`,
  end: (g, D) => `${studio}<div class="c" style="flex-direction:row;gap:70px;inset:90px 110px"><div style="flex:1;display:flex;flex-direction:column;justify-content:center">
    <div class="kick fu" style="${d(.3)}">SPECIAL REPORT</div><div class="bebas fu" style="font-size:190px;margin:8px 0 18px;${d(.4)}">THE <span style="color:var(--amber)">115</span> FILES</div><div class="bar gl" style="width:300px;margin-bottom:40px;${d(.7)}"></div>
    ${[['NARRATION & MUSIC', 'AI-generated'], ['FOOTAGE', 'News archive footage · Pexels'], ['BASED ON REPORTING BY', 'Football Leaks · EIC · Der Spiegel'], ['GRAPHICS', 'Illustrative recreations']].map((r, i) => `<div class="fu" style="margin:11px 0;${d(1 + i * .25)}"><div class="kick" style="font-size:22px;letter-spacing:6px">${r[0]}</div><div style="font:500 34px Inter;color:#f0f0f0">${r[1]}</div></div>`).join('')}</div>
    <div style="width:820px;display:flex;flex-direction:column;justify-content:center;gap:40px">${[0, 1].map(i => `<div class="fu" style="height:330px;border:3px solid rgba(255,255,255,.55);border-radius:18px;background:rgba(14,14,14,.6);display:flex;align-items:center;justify-content:center;${d(1.2 + i * .3)}"><span class="kick" style="color:#a8a8a8">WATCH NEXT</span></div>`).join('')}</div></div>`,
  article: (g, D) => `${STUDIO}<div class="abs" style="display:flex;flex-direction:column;align-items:center;justify-content:center"><div class="push"><div class="fu" style="position:relative;width:1560px;background:#fff;padding:26px 30px 30px;transform:rotate(-1.2deg);box-shadow:0 40px 100px rgba(0,0,0,.7);${d(.15)}">
    <div style="display:flex;justify-content:space-between;font:700 22px 'JetBrains Mono';letter-spacing:3px;color:#555;border-bottom:2px solid #ddd;padding-bottom:14px;margin-bottom:14px"><span>${esc(g.tag)}</span><span>HEADLINE AS PUBLISHED</span></div>
    <div style="position:relative;line-height:0"><img src="file://${B}/${g.img}" style="width:100%">${g.marks.map(m => `<div style="position:absolute;left:${m[0] * 100}%;top:${m[1] * 100}%;width:${m[2] * 100}%;height:${m[3] * 100}%;background:#C6FF00;mix-blend-mode:multiply;transform-origin:left;animation:gl .7s cubic-bezier(.3,.7,.2,1) ${(m[4] * D).toFixed(2)}s both"></div>`).join('')}</div>
    ${g.stamp ? `<div style="position:absolute;right:60px;bottom:-40px"><div class="stamp stampA" style="background:rgba(255,255,255,.92);${d(g.stampat * D)}">${esc(g.stamp)}</div></div>` : ''}</div></div>
    ${g.foot ? `<div class="bebas fu" style="font-size:84px;color:var(--amber);margin-top:70px;${d(g.footat * D)}">${esc(g.foot)}</div>` : ''}</div>`,
  // ---------- transparent overlays for stock footage ----------
  caps: (g, D) => `<div class="abs" style="background:linear-gradient(to bottom,rgba(0,0,0,.55),transparent 24%,transparent 44%,rgba(0,0,0,.93))"></div>
    <div style="position:absolute;left:190px;top:112px">${g.name ? `<div class="wr" style="display:inline-flex;${d(.2)}"><div style="width:16px;background:var(--amber)"></div><div class="bebas" style="background:#0a0a0a;font-size:84px;padding:12px 34px 2px;letter-spacing:3px">${esc(g.name)}</div></div><br>` : ''}
    ${g.role ? `<div class="wr" style="display:inline-block;background:#fff;color:#0a0a0a;font:700 32px Inter;padding:12px 26px;${d(.45)}">${esc(g.role)}</div>` : ''}</div>
    ${g.role ? `<div class="fi" style="position:absolute;right:200px;top:104px;font:700 24px Osw;letter-spacing:5px;color:#f0f0f0;background:rgba(0,0,0,.55);border:2px solid rgba(255,255,255,.6);padding:6px 14px;${d(.3)}">ARCHIVE</div>` : ''}
    <style>.hw{background:var(--amber);color:#0a0a0a;padding:0 18px;display:inline-block;transform:skewX(-4deg)}@keyframes fo{from{opacity:1}to{opacity:0}}</style>
    ${g.phrases.map(p => `<div class="abs pop" style="animation-duration:.22s;${d(p.t0)}"><div style="position:absolute;left:220px;right:220px;bottom:150px;text-align:center;animation:fo .15s linear ${p.t1.toFixed(2)}s both">
      <div class="bebas" style="font-size:${p.q ? 92 : 150}px;line-height:1.04;${p.q ? 'color:#e6e6e6;' : ''}text-shadow:0 6px 40px rgba(0,0,0,.9)">${p.q ? '<span style="color:var(--amber)">Q · </span>' : ''}${esc(p.text).replace(/\*(.+?)\*/g, '<span class="hw">$1</span>')}</div></div></div>`).join('')}`,
  none: () => '',
  stat: (g, D) => { const t0 = (g.late || .08) * D; return `<div style="position:absolute;left:150px;bottom:160px"><div class="bebas wr" style="font-size:300px;text-shadow:0 8px 50px rgba(0,0,0,.7);${d(t0)}">${esc(g.big)}</div><div class="bar gl" style="width:260px;margin:4px 0 22px;${d(t0 + .4)}"></div><div class="sub fu" style="color:#fff;font-size:40px;text-shadow:0 2px 14px #000;${d(t0 + .5)}">${esc(g.label)}</div></div>`; },
  word: (g, D) => { const t0 = (g.late || .1) * D, fs = fit(g.text, 360, 1560);
    return `<div class="abs fi" style="background:rgba(0,0,0,.38);${d(Math.max(0, t0 - .3))}"></div><div class="c" style="align-items:center;text-align:center">${g.stamp ? `<div class="stamp stampA" style="font-size:330px;border-width:16px;padding:10px 70px 0;${d(t0)}">${esc(g.text)}</div>` : `<div class="bebas trk" style="font-size:${fs}px;text-shadow:0 8px 60px rgba(0,0,0,.8);${d(t0)}">${esc(g.text)}</div>`}
    ${g.sub ? `<div class="bar gl" style="width:220px;margin:${g.stamp ? 70 : 20}px 0 24px;${d(t0 + .7)}"></div><div class="sub fu" style="color:#fff;font-size:46px;text-shadow:0 2px 14px #000;${d(t0 + .8)}">${esc(g.sub)}</div>` : ''}</div>`; },
  lower: (g, D) => { const t0 = Math.max(.5, (g.late || 0) * D); return `<div style="position:absolute;left:110px;bottom:150px"><div class="wr" style="display:inline-flex;${d(t0)}"><div style="width:18px;background:var(--amber)"></div><div class="bebas" style="background:#0a0a0a;font-size:104px;padding:14px 40px 4px;letter-spacing:3px">${esc(g.name)}</div></div><br>
    <div class="wr" style="display:inline-block;background:#fff;color:#0a0a0a;font:700 36px Inter;padding:14px 30px;${d(t0 + .35)}">${esc(g.role)}</div></div>`; },
  chips: (g, D) => { const n = g.items.length, t0 = (g.t0 || .12) * D, st = (D * .86 - t0) / n;
    return `<div class="abs" style="background:linear-gradient(90deg,rgba(0,0,0,.82),rgba(0,0,0,.25) 62%,transparent)"></div><div style="position:absolute;left:150px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;align-items:flex-start">
    <div class="bebas wr" style="font-size:${fit(g.title, 200, 1200)}px;${d(.4)}">${esc(g.title)}</div><div class="bar gl" style="width:240px;margin:8px 0 34px;${d(.7)}"></div>
    ${g.items.map((it, i) => `<div class="fu" style="background:rgba(12,12,12,.9);border-left:10px solid var(--amber);font:700 62px Osw;letter-spacing:2px;padding:16px 40px 18px;margin:11px 0;${d(t0 + i * st)}">${esc(it)}</div>`).join('')}</div>`; },
};
const OVERLAY = new Set(['none', 'stat', 'word', 'lower', 'chips']);
const FULL = new Set(['quote', 'sting', 'bumper', 'end', 'map', 'article']);
const isAlpha = s => !FULL.has(s.gfx.type);

function html(s) {
  const g = s.gfx, D = s.dur, alpha = isAlpha(s);
  studio = alpha ? SCRIM(g.type === 'doc' || g.type === 'terminal' ? .62 : .72) : STUDIO;
  const bare = ['quote', 'sting', 'pitch'].includes(g.type) || g.bare;
  return `<!doctype html><html><head><meta charset="utf-8"><style>${CSS}body{--D:${D};background:${alpha ? 'transparent' : '#000000'}}.c{zoom:${({list:1.08,names:1.25,terminal:1.2,flow:1.2,flow3:1.2,org:1.25,bars:1.15,define:1.1})[g.type]||1}}</style></head><body>
${OVERLAY.has(g.type) ? '<div class="abs ovig"></div>' : ''}${T[g.type](g, D)}${g.type === 'pitch' || alpha || !bare ? hud(s) : ''}${g.type === 'sting' ? '' : '<div class="abs flash"></div>'}
<script>window.__init=()=>{window.__A=document.getAnimations();__A.forEach(a=>a.pause())};
window.__seek=t=>{__A.forEach(a=>a.currentTime=t*1000);
document.querySelectorAll('[data-count]').forEach(e=>{const a=+e.dataset.t0,b=+e.dataset.t1;let p=Math.min(1,Math.max(0,(t-a)/(b-a)));p=1-Math.pow(1-p,3);e.textContent=Math.round(+e.dataset.count*p).toLocaleString('en-US')});
document.querySelectorAll('[data-type]').forEach(e=>{const n=Math.max(0,Math.floor((t-+e.dataset.t0)*+e.dataset.cps)),x=e.dataset.type;e.textContent=x.slice(0,n)+(n>0&&n<x.length?'█':'')||'\\u00a0'})}</script></body></html>`;
}

(async () => {
  const args = process.argv.slice(2), still = args.includes('--still');
  const ids = args.filter(a => !a.startsWith('--'));
  const scenes = TL.scenes.filter(s => !ids.length || ids.includes(s.id));
  fs.mkdirSync(B + '/html', { recursive: true });
  if (!fs.existsSync(B + '/world.js')) fs.writeFileSync(B + '/world.js', 'window.WORLD=' + fs.readFileSync(NM + '/world-atlas/countries-50m.json'));
  const browser = await chromium.launch({ args: ['--allow-file-access-from-files', '--force-color-profile=srgb'] });
  const queue = scenes.slice(); let done = 0; const t0 = Date.now();
  const worker = async () => {
    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
    for (let s; (s = queue.shift());) {
      const alpha = isAlpha(s), f = `${B}/html/${s.id}.html`, out = `${B}/frames/${s.id}`;
      fs.writeFileSync(f, html(s));
      await page.goto('file://' + f); await page.evaluate(() => document.fonts.ready); await page.evaluate(() => __init());
      if (still) {
        await page.evaluate(t => __seek(t), s.dur * 0.92);
        await page.screenshot({ path: `${B}/stills/${s.id}.png`, omitBackground: alpha });
      } else {
        fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true });
        for (let i = 0; i < s.nf; i++) {
          await page.evaluate(t => __seek(t), i / FPS);
          const p = `${out}/${String(i).padStart(5, '0')}.${alpha ? 'png' : 'jpg'}`;
          await page.screenshot(alpha ? { path: p, omitBackground: true } : { path: p, type: 'jpeg', quality: 93 });
        }
      }
      console.log(`[${++done}/${scenes.length}] ${s.id} ${s.gfx.type} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    await page.close();
  };
  if (still) fs.mkdirSync(B + '/stills', { recursive: true });
  await Promise.all(Array.from({ length: 4 }, worker));
  await browser.close();
})();
