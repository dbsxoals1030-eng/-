const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
// usage: node render_bumper.js outDir v|h [test t1,t2,..]
(async () => {
  const [outDir, o, mode, ts] = process.argv.slice(2); fs.mkdirSync(outDir, { recursive: true });
  const H = o === 'h'; const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: H ? 1920 : 1080, height: H ? 1080 : 1920 }, deviceScaleFactor: 1 });
  p.on('pageerror', e => console.error('PAGEERR', e.message));
  await p.goto('file://' + path.resolve(__dirname, 'bumper.html') + (H ? '?o=h' : ''));
  await p.evaluate(() => window.fontsReady);
  if (mode === 'test') { for (const t of ts.split(',')) { await p.evaluate(t => window.render(t), parseFloat(t)); await p.screenshot({ path: `${outDir}/t_${t}.png` }); } }
  else { for (let f = 0; f < 150; f++) { await p.evaluate(t => window.render(t), f / 30); await p.screenshot({ path: `${outDir}/${String(f).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 93 }); } }
  await b.close();
})();
