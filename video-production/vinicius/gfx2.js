// Renders every overlay (PNG, transparent, 1x) and plate (JPG, 2x) listed in build/v2/gfx.json. Cached by content hash.
// Usage: node gfx2.js [build/v2]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const kit = require('./kitlib');
const DIR = path.resolve(process.argv[2] || path.join(__dirname, 'build/v2')), OUT = path.join(DIR, 'gfx');
fs.mkdirSync(OUT, { recursive: true });
const list = JSON.parse(fs.readFileSync(path.join(DIR, 'gfx.json')));
const cache = fs.existsSync(path.join(OUT, 'cache.json')) ? JSON.parse(fs.readFileSync(path.join(OUT, 'cache.json'))) : {};
(async () => {
  const b = await chromium.launch();
  const pages = { ov: await b.newPage({ viewport: { width: 1920, height: 1080 } }), plate: await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 }) };
  let n = 0;
  for (const g of list) {
    const kind = g.kind, fn = (kind === 'ov' ? kit.OV : kit.PL)[g.comp];
    if (!fn) throw new Error('unknown component ' + g.comp);
    const html = kit.page(fn(g.p || {}), kind);
    const deps = [...new Set(html.match(/file:\/\/[^)"' ]+\.(?:jpg|png)/g) || [])].map(u => { try { return fs.statSync(u.slice(7)).mtimeMs; } catch (e) { return 0; } }).join(',');
    const h = crypto.createHash('md5').update(html + deps).digest('hex');
    const out = path.join(OUT, g.id + (kind === 'ov' ? '.png' : '.jpg'));
    if (cache[g.id] === h && fs.existsSync(out)) continue;
    const f = path.join(OUT, g.id + '.html'); fs.writeFileSync(f, html);
    const p = pages[kind]; await p.goto('file://' + f); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(60);
    await p.screenshot(kind === 'ov' ? { path: out, omitBackground: true } : { path: out, type: 'jpeg', quality: 92 });
    cache[g.id] = h; n++;
  }
  fs.writeFileSync(path.join(OUT, 'cache.json'), JSON.stringify(cache));
  await b.close(); console.log(`gfx: ${n} rendered, ${list.length} total`);
})();
