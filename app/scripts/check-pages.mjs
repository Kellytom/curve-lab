// Every page of the app, checked in a real browser: one header, one main
// landmark, the draft mark, and no link to the page you are already on.
//
//   node app/scripts/check-pages.mjs
//
// The Astro server must be up on :4321. A page that answers 500, loses its
// <main> (the 2026-11-19 /lab margin fault) or links to itself is a failure.

import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright-core";
import { gotoStable } from "./lib/navigate.mjs";

const BASE = process.env.CURVE_LAB_URL || "http://127.0.0.1:4321";
const EXE = process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const ALL_ROUTES = [
  "/", "/about/", "/everything/", "/lab/", "/finder/", "/finder-candidates/",
  "/illuminations/", "/figures/", "/names/", "/ph-nth-sandbox/", "/users/", "/blog/", "/sandbox/", "/roots/", "/bezier/", "/prime-mover/", "/reduce/", "/candidates/", "/problems/", "/hybrids/", "/hybrids-wonk/", "/plates/", "/extra-curves/", "/said/", "/deep2-said/", "/glue/", "/jobs/", "/class-v/", "/hearts/",
];

// Only the pages you name, or a short list for the loop; with no argument, every page.
//   node app/scripts/check-pages.mjs /plates /hybrids     the two you touched
//   node app/scripts/check-pages.mjs --quick             the four desks
//   node app/scripts/check-pages.mjs                     every page (end of session)
const QUICK = ["/", "/plates", "/hybrids/", "/hybrids-wonk/"];
const asked = process.argv.slice(2);

// The routes whose source changed since HEAD, intersected with the list above.
// A shared layout, style, script or server library means every route.
function changedRoutes() {
  const repo = fileURLToPath(new URL("../../", import.meta.url));
  const changed = [
    execSync("git diff --name-only HEAD", { cwd: repo, encoding: "utf8" }),
    execSync("git ls-files --others --exclude-standard", { cwd: repo, encoding: "utf8" }),
  ].join("\n").split("\n").filter(Boolean);
  const known = new Map(ALL_ROUTES.map((route) => [route.replace(/\/$/, "") || "/", route]));
  const routes = new Set();
  let shared = false;
  for (const file of changed) {
    const page = file.match(/^app\/src\/pages\/(.+)\.astro$/);
    if (page) {
      const name = page[1].replace(/\/index$/, "");
      const route = known.get(`/${name}`.replace(/\/$/, "")) || (name === "index" ? "/" : undefined);
      if (route) routes.add(route);
      continue;
    }
    if (/^app\/(src\/(layouts|components|styles|theme|scripts|lib)\/|public\/vendor\/)/.test(file)) {
      shared = true;
    }
  }
  if (shared) return ALL_ROUTES;
  return [...routes];
}

const changed = asked.includes("--changed");
const ROUTES = changed
  ? changedRoutes()
  : asked.includes("--quick")
    ? QUICK
    : asked.filter((arg) => arg.startsWith("/")).length
      ? asked.filter((arg) => arg.startsWith("/"))
      : ALL_ROUTES;

if (changed) {
  console.log(ROUTES.length
    ? `changed: ${ROUTES.join(" ")}`
    : "no page source in the diff");
  if (!ROUTES.length) process.exit(0);
}

const browser = await chromium.launch({ executablePath: EXE });
const failures = [];

for (const route of ROUTES) {
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  const errors = [];
  page.on("pageerror", (error) => errors.push(`pageerror: ${error}`));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(`console: ${message.text()}`);
  });
  page.on("response", (response) => {
    const status = response.status();
    if (status >= 400 && !response.url().includes("favicon")) {
      errors.push(`resource ${status}: ${response.url()}`);
    }
  });
  try {
    const response = await gotoStable(page, BASE + route, { waitUntil: "domcontentloaded", timeout: 90000 });
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
    if (errors.length) failures.push(`${route}: ${errors.slice(0, 3).join(" | ")}`);
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
