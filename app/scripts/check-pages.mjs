// Every page of the app, checked in a real browser: one header, one main
// landmark, the draft mark, and no link to the page you are already on.
//
//   node app/scripts/check-pages.mjs
//
// The Astro server must be up on :4321. A page that answers 500, loses its
// <main> (the 2026-11-19 /lab margin fault) or links to itself is a failure.

import { chromium } from "playwright-core";

const BASE = process.env.CURVE_LAB_URL || "http://127.0.0.1:4321";
const EXE = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const ROUTES = [
  "/", "/about/", "/everything/", "/lab/", "/finder/", "/finder-candidates/",
  "/illuminations/", "/figures/", "/names/", "/ph-nth-sandbox/", "/users/", "/blog/", "/sandbox/", "/roots/",
];

const browser = await chromium.launch({ executablePath: EXE });
const failures = [];

for (const route of ROUTES) {
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  const errors = [];
  page.on("pageerror", (error) => errors.push(String(error)));
  try {
    const response = await page.goto(BASE + route, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForTimeout(400);
    const found = await page.evaluate(() => {
      const path = location.pathname.replace(/\/$/, "") || "/";
      const selfLinks = [...document.querySelectorAll(".site-menu a, .site-header .brand")]
        .map((a) => a.getAttribute("href"))
        .filter((href) => href && (href === path || (href === "/" && path === "/")));
      return {
        header: Boolean(document.querySelector(".site-header")),
        title: document.querySelector(".page-title")?.innerText.trim() || "",
        menu: document.querySelectorAll(".site-menu a").length,
        draft: document.querySelector(".draft")?.textContent.trim() || "",
        main: Boolean(document.querySelector("main#main")),
        selfLinks,
      };
    });
    if (response?.status() !== 200) failures.push(`${route}: HTTP ${response?.status()}`);
    if (!found.header) failures.push(`${route}: no header`);
    if (!found.title.startsWith("this page is ")) failures.push(`${route}: no page title`);
    if (!found.draft) failures.push(`${route}: no draft mark`);
    if (!found.main) failures.push(`${route}: no <main id="main">`);
    if (found.selfLinks.length) failures.push(`${route}: links to itself (${found.selfLinks.join(", ")})`);
    if (errors.length) failures.push(`${route}: page errors: ${errors.join(" | ")}`);
  } catch (error) {
    failures.push(`${route}: ${String(error).split("\n")[0]}`);
  }
  await page.close();
}

await browser.close();

if (failures.length) {
  console.error(failures.map((line) => `FAIL ${line}`).join("\n"));
  process.exit(1);
}
console.log(`ok — ${ROUTES.length} pages: one header, one main, the draft mark, no self-link`);
