// Print plates: white ground, 300 dpi, two grey tones, turned as the record says.
//
//   node scripts/print_plates.mjs --only c-0273,c-0290
//   node scripts/print_plates.mjs --all
//
// For each record: the spine (or the stored path) is turned by the record's `transform`,
// split at the vertical axis, and the two halves are drawn in two greys — one tone left,
// one tone right — so a two-colour press can tell them apart. Character rails are drawn
// from the record's own width, plus and minus when it has rows to build them from.
//
// Writes book/print/<uid>.svg and <uid>.png (long side 3000 px, 300 dpi).

import { existsSync, mkdirSync, readdirSync, readFileSync, renameSync, rmSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { chromium } from "playwright-core";
import { setDpi } from "./lib/png-dpi.mjs";
import { turn, frame as frameFor } from "./lib/plate-frame.mjs";
import { rowFor as plateRow, symmetricStrength, presetWidthPercent } from "./lib/plate-row.mjs";

// d3 does the geometry: the extents and the line generator. It is a dependency the app
// already carries (app/node_modules), so the plate uses the same library as the pages.
const d3 = await import(new URL("../app/node_modules/d3/dist/d3.mjs", import.meta.url).href);

const ROOT = path.resolve(import.meta.dirname, "..");
const OUT = path.join(ROOT, "book", "print");
const WEB = path.join(ROOT, "app", "public", "plates-web");
mkdirSync(OUT, { recursive: true });
mkdirSync(WEB, { recursive: true });

// The web copy: PNG at 1600 px. PNG is the one format that opens everywhere — LibreOffice,
// Pages, Word, a browser, a print shop — so the copy in git is a PNG too, not WebP. It is
// about three times the WebP and worth it: a picture nobody can place in a document is not
// preserved.
// The screenshot arrives as RGBA with three identical channels: the two greys are stored
// three times over. Rewrite it as grey + alpha — half the bytes, the same picture, and the
// `grey` in the file name becomes true.
function greyAlpha(file) {
  const temp = file.replace(/\.png$/, ".grey.png");
  try {
    execFileSync("sips", ["--matchTo", "/System/Library/ColorSync/Profiles/Generic Gray Profile.icc",
      file, "--out", temp], { stdio: "ignore" });
    renameSync(temp, file);
  } catch { rmSync(temp, { force: true }); }
}

const WEB_SIDE = 1600;
function webCopy(uid, png) {
  const small = path.join(WEB, `${uid}.tmp.png`);
  try {
    // resize, then drop to grey: the plate is grey on white, so an RGB PNG carries three
    // channels for one. Grey is about half the bytes and opens in every program.
    execFileSync("sips", ["-Z", String(WEB_SIDE), png, "--out", small], { stdio: "ignore" });
    execFileSync("sips", ["--matchTo", "/System/Library/ColorSync/Profiles/Generic Gray Profile.icc",
      small, "--out", path.join(WEB, `${uid}-${WEB_SIDE}-grey.png`)], { stdio: "ignore" });
  } catch { /* no sips: the 3000 px plate is still there */ }
  rmSync(small, { force: true });
}

const PLATE = (await import(path.join(ROOT, "workbench", "plate_math.js"))).default
  || (await import(path.join(ROOT, "workbench", "plate_math.js")));

const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));
// The saved values are the database's, exported to data/curves.json. The old
// workbench/curve-notes.json was a stale copy whose nulls fell through to the row
// preset, which is how the stored paths (c-0275..c-0368) gained a band they never
// asked for (2026-11-21).
const saved = JSON.parse(readFileSync(path.join(ROOT, "data", "curves.json"), "utf8"));
const noteOf = new Map((saved.rows || []).map((row) => [row.uid, row.note || {}]));
// The desk's decisions live in ONE copy: data/sandbox-curves.json (the database export).
// Reading the old workbench path in silence used the defaults for every curve, which is how
// character values stopped reaching the plates.
const DECISIONS = path.join(ROOT, "data", "sandbox-curves.json");
const decisionsRaw = existsSync(DECISIONS) ? JSON.parse(readFileSync(DECISIONS, "utf8")) : {};
const decisions = decisionsRaw.rows || decisionsRaw.curves || [];
if (!decisions.length) {
  console.log("WARNING: data/sandbox-curves.json is missing or empty — every plate will use " +
    "the measured preset (a 2 % drawn gap, plus 2.5, minus 0.1, bow). " +
    "Run: node scripts/export-data.mjs");
}
const extra = new Map(decisions.map((row) => [row.uid || row.name, row]));

const LONG_SIDE = 3000;
const STROKE = 0.0035;                // 3.5/1000 of the long side, the book rule
const LEFT = "#2b2b2b";               // the stroke
const RIGHT = "#8d8d8d";              // the lighter stroke tone of the two-tone split
const LIGHT_BAND = "#e2e2e2";          // between the left rail and the spine
const DARK_BAND = "#8a8a8a";           // between the right rail and the spine

const args = process.argv.slice(2);
const only = (() => {
  const at = args.indexOf("--only");
  return at >= 0 ? new Set(args[at + 1].split(",")) : null;
})();
const missing = args.includes("--missing");
const SVG_ONLY = args.includes("--svg-only");
// one tone (a single black) or two (dark left, grey right); the brief asked for two
const toneArg = (args.find((a) => a.startsWith("--tone=")) || "--tone=two").split("=")[1];
const singleTone = toneArg === "one";

// the one law lives in scripts/lib/plate-row.mjs: note -> desk row -> defaults
const rowFor = (record, extra) => plateRow(record, {
  note: noteOf.get(record.uid) || {},
  desk: extra.get(record.uid) || extra.get((record.aliases || [])[0]) || {},
});

/** the polyline split where it crosses x = 0, both halves returned in order */
function halves(points) {
  const left = [], right = [];
  for (let i = 0; i < points.length - 1; i += 1) {
    const a = points[i], b = points[i + 1];
    const target = ((a[0] + b[0]) / 2) < 0 ? left : right;
    target.push(a);
    if ((a[0] >= 0) !== (b[0] >= 0)) {
      const t = a[0] / (a[0] - b[0]);
      const crossing = [0, a[1] + (b[1] - a[1]) * t];
      left.push(crossing); right.push(crossing);
    }
  }
  const last = points[points.length - 1];
  (last[0] < 0 ? left : right).push(last);
  return { left, right };
}

// A record may hold several branches joined end to start. Drawn as one polyline they make a
// chord across the shape, so a jump bigger than 2 % of the curve's size is a break.
function splitBranches(points) {
  const xs = points.map((p) => p[0]), ys = points.map((p) => p[1]);
  const size = Math.hypot(Math.max(...xs) - Math.min(...xs), Math.max(...ys) - Math.min(...ys)) || 1;
  const runs = [];
  let run = [points[0]];
  for (let i = 1; i < points.length; i += 1) {
    const [x0, y0] = points[i - 1], [x1, y1] = points[i];
    if (Math.hypot(x1 - x0, y1 - y0) > 0.25 * size) { runs.push(run); run = [points[i]]; }
    else run.push(points[i]);
  }
  runs.push(run);
  return runs.filter((line) => line.length > 2);
}

function plateSvg(record) {
  const row = rowFor(record, extra);
  const degrees = Number(record.transform?.degrees || 0);
  // The offset curves: one character law, the two sides the same strength (the average of
  // the saved pair), the profile zero at both ends so the start and end gaps are the base.
  // No scaling of the drawn curve (2026-11-21, the operator: "the offset curves should look
  // the same on both sides, not thin on the right and wide on the left").
  const strength = symmetricStrength(row.character.plus, row.character.minus);
  const character = { ...row.character, plus: strength, minus: strength };
  // The plate never draws wider than the measured preset gap. A saved width can only lower
  // it (operator, 2026-11-22: "c-0006 is too wide"); the desk keeps the saved number.
  const widthPercent = Math.min(row.width.percent, presetWidthPercent(row.character));
  // A preset curve is normalised to the measured target gap; a saved width is used as asked.
  // A plate draws one or more segments. Usually it is one; a curve that turns tighter than
  // the asked width gets the band lifted across the turn and started again after it
  // (operator, 2026-11-22: "break the band at each sharp turn"). That is a display choice,
  // computed from the equation here; nothing about the break is stored.
  let segments = [];
  // One continuous band, never broken (operator, 2026-11-22: "it breaks too many places ...
  // just keep the side curves with tight thin, but as thick as reasonable until they start
  // to buckle, and i will manually adjust"). The guard already answers that: the band is cut
  // to the largest width that does not fold, and the tuning page names the cut.
  // a record that carries its branches separately gets one stroke per branch, which is what
  // the curve actually is; the single path stays for readers that expect it
  if (Array.isArray(record.branches) && record.branches.length > 1) {
    segments = record.branches.map((branch) => {
      const group = PLATE.pathGroup(branch, {
        widthPercent, plus: strength, minus: strength, profile: row.character.profile,
      });
      return group && group.paths.length
        ? { spine: group.paths[0], rails: group.paths.slice(1) }
        : { spine: branch.map(([x, y]) => [x, y]), rails: [] };
    });
  }
  if (!segments.length && Array.isArray(record.path) && record.path.length > 2) {
    const branches = splitBranches(record.path);
    if (branches.length > 1) {
      segments = branches.map((branch) => {
        const group = PLATE.pathGroup(branch, {
          widthPercent, plus: strength, minus: strength, profile: row.character.profile,
        });
        return group && group.paths.length
          ? { spine: group.paths[0], rails: group.paths.slice(1) }
          : { spine: branch, rails: [] };
      });
    }
  }
  if (!segments.length && Array.isArray(record.path) && record.path.length > 2) {
    const group = PLATE.pathGroup(record.path, {
      widthPercent, plus: strength, minus: strength,
      profile: row.character.profile,
    });
    if (group && group.paths.length) {
      segments = [{ spine: group.paths[0], rails: group.paths.slice(1) }];
    } else {
      segments = [{ spine: record.path.map(([x, y]) => [x, y]), rails: [] }];
    }
  } else if (!segments.length) {
    let group = null;
    try { group = PLATE.group ? PLATE.group({ ...row, width: { percent: widthPercent }, character }) : null; } catch { group = null; }
    if (group && group.paths && group.paths.length > 1) {
      segments = [{ spine: group.paths[0], rails: group.paths.slice(1) }];
    } else {
      segments = [{ spine: PLATE.spine(row.speedX, row.speedY, 400).map((s) => [s.x, s.y]), rails: [] }];
    }
  }
  // Every crossing on either rail, measured on the unturned geometry so the point can be used
  // to cut the curve later, then turned with it. The span between the two passes of a crossing
  // is the loop; the plate hides it, because a band that closes a loop on itself cannot be one
  // printed stroke, and records it in book/print/rail-holes.json.
  const cuts = [];
  const holes = segments.map((segment) => segment.rails.slice(0, 2).map((rail) => {
    if (!rail || rail.length < 4) return { crossings: [], spans: [] };
    const info = PLATE.railHoles(rail);
    for (const hit of info.crossings) cuts.push({ x: hit.x, y: hit.y });
    return info;
  }));
  const turned = segments.map((segment, index) => ({
    spine: turn(segment.spine, degrees),
    rails: segment.rails.map((rail) => turn(rail, degrees)),
    // one entry per rail: the runs left after the hidden spans, or an empty array when the
    // rail is drawn whole (no hole was found)
    runs: segment.rails.slice(0, 2).map((rail, side) => {
      const spans = (holes[index][side] || { spans: [] }).spans;
      if (!rail || !spans.length) return [];
      return PLATE.railRuns(rail, spans).map((run) => ({
        from: run.from,
        to: run.to,
        spine: turn(segment.spine.slice(run.from, run.to + 1), degrees),
        rail: turn(run.points, degrees),
      }));
    }),
  }));
  const cutPoints = cuts.map((hit) => turn([[hit.x, hit.y]], degrees)[0]);
  // the hidden spans, in model coordinates, one entry per rail that has one
  const holeRecords = [];
  segments.forEach((segment, index) => {
    (holes[index] || []).forEach((info, side) => {
      if (!info.spans.length) return;
      const rail = segment.rails[side];
      holeRecords.push({
        rail: side === 0 ? "plus" : "minus",
        spans: info.spans.map((span) => ({
          from: span.from,
          to: span.to,
          length: Number(span.length.toFixed(6)),
          start: rail[span.from],
          end: rail[span.to],
        })),
        crossings: info.crossings.map((hit) => ({
          x: Number(hit.x.toFixed(6)), y: Number(hit.y.toFixed(6)),
        })),
      });
    });
  });

  const all = turned.flatMap((segment) => [...segment.spine, ...segment.rails.flat()]);
  const [x0, x1] = d3.extent(all, (p) => p[0]);
  const [y0, y1] = d3.extent(all, (p) => p[1]);
  const w = x1 - x0 || 1, h = y1 - y0 || 1;
  const long = Math.max(w, h);
  const isWonkDouble = /^double-/i.test(record.name || "");
  // A cusp dot is deliberately larger than the working dots (three times, 2026-11-23) and it
  // sits at the cusp, which is often the outermost station: the margin must carry its radius,
  // or the dot is clipped by the canvas edge.
  const margin = 0.012 * long + (isWonkDouble ? 0.055 * long : 0);
  const boxW = w + 2 * margin, boxH = h + 2 * margin;
  const scale = LONG_SIDE / Math.max(boxW, boxH);      // the canvas long side is exactly 3000
  const pxW = Math.round(boxW * scale);
  const pxH = Math.round(boxH * scale);
  const k = scale;
  const ox = (pxW - w * k) / 2 - x0 * k;
  const oy = (pxH + h * k) / 2 + y0 * k;
  const px = ([x, y]) => [ox + x * k, oy - y * k];
  const gen = d3.line().x((p) => px(p)[0]).y((p) => px(p)[1]).curve(d3.curveLinear);
  const line = (points, colour, width) => points.length < 2 ? "" :
    `<path d="${gen(points)}" fill="none" stroke="${colour}" stroke-width="${width.toFixed(2)}" ` +
    `stroke-linecap="round" stroke-linejoin="round"/>`;

  const stroke = Math.max(1, STROKE * LONG_SIDE);
  // two tones without cutting the line: the whole spine is dark, then the same spine is
  // drawn again in the light tone inside a clip over x ≥ 0
  // the split is the figure's own centre line, so both tones always appear; a curve whose
  // centre is the y axis is split there
  const axisX = (x0 + x1) / 2;
  const axis = px([axisX, 0])[0].toFixed(2);
  // the bands: between each rail and the spine, filled. The right rail's band is the dark
  // grey, the left rail's the light one; the spine and the rails are then stroked on top.
  // nonzero, not even-odd: where a rail crosses itself the band fills as one solid shape, not
  // beveled out. A rail with a hidden span is filled run by run, so the loop stays empty.
  const bandPath = (spine, rail, fill) => (rail && rail.length > 2)
    ? `<path d="${gen([...spine, ...[...rail].reverse()])}Z" fill="${fill}" ` +
      `fill-rule="nonzero" stroke="none"/>`
    : "";
  const band = (segment, side, fill) => {
    const rail = segment.rails[side];
    if (!rail || rail.length <= 2) return "";
    const runs = segment.runs[side];
    return runs && runs.length
      ? runs.map((run) => bandPath(run.spine, run.rail, fill)).join("")
      : bandPath(segment.spine, rail, fill);
  };
  const bands = turned.map((segment) => segment.rails.length >= 2
    ? band(segment, 0, LIGHT_BAND) + band(segment, 1, DARK_BAND)
    : "").join("");
  const railLines = turned.map((segment) =>
    segment.rails.slice(0, 2).map((rail, side) => {
      const runs = segment.runs[side];
      const pieces = runs && runs.length ? runs.map((run) => run.rail) : [rail];
      return pieces.map((piece) => line(piece, "#3a3a3a", stroke * 0.6)).join("");
    }).join("")).join("");
  const spineLeft = turned.map((segment) => line(segment.spine, LEFT, stroke)).join("");
  const spineRight = turned.map((segment) => line(segment.spine, RIGHT, stroke)).join("");
  const dotLines = cutPoints.map(([x, y]) => {
    const [cx, cy] = px([x, y]);
    const r = Math.max(3, 0.01 * LONG_SIDE);
    return `<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${r.toFixed(1)}" fill="#b03a2e"/>`;
  }).join("");
  // A cusp on a wonk-derived curve (the doubles): the tangent reverses sharply. The dot is
  // decorative, so it is larger than the working dots and in a blue whose luminance matches the
  // light grey, so a grey print sees a neutral grey, not a dark spot. #7290c0 -> 141, the same
  // as #8d8d8d. Detection is on the source stations, before the plate's smoothing, or a cusp is
  // rounded away and never seen.
  const cuspPoints = [];
  if (isWonkDouble) {
    const source = Array.isArray(record.path) && record.path.length > 2
      ? record.path.map(([x, y]) => [x, y])
      : PLATE.spine(record.speedX || [0], record.speedY || [0], 700).map((s) => [s.x, s.y]);
    const [sx0, sy0, sx1, sy1] = d3.extent(source, (p) => p[0]).concat(d3.extent(source, (p) => p[1]));
    const size = Math.hypot((sx1 || 0) - (sx0 || 0), (sy1 || 0) - (sy0 || 0)) || 1;
    let last = null;
    for (let i = 1; i < source.length - 1; i += 1) {
      const a = source[i - 1], b = source[i], c = source[i + 1];
      const v1 = [b[0] - a[0], b[1] - a[1]];
      const v2 = [c[0] - b[0], c[1] - b[1]];
      const l1 = Math.hypot(...v1) || 1, l2 = Math.hypot(...v2) || 1;
      const dot = (v1[0] * v2[0] + v1[1] * v2[1]) / (l1 * l2);
      const angle = (Math.acos(Math.max(-1, Math.min(1, dot))) * 180) / Math.PI;
      if (angle > 165) {
        if (!last || Math.hypot(b[0] - last[0], b[1] - last[1]) > 0.01 * size) {
          cuspPoints.push(b);
          last = b;
        }
      }
    }
  }
  // where the curve begins and ends, so a turn is readable at a glance
  const [startX, startY] = px(turned[0].spine[0]);
  const endSpine = turned[turned.length - 1].spine;
  const [endX, endY] = px(endSpine[endSpine.length - 1]);
  const marker = Math.max(4, 0.014 * LONG_SIDE);
  // A closed curve starts and ends at the same point: show the start as a blue disc inside a
  // green ring, so both are readable instead of one dot hiding the other.
  const coincident = Math.hypot(endX - startX, endY - startY) < marker * 1.5;
  const cuspDots = cuspPoints.map(([x, y]) => {
    const turned = turn([[x, y]], degrees)[0];
    const [cx, cy] = px(turned);
    // A cusp dot is three times the working-dot size (operator, 2026-11-23: "make those dots
    // triple that size"): at 3000 px it is 153 px across, large enough to read as a deliberate
    // stop at the cusp rather than a spot.
    const r = Math.max(18, 0.051 * LONG_SIDE);
    return `<circle cx="${cx.toFixed(1)}" cy="${cy.toFixed(1)}" r="${r.toFixed(1)}" fill="#7290c0" fill-opacity="0.85"/>`;
  }).join("");
  const endLines = coincident
    ? `<circle cx="${startX.toFixed(1)}" cy="${startY.toFixed(1)}" r="${(marker * 1.7).toFixed(1)}" ` +
      `fill="none" stroke="#e8890c" stroke-width="${(marker * 0.55).toFixed(1)}"/>` +
      `<circle cx="${startX.toFixed(1)}" cy="${startY.toFixed(1)}" r="${marker.toFixed(1)}" fill="#1f5fbf"/>`
    : `<circle cx="${startX.toFixed(1)}" cy="${startY.toFixed(1)}" r="${marker.toFixed(1)}" fill="#1f5fbf"/>` +
      `<circle cx="${endX.toFixed(1)}" cy="${endY.toFixed(1)}" r="${marker.toFixed(1)}" fill="#e8890c"/>`;
  const body = singleTone
    ? [bands, railLines, spineLeft, dotLines, endLines, cuspDots].join("")
    : [
        bands,
        railLines,
        spineLeft,
        `<clipPath id="right"><rect x="${axis}" y="0" width="${(pxW - Number(axis)).toFixed(2)}" height="${pxH}"/></clipPath>`,
        `<g clip-path="url(#right)">${spineRight}</g>`,
        dotLines,
        endLines,
        cuspDots,
      ].join("");
  const railCount = turned.reduce((n, segment) => n + segment.rails.length, 0);
  return { svg: `<svg xmlns="http://www.w3.org/2000/svg" width="${pxW}" height="${pxH}" viewBox="0 0 ${pxW} ${pxH}">${body}</svg>`,
    pxW, pxH, degrees, rails: railCount, segments: segments.length,
    cuts: cuts.map((hit) => ({ x: hit.x, y: hit.y })),
    holes: holeRecords };
}

const records = registry.curves.filter((record) => {
  if (only && !only.has(record.uid)) return false;
  if (missing && existsSync(path.join(OUT, `${record.uid}.png`))) return false;
  return true;
});
// The SVG is the plate; the PNG is a convenience raster. --svg-only writes every SVG in
// seconds (no browser, no screenshot), which is the fast iteration the operator asked for.
const browser = SVG_ONLY ? null : await chromium.launch({
  executablePath: process.env.CHROME_PATH || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
const page = browser ? await browser.newPage() : null;

let done = 0;
const cutList = [];
const holeList = [];
for (const record of records) {
  const { svg, pxW, pxH, degrees, rails, cuts, holes } = plateSvg(record);
  if (cuts && cuts.length) cutList.push({ uid: record.uid, name: record.name, points: cuts });
  if (holes && holes.length) holeList.push({ uid: record.uid, name: record.name, rails: holes });
  // Naming: <uid>-<long side>-<tone>-<dpi>.<ext>. The size and tone are in the name so a
  // folder of renders can be read without opening one.
  const svgPath = path.join(OUT, `${record.uid}.svg`);
  const pngPath = path.join(OUT, `${record.uid}-${LONG_SIDE}-grey-300dpi.png`);
  writeFileSync(svgPath, svg);
  if (SVG_ONLY) {
    done += 1;
    continue;
  }
  await page.setViewportSize({ width: pxW, height: pxH });
  // omitBackground keeps the alpha: what is not drawn is transparent, not white
  await page.setContent(`<body style="margin:0;background:transparent">${svg}</body>`);
  await page.screenshot({ path: pngPath, clip: { x: 0, y: 0, width: pxW, height: pxH },
    omitBackground: true });
  greyAlpha(pngPath);
  setDpi(pngPath, 300);
  webCopy(record.uid, pngPath);
  done += 1;
  if (done <= 12 || done % 50 === 0) {
    console.log(`${record.uid.padEnd(8)} ${record.name.slice(0, 26).padEnd(26)} ` +
      `turn ${String(degrees).padStart(3)}°  ${pxW}×${pxH}  rails ${rails}`);
  }
}
if (browser) await browser.close();

// A partial run (--only, --missing) must never replace a whole index with its own few
// curves: a `--only` run once wrote index.json from the two curves it had drawn and every
// other entry vanished (register row 37). A full run replaces the file; a partial run
// merges, replacing only the entries it just measured.
const partialRun = Boolean(only || missing);
function writeIndex(file, header, entries) {
  const kept = partialRun
    ? (() => {
        try { return JSON.parse(readFileSync(file, "utf8")).curves || []; } catch { return []; }
      })()
    : [];
  const byUid = new Map(kept.map((entry) => [entry.uid, entry]));
  for (const entry of entries) byUid.set(entry.uid, entry);
  const curves = [...byUid.values()].sort((a, b) => String(a.uid).localeCompare(String(b.uid)));
  writeFileSync(file, `${JSON.stringify({ ...header, curves }, null, 1)}\n`);
  return curves.length;
}

// The future cut points, in the curve's own model coordinates: where either rail crosses
// itself and has to be cut before it can be a printed side curve.
const cutsPath = path.join(OUT, "cuts.json");
const cutCount = writeIndex(cutsPath, {
  format: "curve-lab.cuts/1",
  note: "Self-crossings of a character rail, in model coordinates. Each point is a place " +
    "the rail has to be cut; the dot on the plate marks the same point.",
}, cutList);
console.log(`${cutList.length} curve(s) with rail cut points -> ${path.relative(ROOT, cutsPath)}` +
  ` (${cutCount} in the index)`);

// The hidden spans: the loop between the two passes of a crossing, which the plate does not
// draw or fill. Indices are into the rail as this script builds it; the endpoints are in
// model coordinates, so a later cut can use them without the plate's turn.
const holesPath = path.join(OUT, "rail-holes.json");
const holeCount = writeIndex(holesPath, {
  format: "curve-lab.rail-holes/1",
  note: "The span of a character rail hidden on the plate: the small loop between the two " +
    "passes of a self-crossing. from/to index the rail; start/end are model coordinates.",
}, holeList);
console.log(`${holeList.length} curve(s) with hidden rail spans -> ${path.relative(ROOT, holesPath)}` +
  ` (${holeCount} in the index)`);

// a plate is replaced, never duplicated: the expected names are known, so anything else in
// the folder is an orphan and is removed
const expected = new Set(["cuts.json", "rail-holes.json"]);
for (const record of registry.curves) {
  expected.add(`${record.uid}.svg`);
  expected.add(`${record.uid}-${LONG_SIDE}-grey-300dpi.png`);
}
let pruned = 0;
for (const file of readdirSync(OUT)) {
  if (expected.has(file)) continue;
  rmSync(path.join(OUT, file));
  pruned += 1;
}
console.log(SVG_ONLY
  ? `${done} plate SVGs written to book/print (no raster pass)`
  : `${done} plates written to book/print at ${LONG_SIDE} px, 300 dpi` +
    (pruned ? `; ${pruned} orphan files removed` : ""));
