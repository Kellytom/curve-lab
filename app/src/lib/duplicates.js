// @ts-check
// Which curves the duplicate audit says are the same drawing.
//
// The audit writes state/DUPLICATES-int.md; this reads its table so a page can
// mark the rows. The file is the record when the page is not open, and the
// page is the prompt when the file is not read.
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

const UID = /^c-\d{4}$/;

/**
 * @param {string} text
 * @returns {Map<string, string[]>}
 */
export function parseDuplicates(text) {
  const map = new Map();
  for (const line of String(text || "").split("\n")) {
    if (!line.trim().startsWith("|")) continue;
    const cells = line.split("|").map((cell) => cell.trim());
    const uids = (cells[3] || "").split(",").map((uid) => uid.trim()).filter((uid) => UID.test(uid));
    if (uids.length < 2) continue;
    for (const uid of uids) map.set(uid, uids.filter((other) => other !== uid));
  }
  return map;
}

/**
 * @param {string} root
 * @returns {Map<string, string[]>}
 */
export function readDuplicates(root) {
  const file = path.join(root, "state", "DUPLICATES-int.md");
  if (!existsSync(file)) return new Map();
  return parseDuplicates(readFileSync(file, "utf8"));
}
