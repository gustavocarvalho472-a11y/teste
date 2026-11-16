// Renders the "video wall" frame used behind/around real footage takes (lime + black brand).
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const X = 160, Y = 84, W = 1600, H = 900;
  await p.setContent(`<body style="margin:0;width:1920px;height:1080px;background:#050505;overflow:hidden">
    <div style="position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.10) 1.3px,transparent 1.6px);background-size:14px 14px"></div>
    <div style="position:absolute;inset:0;background:repeating-linear-gradient(135deg,transparent 0 46px,rgba(198,255,0,.035) 46px 48px)"></div>
    <div style="position:absolute;left:-200px;top:-260px;width:900px;height:700px;background:#0c0c0c;transform:rotate(-12deg)"></div>
    <div style="position:absolute;right:-240px;bottom:-300px;width:1000px;height:760px;background:#0d0d0d;transform:rotate(-9deg)"></div>
    <div style="position:absolute;inset:0;background:radial-gradient(ellipse at 50% 50%,transparent 45%,rgba(0,0,0,.75))"></div></body>`);
  await p.screenshot({ path: __dirname + '/build/frame_bg.png' });
  const c = (x, y, r) => `<div style="position:absolute;left:${x}px;top:${y}px;width:54px;height:54px;border-top:8px solid #C6FF00;border-left:8px solid #C6FF00;transform:rotate(${r}deg)"></div>`;
  await p.setContent(`<body style="margin:0;width:1920px;height:1080px;background:transparent;overflow:hidden">
    <div style="position:absolute;left:${X - 3}px;top:${Y - 3}px;width:${W}px;height:${H}px;border:3px solid rgba(255,255,255,.85);box-shadow:0 0 0 1px #000,0 30px 80px rgba(0,0,0,.8)"></div>
    ${c(X - 16, Y - 16, 0)}${c(X + W - 38, Y - 16, 90)}${c(X + W - 38, Y + H - 38, 180)}${c(X - 16, Y + H - 38, 270)}
    <div style="position:absolute;left:${X + W + 22}px;top:${Y + 120}px;width:10px;height:220px;background:#C6FF00"></div>
    <div style="position:absolute;left:${X - 34}px;top:${Y + H - 330}px;width:10px;height:160px;background:rgba(255,255,255,.5)"></div></body>`);
  await p.screenshot({ path: __dirname + '/build/frame_fg.png', omitBackground: true });
  await b.close();
})();
