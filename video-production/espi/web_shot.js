// Real website screenshot with lime highlights applied in the page itself. Usage: node web_shot.js <url> <outdir>
const { chromium } = require('playwright');
const OUT = process.argv[3];
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 2, userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36' });
  await p.goto(process.argv[2], { waitUntil: 'domcontentloaded', timeout: 60000 });
  await p.waitForTimeout(6000);
  const r = await p.evaluate(() => {
    document.querySelectorAll('[id*=onetrust],[class*=cookie],[id*=cookie],[class*=consent],[id*=consent]').forEach(e => e.remove());
    const css = document.createElement('style');
    css.textContent = `mark.hl{background:linear-gradient(180deg,transparent 52%,rgba(198,255,0,.95) 52%,rgba(198,255,0,.95) 92%,transparent 92%);color:inherit;padding:0 2px}
      .dt{outline:3px solid #C6FF00;outline-offset:6px;border-radius:999px}`;
    document.head.appendChild(css);
    const wrap = (needle) => { for (const el of document.querySelectorAll('p,h1')) { const i = el.innerHTML.indexOf(needle); if (i >= 0) { el.innerHTML = el.innerHTML.replace(needle, `<mark class="hl">${needle}</mark>`); return true; } } return false; };
    const ok = [wrap('Real Madrid swoop in on Hull City transfer target'), wrap('the Tigers had all but landed the 21-year-old forward'), wrap('Real Madrid registered their interest in Espi')];
    for (const el of document.querySelectorAll('span,div,time')) if (el.childElementCount === 0 && el.textContent.trim() === '30, Jul') { el.classList.add('dt'); ok.push('date'); break; }
    const h1 = document.querySelector('h1').getBoundingClientRect();
    const box = t => { for (const el of document.querySelectorAll('p')) if (el.innerText.startsWith(t)) { const q = el.getBoundingClientRect(); return [q.top + scrollY, q.bottom + scrollY]; } };
    return { ok, h1: [h1.left, h1.top + scrollY, h1.right], p1: box('Hull were linked'), p2: box('Before they could'), p0: box('The Tigers are') };
  });
  console.log(JSON.stringify(r));
  const x = r.h1[0] - 60, w = 790;
  await p.screenshot({ path: OUT + '/dazn_top.png', clip: { x, y: r.h1[1] - 90, width: w, height: 840 }, fullPage: true });
  await p.evaluate(y => window.scrollTo(0, y), r.p1[0] - 200); await p.waitForTimeout(800);
  const sy = await p.evaluate(() => scrollY);
  await p.screenshot({ path: OUT + '/dazn_body.png', clip: { x, y: r.p1[0] - 40 - sy, width: w, height: r.p2[1] - r.p1[0] + 70 } });
  await b.close();
})();
