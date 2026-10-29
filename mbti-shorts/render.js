const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
// usage: node render.js outDir fps startFrame endFrame  |  node render.js outDir test t1,t2,...
(async () => {
  const [outDir, a, b, c] = process.argv.slice(2);
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('PAGEERR', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
  await page.goto('file://' + path.resolve(__dirname, 'index.html'));
  await page.evaluate(() => window.fontsReady);
  if (a === 'test') {
    for (const t of b.split(',')) {
      await page.evaluate(t => window.render(t), parseFloat(t));
      await page.screenshot({ path: `${outDir}/t_${t}.png` });
    }
  } else {
    const fps = parseInt(a), s = parseInt(b), e = parseInt(c);
    for (let f = s; f < e; f++) {
      await page.evaluate(t => window.render(t), f / fps);
      await page.screenshot({ path: `${outDir}/${String(f).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 93 });
    }
  }
  await browser.close();
})();
