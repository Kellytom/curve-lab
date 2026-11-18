// The hub's page list: every page the app should show, with the group headings
// the workbench manifest already uses. The manifest is the source for the 86
// curated pages; any other .html in workbench/ is listed under "Also in
// workbench" rather than left invisible.

import { readdirSync, readFileSync } from "node:fs";
import path from "node:path";
import { repoRoot } from "./gallery.js";

// The old hub, the browser tabs page and a redirect stub are not content.
const SKIP = new Set(["index.html", "tabs.html", "workbench.html"]);

function titleFromFile(file) {
  const stem = file.replace(/\.html$/, "").replace(/\//g, " · ");
  return stem.replace(/-/g, " ").replace(/\bph\b/gi, "PH")
    .replace(/^\w/, (c) => c.toUpperCase());
}

export function buildHub({ root } = {}) {
  const repo = repoRoot(root);
  const manifest = JSON.parse(
    readFileSync(path.join(repo, "workbench", "manifest.json"), "utf8"));

  const groups = manifest.groups.map((group) => ({
    key: group.key,
    label: group.label,
    pages: [],
  }));
  const byKey = new Map(groups.map((group) => [group.key, group]));
  const listed = new Set();

  for (const page of manifest.pages) {
    listed.add(page.file);
    const group = byKey.get(page.group) || groups[0];
    group.pages.push({
      key: page.key,
      file: page.file,
      title: page.title,
      purpose: page.purpose,
      src: `/pages/${page.file}`,
    });
  }

  const extra = readdirSync(path.join(repo, "workbench"))
    .filter((file) => file.endsWith(".html") && !listed.has(file) && !SKIP.has(file))
    .sort()
    .map((file) => ({
      key: file.replace(/\.html$/, ""),
      file,
      title: titleFromFile(file),
      purpose: "not in the manifest — listed from the workbench folder",
      src: `/pages/${file}`,
    }));

  const sections = groups.filter((group) => group.pages.length);
  if (extra.length) {
    sections.push({ key: "unlisted", label: "Also in workbench", pages: extra });
  }

  // The app's own pages lead: they are the future, the workbench pages are the
  // material they are being ported from.
  const app = [
    { key: "lab", title: "The lab", src: "/lab",
      purpose: "Square and frame lab: the saved curves on 90° edges, stars, save." },
    { key: "book", title: "The book gallery", src: "/book",
      purpose: "The exported plates: stars, cross and leaf, then the singles." },
    { key: "finder", title: "Curve finder", src: "/finder",
      purpose: "Properness, collapse and the curvature peak for the first curve families." },
  ];

  const total = app.length + sections.reduce((n, group) => n + group.pages.length, 0);

  return { app, sections, total };
}
