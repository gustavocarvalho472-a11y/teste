const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 2 });
  await p.goto('file://' + path.resolve(__dirname, process.argv[2] || 'thumb.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  await p.screenshot({ path: path.resolve(__dirname, process.argv[3] || 'thumb_2x.png') }); await b.close(); })();
