// Every book plate is 3000 px on the long side at 300 dpi, and every curve has one.
//
//   node scripts/check_book_plates.mjs
//
// The book's rules are in book/README.md: a 3000 px long side (10 in at 300 dpi), so a page can
// downscale it, and a PNG pHYs of 300 dpi so LibreOffice inserts it at the right size. The plate
// is written by scripts/print_plates.mjs; this reads the header only, so it is a second to run.
// A plate with no record, or a record with no plate, is a fault — the operator asked for every
// curve to be in the database and the book is drawn from it.

import { readFileSync, existsSync } from "node:fs";
import path from "node:path";

const ROOT = path.resolve(import.meta.dirname, "..");
const DIR = path.join(ROOT, "book", "print");
const registry = JSON.parse(readFileSync(path.join(ROOT, "workbench", "curve-registry.json"), "utf8"));

const pngHeader = (file) => {
  const buf = readFileSync(file);
  if (buf.length < 8 || buf.subarray(0, 8).toString("hex") !== "89504e470d0a1a0a") return null;
  let pos = 8;
  const out = { width: 0, height: 0, dpiX: null, dpiY: null };
  while (pos + 8 <= buf.length) {
    const length = buf.readUInt32BE(pos);
    const type = buf.subarray(pos + 4, pos + 8).toString("ascii");
    if (type === "IHDR") {
      out.width = buf.readUInt32BE(pos + 8);
      out.height = buf.readUInt32BE(pos + 12);
    } else if (type === "pHYs") {
      const unit = buf[pos + 16];
      if (unit === 1) {
        out.dpiX = Math.round(buf.readUInt32BE(pos + 8) * 0.0254);
        out.dpiY = Math.round(buf.readUInt32BE(pos + 12) * 0.0254);
      }
    } else if (type === "IDAT") break;
    pos += 12 + length;
  }
  return out;
};

const bad = [];
for (const curve of registry.curves) {
  const file = path.join(DIR, `${curve.uid}-3000-grey-300dpi.png`);
  if (!existsSync(file)) {
    bad.push(`${curve.uid} ${curve.name}: no 3000 px plate`);
    continue;
  }
  const head = pngHeader(file);
  if (!head) {
    bad.push(`${curve.uid}: not a PNG`);
    continue;
  }
  const long = Math.max(head.width, head.height);
  if (long !== 3000) bad.push(`${curve.uid}: long side ${long} px, not 3000`);
  if (head.dpiX !== 300 || head.dpiY !== 300) {
    bad.push(`${curve.uid}: ${head.dpiX} × ${head.dpiY} dpi, not 300`);
  }
}

for (const line of bad) console.log(`book plates: ${line}`);
if (bad.length) {
  console.log(`book plates: ${bad.length} problem(s) across ${registry.curves.length} curves`);
  process.exit(1);
}
console.log(`book plates: ok (${registry.curves.length} curves, every plate 3000 px at 300 dpi)`);
