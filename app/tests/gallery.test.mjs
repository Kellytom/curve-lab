// The Astro book gallery: the plates come from the files, not from a hand list.
//
// The one fault this guards: a plate in book/plates.json or workbench/starred.json
// that the gallery does not show. Both files are read here, and the page reads
// them through src/lib/gallery.js.

import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { buildGallery, readStarred, PLATE_ID } from "../src/lib/gallery.js";

const APP = fileURLToPath(new URL("..", import.meta.url));
const ROOT = path.resolve(APP, "..");
const manifest = JSON.parse(
  await readFile(path.join(ROOT, "book", "old-plates.json"), "utf8"));
const manifestDesigns = manifest.plates.filter((plate) => plate.kind === "design");

test("both simple designs are listed, each with its caption and its PNG", () => {
  const gallery = buildGallery({ root: ROOT, starred: [] });
  assert.deepEqual(gallery.designs.map((plate) => plate.id),
    manifestDesigns.map((plate) => plate.id));
  assert.equal(gallery.designs.length, 2, "cross and leaf");
  for (const plate of gallery.designs) {
    assert.ok(plate.note.length > 0, `${plate.id} has no caption`);
    assert.ok(plate.image, `${plate.id} has no exported PNG`);
    assert.ok(plate.width > 0 && plate.height > 0, `${plate.id} has no pixel size`);
  }
});

test("every manifest plate appears exactly once across the sections", () => {
  const gallery = buildGallery({ root: ROOT, starred: [] });
  const ids = [...gallery.designs, ...gallery.singles].map((plate) => plate.id);
  assert.equal(ids.length, manifest.plates.length);
  assert.equal(new Set(ids).size, manifest.plates.length, "a plate is listed twice");
  for (const plate of manifest.plates) {
    assert.ok(ids.includes(plate.id), `${plate.id} is missing from the gallery`);
  }
});

test("every starred plate is listed, in its own section, above the designs", () => {
  const starred = [
    { id: "u-bowl-arch-1-t-exp-c-0301", descriptor: "u-bowl-arch", variant: 1,
      kind: "star", form: "arch", curve: "u-bowl", serial: 301 },
    { id: "swan-single-1-t-exp-c-0302", descriptor: "swan-single", variant: 1,
      kind: "star", form: "single", curve: "swan", serial: 302 },
  ];
  const gallery = buildGallery({ root: ROOT, starred });
  assert.deepEqual(gallery.stars.map((plate) => plate.id), starred.map((plate) => plate.id));
  for (const plate of gallery.stars) {
    assert.match(plate.note, /starred/, `${plate.id} is not marked as a star`);
  }
  assert.equal(gallery.counts.total, manifest.plates.length + starred.length);
});

test("a missing star file is a prompt, not an error", async () => {
  const empty = await mkdtemp(path.join(tmpdir(), "gallery-"));
  assert.deepEqual(readStarred(path.join(empty, "workbench", "starred.json")),
    { present: false, plates: [] });
  const gallery = buildGallery({ root: ROOT, starred: [] });
  assert.equal(gallery.stars.length, 0);
  await rm(empty, { recursive: true, force: true });
});

test("a damaged star entry is listed and named, not dropped", () => {
  const gallery = buildGallery({ root: ROOT, starred: [
    { id: "ghost-single-1-t-exp-c-0303", descriptor: "ghost-single", variant: 1,
      kind: "star", form: "single", curve: "no-such-curve", serial: 303 },
  ] });
  assert.equal(gallery.stars.length, 1);
  assert.match(gallery.stars[0].note, /could not compose/);
  assert.equal(gallery.stars[0].image, null);
});

test("the page reads the gallery module, and the generated page is gone", async () => {
  const page = await readFile(path.join(APP, "src", "pages", "illuminations.astro"), "utf8");
  assert.ok(page.includes('from "../lib/gallery.js"'));
  assert.ok(page.includes("buildGallery"));
  assert.ok(page.includes("Framed Quintic symmetric figures"));
  assert.ok(page.includes("Simple framed symmetric central figures"));
  // The generated gallery is gone. A small redirect file may exist for the old
  // Python server at :8003 — it must contain no figures, only a jump to /book.
  const legacy = path.join(ROOT, "book", "index.html");
  if (existsSync(legacy)) {
    const text = (await readFile(legacy, "utf8"));
    assert.ok(text.includes("location.replace"), "book/index.html is not a redirect");
    assert.ok(text.includes("/illuminations"), "the redirect does not reach the gallery");
    assert.ok(!text.includes("<figure>"), "book/index.html is still the generated gallery");
  }
});

test("the star file is read through the same plate-name rule as the save", async () => {
  assert.ok(PLATE_ID.test("amper-1-t-exp-c-0101"));
  assert.ok(!PLATE_ID.test("../book/plates/amper-1-t-exp-c-0101"));
  const root = await mkdtemp(path.join(tmpdir(), "starred-"));
  await mkdir(path.join(root, "workbench"), { recursive: true });
  await writeFile(path.join(root, "workbench", "starred.json"), JSON.stringify({
    format: "starred/1",
    plates: [
      { id: "amper-1-t-exp-c-0101", descriptor: "amper", variant: 1, form: "single", curve: "amper" },
      { id: "bad", descriptor: "bad", variant: 1, form: "single", curve: "amper" },
    ],
  }));
  const read = readStarred(path.join(root, "workbench", "starred.json"));
  assert.equal(read.present, true);
  assert.deepEqual(read.plates.map((plate) => plate.id), ["amper-1-t-exp-c-0101"]);
  await rm(root, { recursive: true, force: true });
});
