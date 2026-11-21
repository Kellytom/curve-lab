// The book gallery, in plain Node so the Astro page and its tests share it.
//
// Three lists, in the order the operator reads them: the plates starred in the
// lab, the two simple central designs (cross and leaf), then the single curves.
// A caption comes from workbench/plate_compose.js — the same call the exporter
// makes — so the page and the PNG never disagree about what a plate is.

import { existsSync, readFileSync, statSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);

const APP_ROOT = fileURLToPath(new URL("../..", import.meta.url));
export const PLATE_ID = /^[a-z0-9][a-z0-9-]*-[0-9]+-t-exp-c-[0-9]{4}$/;

export function repoRoot(root) {
  const chosen = root || process.env.CURVE_LAB_ROOT;
  if (chosen) return path.resolve(chosen);
  // The built server runs from app/ and the tests from the repo, so look for the
  // book manifest rather than trusting one relative path.
  for (const candidate of [path.resolve(process.cwd(), ".."), process.cwd(),
                           path.resolve(APP_ROOT, "..")]) {
    if (existsSync(path.join(candidate, "book", "old-plates.json"))) return candidate;
  }
  return path.resolve(APP_ROOT, "..");
}

// The caption comes from one module at the repo root. It is required by absolute
// path because the bundle moves this file into app/dist/server/chunks.
const composers = new Map();
function composer(repo) {
  if (!composers.has(repo)) {
    const file = path.join(repo, "workbench", "plate_compose.js");
    composers.set(repo, require(file).composePlate);
  }
  return composers.get(repo);
}

function readJson(file, fallback) {
  if (!existsSync(file)) return fallback;
  return JSON.parse(readFileSync(file, "utf8"));
}

// A missing star file is a prompt, not an error: the lab writes one only after
// the operator presses save to workbench.
export function readStarred(file) {
  if (!existsSync(file)) return { present: false, plates: [] };
  const data = readJson(file, {});
  const plates = Array.isArray(data.plates) ? data.plates : [];
  return { present: true, plates: plates.filter((plate) => PLATE_ID.test(plate.id || "")) };
}

function pngSize(file) {
  try {
    if (!statSync(file).isFile()) return null;
    const data = readFileSync(file);
    if (data.length < 24 || data.toString("ascii", 12, 16) !== "IHDR") return null;
    return [data.readUInt32BE(16), data.readUInt32BE(20)];
  } catch {
    return null;
  }
}

function plateItem(plate, rows, plateDir, composePlate) {
  const id = plate.id;
  let note;
  try {
    note = composePlate(plate, rows).note;
  } catch (error) {
    // A star can name a curve the saved set no longer holds. The plate is still
    // listed, with the reason on it, rather than dropped from the gallery.
    note = `could not compose: ${error.message || error}`;
  }
  const file = path.join(plateDir, `${id}.png`);
  const size = pngSize(file);
  return {
    id,
    kind: plate.kind,
    note,
    image: size ? `/api/plate/${id}` : null,
    width: size ? size[0] : null,
    height: size ? size[1] : null,
  };
}

export function buildGallery({ root, starred: givenStarred } = {}) {
  const repo = repoRoot(root);
  const manifest = readJson(path.join(repo, "book", "old-plates.json"), { plates: [] });
  const curves = readJson(path.join(repo, "workbench", "real-curves.json"), { curves: [] });
  const rows = Object.fromEntries((curves.curves || []).map((row) => [row.name, row]));
  const plateDir = path.join(repo, "book", "old-plates");

  const starredFile = path.join(repo, "workbench", "starred.json");
  const starred = givenStarred
    ? { present: true, plates: givenStarred }
    : readStarred(starredFile);

  const manifestPlates = Array.isArray(manifest.plates) ? manifest.plates : [];
  const starPlates = starred.plates.map((plate) => ({ ...plate, kind: "star" }));
  const composePlate = composer(repo);
  const item = (plate) => plateItem(plate, rows, plateDir, composePlate);
  const stars = starPlates.map(item);
  const designs = manifestPlates.filter((plate) => plate.kind === "design").map(item);
  const singles = manifestPlates.filter((plate) => plate.kind !== "design").map(item);

  return {
    stars,
    designs,
    singles,
    counts: {
      stars: stars.length,
      designs: designs.length,
      singles: singles.length,
      total: stars.length + designs.length + singles.length,
    },
    starredPresent: starred.present,
    missingImages: [...stars, ...designs, ...singles]
      .filter((item) => !item.image).map((item) => item.id),
  };
}
