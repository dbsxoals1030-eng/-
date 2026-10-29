const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2560, height: 1440 } });
  await p.goto('file://' + path.resolve(__dirname, 'channel.html'));
  await p.evaluate(() => Promise.all(['600','700','800','900'].map(w => document.fonts.load(`${w} 40px P`, '잇팁인데요'))).then(() => document.fonts.ready));
  await p.locator('#profile').screenshot({ path: 'profile_800.png' });
  await p.locator('#banner').screenshot({ path: 'banner_2560x1440.png' });
  await b.close();
})();
