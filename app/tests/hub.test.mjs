// The hub must show every page, not a hand list. This compares the hub's page
// list with the manifest and with the files in workbench/.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync } from "node:fs";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { buildHub } from "../src/lib/pages.js";
import { lanUrls, latestTunnelUrl } from "../src/lib/tunnel.js";

const APP = fileURLToPath(new URL("..", import.meta.url));
const ROOT = path.resolve(APP, "..");
const manifest = JSON.parse(
  await readFile(path.join(ROOT, "workbench", "manifest.json"), "utf8"));

test("every manifest page is in the hub, once, under its own group", () => {
  const hub = buildHub({ root: ROOT });
  const shown = hub.sections.flatMap((section) => section.pages);
  const ids = shown.map((page) => page.file);
  for (const page of manifest.pages) {
    assert.ok(ids.includes(page.file), `${page.file} is missing from the hub`);
  }
  assert.equal(new Set(ids).size, ids.length, "a page is shown twice");
  for (const group of manifest.groups) {
    const section = hub.sections.find((item) => item.key === group.key);
    assert.ok(section, `group ${group.key} has no section`);
  }
});

test("workbench files outside the manifest are still listed", () => {
  const hub = buildHub({ root: ROOT });
  const shown = new Set(hub.sections.flatMap((section) => section.pages.map((page) => page.file)));
  const skip = new Set(["index.html", "tabs.html", "workbench.html"]);
  const disk = readdirSync(path.join(ROOT, "workbench"))
    .filter((file) => file.endsWith(".html") && !skip.has(file));
  for (const file of disk) assert.ok(shown.has(file), `${file} is on disk but not in the hub`);
});

test("the app's own pages lead, and every page has a source url", () => {
  const hub = buildHub({ root: ROOT });
  assert.deepEqual(hub.app.map((page) => page.src), ["/lab", "/book", "/ph-nth-sandbox", "/finder"]);
  assert.equal(hub.total, hub.app.length
    + hub.sections.reduce((n, section) => n + section.pages.length, 0));
  for (const page of [...hub.app, ...hub.sections.flatMap((section) => section.pages)]) {
    assert.ok(page.src.startsWith("/"), page.title);
    assert.ok(page.title.length > 0, page.src);
  }
});

test("the hub page reads the module, and the lab moved off the root", async () => {
  const hubPage = await readFile(path.join(APP, "src", "pages", "index.astro"), "utf8");
  assert.ok(hubPage.includes('from "../lib/pages.js"'));
  assert.ok(hubPage.includes("<iframe"));
  assert.ok(hubPage.includes('href="/everything"'), "the hub no longer points at the full list");
  const all = await readFile(path.join(APP, "src", "pages", "everything.astro"), "utf8");
  assert.ok(all.includes("buildHub"));
  const lab = await readFile(path.join(APP, "src", "pages", "lab.astro"), "utf8");
  assert.ok(lab.includes("Square and frame lab"));
});

test("the tunnel url is the last one the log announced", () => {
  const log = [
    "INF | https://first-name-old.trycloudflare.com |",
    "2026-11-17 INF some other line",
    "INF | https://second-name-new.trycloudflare.com |",
    "INF connection registered",
  ].join("\n");
  assert.equal(latestTunnelUrl(log), "https://second-name-new.trycloudflare.com");
  assert.equal(latestTunnelUrl(""), null);
  assert.equal(latestTunnelUrl(null), null);
});

test("the home address is a plain http url on this machine", () => {
  for (const url of lanUrls()) {
    assert.match(url, /^http:\/\/\d+\.\d+\.\d+\.\d+:4321$/);
  }
});
