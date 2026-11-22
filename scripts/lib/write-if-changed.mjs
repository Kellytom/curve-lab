// Write a file only when its bytes change.
//
// Why: the Astro dev server watches app/public and app/src, so an unconditional write
// reloaded every open page. The launch agent re-runs `npm run dev` on a loop, and its
// `predev` step ran the ornament writer, which wiped the folder and rewrote all 371
// SVGs every ten seconds (2026-11-22, the operator: "the page keeps refreshing
// constantly"). The fix is not to write at all when nothing changed.
import { readFileSync, writeFileSync } from "node:fs";

export function writeIfChanged(file, text) {
  try {
    if (readFileSync(file, "utf8") === text) return false;
  } catch {
    /* missing: write it */
  }
  writeFileSync(file, text);
  return true;
}
