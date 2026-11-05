// Layout gate for the three ornament proofs.
// Uses playwright-core with the installed Chrome: no browser download.
//
//   node scripts/check-proofs.mjs
//
// Fails (exit 1) on a missing page or horizontal overflow at any viewport.

import { chromium } from "playwright-core";

const BASE = "http://127.0.0.1:8003/workbench/";
const PAGES = ["fleur-proof.html", "volute-proof.html", "cruciform-proof.html", "ending-fit.html"];
const VIEWPORTS = [[1000, 1200], [390, 844], [320, 844]];

const browser = await chromium.launch({ channel: "chrome", headless: true });
const context = await browser.newContext();
let failed = false;
const results = [];

for (const page of PAGES) {
    for (const [width, height] of VIEWPORTS) {
        const tab = await context.newPage();
        await tab.setViewportSize({ width, height });
        try {
            const response = await tab.goto(BASE + page, { waitUntil: "load", timeout: 15000 });
            const status = response ? response.status() : null;
            const overflow = await tab.evaluate(() =>
                document.documentElement.scrollWidth - window.innerWidth);
            const svgs = await tab.evaluate(() => document.querySelectorAll("svg").length);
            const ok = status === 200 && overflow <= 1 && svgs > 0;
            if (!ok) failed = true;
            results.push({ page, width, status, overflow, svgs, ok });
        } catch (error) {
            failed = true;
            results.push({ page, width, error: error.message.split("\n")[0], ok: false });
        } finally {
            await tab.close();
        }
    }
}

await browser.close();
console.log(JSON.stringify(results, null, 2));
process.exit(failed ? 1 : 0);
