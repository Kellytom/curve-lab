// The trim desk: rational fractions of t reach the cut, and the preview follows the form.
//
//   node scripts/check-trim.mjs
//
// The maths is app/src/lib/trim-curve.js (node-tested); this proves the page's form posts the
// fractions it shows and the cut piece is drawn for the range asked for.

import { chromium } from "playwright-core";
import { fileURLToPath } from "node:url";
import { isKept } from "../app/src/lib/provenance.js";
import { orderPlates } from "../app/src/lib/plate-order.js";

// The pages read the registry through the database (loadRegistry), so the check does too.
const ROOT = fileURLToPath(new URL("..", import.meta.url));
process.env.DATABASE_URL ||= `file:${fileURLToPath(new URL("../app/prisma/dev.db", import.meta.url))}`;
const { loadRegistry } = await import("../app/src/lib/registry.ts");

// The operator, 2026-11-24: "those curves are ok; leave them at the bottom. put the curves from
// /plates". The list must lead with the plates' kept set, in the plates' star order, and the
// counts it prints must be the ones the registry makes.
const registry = await loadRegistry(ROOT);
const byUid = new Map(registry.curves.map((curve: any) => [curve.uid, curve]));
const cuttable = (curve: any) => (Array.isArray(curve.path) && curve.path.length > 2)
  || (Array.isArray(curve.speedX) && Array.isArray(curve.speedY)
    && curve.speedX.length > 0 && curve.speedY.length > 0);
const plates = orderPlates(registry.curves.filter(cuttable).filter((curve: any) => isKept(curve, byUid)), "stars");
const rest = registry.curves.filter(cuttable).filter((curve: any) => !plates.some((row: any) => row.uid === curve.uid));

const BASE = process.env.CURVE_LAB_URL || "http://127.0.0.1:4321";
const EXE = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const browser = await chromium.launch({ executablePath: EXE, headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
const errors: string[] = [];
page.on("pageerror", (error: Error) => errors.push(error.message));

await page.goto(`${BASE}/trim/`, { waitUntil: "networkidle" });
const lead = await page.locator("main .lead").innerText();
if (!lead.includes(`${plates.length} curves on`)) throw new Error(`the plates count is missing: ${lead}`);
if (!lead.includes(`${rest.length} others follow`)) throw new Error(`the rest count is missing: ${lead}`);
const firstUid = await page.locator(".trim-card code").first().innerText();
if (firstUid !== plates[0].uid) throw new Error(`the list leads with ${firstUid}, not ${plates[0].uid}`);

await page.goto(`${BASE}/trim/c-0274`, { waitUntil: "networkidle" });
const caption = page.locator(".trim-half figcaption");
const first = await caption.innerText();
if (!first.includes("t 1/4 → 3/4")) throw new Error(`default cut: ${first}`);

await page.fill('input[name="from"]', "1/3");
await page.fill('input[name="to"]', "2/3");
await Promise.all([
  page.waitForLoadState("networkidle"),
  page.locator('.trim-form button[type="submit"]').first().click(),
]);
const url = new URL(page.url());
if (url.searchParams.get("from") !== "1/3" || url.searchParams.get("to") !== "2/3") {
  throw new Error(`the preview did not carry the fractions: ${page.url()}`);
}
const second = await caption.innerText();
if (!second.includes("t 1/3 → 2/3")) throw new Error(`after the preview: ${second}`);

// a bad fraction is refused with a message, not a broken picture
await page.fill('input[name="from"]', "0.3");
await Promise.all([
  page.waitForLoadState("networkidle"),
  page.locator('.trim-form button[type="submit"]').first().click(),
]);
const bad = await page.locator(".trim-bad").innerText().catch(() => "");
if (!/whole-number fraction/.test(bad)) throw new Error(`a decimal was not refused: ${bad}`);

// The operator's mirror rule: typing a start fraction sets the end to (q - p)/q, ordered.
await page.goto(`${BASE}/trim/c-0274`, { waitUntil: "networkidle" });
await page.fill('input[name="from"]', "200/10001");
await page.locator('input[name="to"]').click();
if (await page.locator('input[name="to"]').inputValue() !== "9801/10001") {
  throw new Error("the end did not follow (q - p)/q");
}
await page.fill('input[name="from"]', "3/5");
await page.locator('input[name="to"]').click();
if (await page.locator('input[name="from"]').inputValue() !== "2/5"
  || await page.locator('input[name="to"]').inputValue() !== "3/5") {
  throw new Error("a pair past the middle was not ordered");
}

// The tune page's door: the link must carry the values on screen, so the cut is made with the
// band being looked at (operator, 2026-11-24: "connect /tune/ to the trim function").
await page.goto(`${BASE}/tune/c-0022`, { waitUntil: "networkidle" });
const door = page.locator("#tune-trim");
const before = await door.getAttribute("href");
if (!before || !before.startsWith("/trim/c-0022?")) throw new Error(`the trim door: ${before}`);
await page.locator('input[name="widthPct"]').first().fill("6.5");
const after = await door.getAttribute("href");
if (!after.includes("widthPct=6.5")) throw new Error(`the door did not follow the slider: ${after}`);
await page.goto(`${BASE}${after}`, { waitUntil: "networkidle" });
const width = await page.locator('input[name="widthPct"]').inputValue();
if (width !== "6.5") throw new Error(`the trim page lost the width: ${width}`);

if (errors.length) throw new Error(`page errors: ${errors.join(" · ")}`);
console.log(`trim: ok — 1/4 → 3/4, then 1/3 → 2/3 drawn; a decimal is refused`);
await browser.close();
