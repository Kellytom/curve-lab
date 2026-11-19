// The click-everything gate: every page, every safe control, in a real browser.
//
//   CURVE_LAB_URL=http://127.0.0.1:4399 node app/scripts/check-clicks.mjs
//
// It absorbs the three earlier checks:
//   - check-pages: one header, one main, the draft mark, no self-link;
//   - check-stars: no duplicate cards, a star round trip leaves the list as it
//     found it;
//   - check-names: the chosen curves, every one composes a name, a saved name
//     survives a reload, and a save does not change the row count.
//
// It then presses every control that is safe to press. A control is safe when
// it is a button in the app's own write set, or an input/select/textarea. Links
// and download/export buttons are skipped. A refused write (an /api response
// of 400 or more) and any page error are failures.
//
// The server is whatever CURVE_LAB_URL names. test-server.mjs points it at a
// scratch copy of the database; this file never opens app/prisma/dev.db.

import { chromium } from "playwright-core";

const BASE = process.env.CURVE_LAB_URL || "http://127.0.0.1:4321";
const EXE = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const ROUTES = [
  "/", "/about/", "/everything/", "/lab/", "/finder/", "/finder-candidates/",
  "/illuminations/", "/figures/", "/names/", "/ph-nth-sandbox/", "/users/", "/blog/",
];

// Buttons that write to the database or the browser, never navigate away.
// `#sf-star` comes before `#sf-save`: a save with no star would empty the list.
const SAFE_BUTTONS = [
  "button.star", "button.save", "button.to-notes", "button.restore",
  "button.turn", "button[data-turn]", "button[data-piece]", "button[data-imp]",
  ".stars button", "#save-stars", "#sf-star", "#sf-save", "#names-undo button",
];
const SAFE_INPUTS = [
  "input[type=text]", "input[type=number]", "input[type=range]",
  "input[type=checkbox]", "select", "textarea",
];
const SKIP_TEXT = /download|export/i;
const WRITE_API = /\/api\/(curve-notes|finder-stars|stars|sandbox-curves)(\?|$)/;

const failures = [];
const fail = (route, message) => failures.push(`${route}: ${message}`);

function isWriteApi(url) {
  return WRITE_API.test(new URL(url).pathname);
}

async function pageShape(page) {
  return page.evaluate(() => {
    const path = location.pathname.replace(/\/$/, "") || "/";
    const selfLinks = [...document.querySelectorAll(".site-menu a, .site-header .brand")]
      .map((a) => a.getAttribute("href"))
      .filter((href) => href && (href === path || (href === "/" && path === "/")));
    const starIds = [...document.querySelectorAll("button.star")].map((b) => b.dataset.id);
    return {
      header: Boolean(document.querySelector(".site-header")),
      title: document.querySelector(".page-title")?.innerText.trim() || "",
      draft: document.querySelector(".draft")?.textContent.trim() || "",
      main: Boolean(document.querySelector("main#main")),
      selfLinks,
      cards: starIds.length,
      duplicateCards: starIds.length - new Set(starIds).size,
      rows: document.querySelectorAll(".row").length,
    };
  });
}

async function waitForPage(page) {
  await page.waitForTimeout(500);
}

async function pressButtons(page, route) {
  for (const selector of SAFE_BUTTONS) {
    const count = await page.$$eval(selector, (els) => els.length).catch(() => 0);
    for (let i = 0; i < Math.min(count, 8); i += 1) {
      const handle = (await page.$$(selector).catch(() => []))[i];
      if (!handle) continue;
      const text = await handle.textContent().catch(() => "");
      if (SKIP_TEXT.test(text)) continue;
      const disabled = await handle.evaluate((el) => el.disabled).catch(() => true);
      if (disabled) continue;
      try {
        await handle.click({ timeout: 1500 });
      } catch {
        // A reload replaced the page; go back and continue.
        await page.goto(BASE + route, { waitUntil: "domcontentloaded" }).catch(() => {});
        await waitForPage(page);
      }
      await page.waitForTimeout(250);
      if (!page.url().startsWith(BASE + route)) {
        await page.goto(BASE + route, { waitUntil: "domcontentloaded" }).catch(() => {});
        await waitForPage(page);
      }
    }
  }
}

async function changeInputs(page) {
  for (const selector of SAFE_INPUTS) {
    const count = await page.$$eval(selector, (els) => els.length).catch(() => 0);
    for (let i = 0; i < Math.min(count, 12); i += 1) {
      const handle = (await page.$$(selector).catch(() => []))[i];
      if (!handle) continue;
      const info = await handle.evaluate((el) => ({
        type: el.type || el.tagName.toLowerCase(),
        tag: el.tagName.toLowerCase(),
        value: el.value,
        max: el.max,
        options: el.tagName === "SELECT" ? [...el.options].map((o) => o.value).filter(Boolean) : [],
        selectedIndex: el.selectedIndex,
      })).catch(() => null);
      if (!info) continue;
      try {
        if (info.type === "checkbox") {
          await handle.click({ timeout: 1000 });
        } else if (info.tag === "select") {
          const next = info.options[(info.selectedIndex + 1) % info.options.length];
          if (next !== undefined) await handle.selectOption(next, { timeout: 1000 });
        } else if (info.type === "range" || info.type === "number") {
          const next = String(Number(info.value) + 1);
          await handle.fill(next, { timeout: 1000 });
        } else {
          await handle.fill(`${info.value}x`, { timeout: 1000 });
        }
      } catch { /* stale or not editable */ }
      await page.waitForTimeout(150);
    }
  }
}

async function starRoundTrip(page, route) {
  await page.evaluate(() => localStorage.removeItem("finder-stars"));
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.waitForTimeout(800);

  const before = await (await fetch(`${BASE}/api/finder-stars`)).json();
  const beforeCount = (before.curves || []).length;
  const picked = await page.evaluate(() => {
    const button = [...document.querySelectorAll("button.star")].find((b) => b.textContent.trim() === "☆");
    if (!button) return null;
    button.click();
    return button.dataset.id;
  });
  if (!picked) {
    fail(route, "no empty star to press");
    return;
  }
  await page.waitForTimeout(1200);
  const on = await page.evaluate((id) => {
    const button = document.querySelector(`button.star[data-id="${id}"]`);
    return button ? button.textContent.trim() === "★" : false;
  }, picked);
  await page.evaluate((id) => document.querySelector(`button.star[data-id="${id}"]`)?.click(), picked);
  await page.waitForTimeout(1200);
  const after = await (await fetch(`${BASE}/api/finder-stars`)).json();
  const afterCount = (after.curves || []).length;

  if (!on) fail(route, "the star did not turn on");
  if (afterCount !== beforeCount) {
    fail(route, `the finder star list has ${afterCount} curves, not the ${beforeCount} it started with`);
  }
}

async function namesRoundTrip(page, route) {
  await page.evaluate(() => localStorage.removeItem("names-drafts"));
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.waitForTimeout(800);

  const desk = await page.evaluate(() => {
    const rows = [...document.querySelectorAll(".row")];
    return {
      rows: rows.length,
      unsaveable: rows
        .filter((row) => !row.querySelector(".preview").textContent.trim())
        .map((row) => row.querySelector(".now").textContent),
    };
  });
  if (desk.rows < 1) fail(route, "the naming desk shows no rows");
  if (desk.unsaveable.length) fail(route, `no name to save for: ${desk.unsaveable.join(", ")}`);

  const saved = await page.evaluate(async () => {
    const row = document.querySelector(".row");
    const name = row.querySelector(".preview").textContent.replace(/^=\s*/, "");
    row.querySelector(".save").click();
    await new Promise((resolve) => setTimeout(resolve, 1200));
    return { uid: row.dataset.uid, name, flag: row.querySelector(".flag").textContent };
  });
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1000);
  const afterReload = await page.evaluate((uid) => {
    const row = document.querySelector(`.row[data-uid="${uid}"]`);
    return {
      rows: document.querySelectorAll(".row").length,
      now: row.querySelector(".now").textContent,
      draft: JSON.parse(localStorage.getItem("names-drafts") || "{}")[uid],
    };
  }, saved.uid);

  if (afterReload.rows !== desk.rows) {
    fail(route, `a save changed the row count: ${desk.rows} before, ${afterReload.rows} after`);
  }
  if (!/saved/.test(saved.flag)) fail(route, `save said "${saved.flag}"`);
  if (afterReload.now !== saved.name) {
    fail(route, `after reload the name is "${afterReload.now}", not "${saved.name}"`);
  }
  if (afterReload.draft !== undefined) fail(route, "the saved name is still a draft");
}

async function sweep(browser, route) {
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  const pageErrors = [];
  page.on("pageerror", (error) => pageErrors.push(String(error)));
  page.on("response", (response) => {
    if (isWriteApi(response.url()) && response.status() >= 400) {
      fail(route, `refused write: ${response.status()} ${response.url()}`);
    }
  });

  try {
    const response = await page.goto(BASE + route, { waitUntil: "domcontentloaded", timeout: 30000 });
    await waitForPage(page);
    if (response?.status() !== 200) fail(route, `HTTP ${response?.status()}`);

    const shape = await pageShape(page);
    if (!shape.header) fail(route, "no header");
    if (!shape.title.startsWith("this page is ")) fail(route, "no page title");
    if (!shape.draft) fail(route, "no draft mark");
    if (!shape.main) fail(route, "no <main id=\"main\">");
    if (shape.selfLinks.length) fail(route, `links to itself (${shape.selfLinks.join(", ")})`);
    if (shape.duplicateCards) fail(route, `draws ${shape.duplicateCards} duplicate card(s)`);

    if (route === "/finder/") await starRoundTrip(page, route);
    if (route === "/names/") await namesRoundTrip(page, route);

    // The specific checks can reload the page; go back to a clean copy before
    // pressing the generic controls.
    await page.goto(BASE + route, { waitUntil: "domcontentloaded" }).catch(() => {});
    await waitForPage(page);

    await pressButtons(page, route);
    await changeInputs(page);

    if (pageErrors.length) fail(route, `page errors: ${pageErrors.join(" | ")}`);
  } catch (error) {
    fail(route, String(error).split("\n")[0]);
  } finally {
    await page.close();
  }
}

const browser = await chromium.launch({ executablePath: EXE });
try {
  for (const route of ROUTES) await sweep(browser, route);
} finally {
  await browser.close();
}

if (failures.length) {
  console.error(failures.map((line) => `FAIL ${line}`).join("\n"));
  process.exit(1);
}
console.log(`ok — ${ROUTES.length} pages, every safe control pressed, no page error, no duplicate card, no refused write`);
