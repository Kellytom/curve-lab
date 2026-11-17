// Save or reopen the light browser's tabs.
//
//   node scripts/tabs.mjs save     # running light Chrome (CDP 9224) -> tabs.json
//   node scripts/tabs.mjs open     # one URL per line; the launcher uses this
//   node scripts/tabs.mjs list     # title and URL, for looking
//   node scripts/tabs.mjs index    # the local session HTML; the launcher opens it
//   node scripts/tabs.mjs status    # where the file is and how old it is
//
// The URL snapshot lives at ~/.config/curve-lab/tabs.json; the local session
// page is workbench/tabs.html, generated from it and ignored by git. Only
// http(s)/file pages are kept; devtools and chrome:// pages are not part of a
// work session.

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const PORT = process.env.CURVE_TABS_PORT || "9224";
const FILE = path.join(os.homedir(), ".config", "curve-lab", "tabs.json");
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const INDEX = path.join(ROOT, "workbench", "tabs.html");
const INDEX_URL = pathToFileURL(INDEX).href;
const mode = process.argv[2] || "save";

const usage = `usage: node scripts/tabs.mjs <save|open|list|status>`;

function read() {
  return JSON.parse(readFileSync(FILE, "utf8"));
}

if (mode === "save") {
  let tabs;
  try {
    const response = await fetch(`http://127.0.0.1:${PORT}/json/list`);
    tabs = await response.json();
  } catch {
    console.error(
      `the light browser is not answering on 127.0.0.1:${PORT}. ` +
        "Launch it once with scripts/chrome-curve.command; older instances " +
        "started before the debugging port was added must be relaunched.");
    process.exit(1);
  }
  const pages = tabs
    .filter((tab) => tab.type === "page"
      && /^(https?|file):/.test(tab.url || "")
      && tab.url !== INDEX_URL)
    .map((tab) => ({ url: tab.url, title: tab.title || "" }));
  const saved = new Date().toISOString();
  mkdirSync(path.dirname(FILE), { recursive: true });
  writeFileSync(
    FILE,
    JSON.stringify({ format: "curve-lab.tabs/1", saved, pages }, null, 1) + "\n",
  );
  const escape = (text) => String(text).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);
  const rows = pages.map((page) => `      <li><a href="${escape(page.url)}" target="_blank" rel="noreferrer">`
    + `${escape(page.title || page.url)}</a><br><code>${escape(page.url)}</code></li>`)
    .join("\n");
  writeFileSync(INDEX, `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Curve lab — saved tabs</title>
<style>
body{margin:0;background:#f6f1e4;color:#2e2413;font:15px/1.55 Georgia,serif}
main{max-width:760px;margin:0 auto;padding:32px 22px 60px}
h1{font-size:22px;margin:0 0 4px}
p{color:#7b6c4e;margin:0 0 20px}
ol{padding-left:20px}
li{margin:0 0 16px}
a{color:#8c6a21;font-size:17px}
code{font:11px ui-monospace,Menlo,monospace;color:#777}
</style></head><body><main>
<h1>Curve lab — saved tabs</h1>
<p>${pages.length} tab${pages.length === 1 ? "" : "s"}, saved ${saved}.
Open the one you need; the browser stays light. Regenerate with
<code>scripts/chrome-curve.command --save</code>.</p>
<ol>
${rows}
</ol>
</main></body></html>
`);
  console.log(`${pages.length} tab${pages.length === 1 ? "" : "s"} saved to ${FILE}`);
  console.log(`session index: ${INDEX}`);
} else if (mode === "open") {
  if (!existsSync(FILE)) {
    console.error(`no saved tabs at ${FILE}`);
    process.exit(1);
  }
  read().pages.forEach((page) => console.log(page.url));
} else if (mode === "index") {
  if (!existsSync(INDEX)) {
    console.error(`no session index at ${INDEX}`);
    process.exit(1);
  }
  console.log(INDEX);
} else if (mode === "list") {
  if (!existsSync(FILE)) {
    console.error(`no saved tabs at ${FILE}`);
    process.exit(1);
  }
  const data = read();
  console.log(`${data.pages.length} tabs, saved ${data.saved}`);
  data.pages.forEach((page) => console.log(`  ${page.title || "(no title)"}\n    ${page.url}`));
} else if (mode === "status") {
  if (!existsSync(FILE)) {
    console.log(`no saved tabs at ${FILE}`);
  } else {
    const data = read();
    console.log(`${data.pages.length} tabs saved ${data.saved}\n${FILE}`);
  }
} else {
  console.error(usage);
  process.exit(2);
}
