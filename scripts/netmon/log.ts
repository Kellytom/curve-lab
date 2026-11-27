/**
 * Reading and writing the JSONL logs, one JSON object per line.
 *
 * A line is written as one append, so a crash can leave at most one half line;
 * the reader skips it rather than failing the whole report.
 */
import { appendFileSync, mkdirSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import path from "node:path";

export function appendJsonl(file: string, entry: Record<string, unknown>): void {
  mkdirSync(path.dirname(file), { recursive: true });
  appendFileSync(file, JSON.stringify(entry) + "\n");
}

export function readJsonl(file: string): Record<string, any>[] {
  let text = "";
  try {
    text = readFileSync(file, "utf8");
  } catch {
    return [];
  }
  const rows: Record<string, any>[] = [];
  for (const line of text.split("\n")) {
    if (!line.trim()) continue;
    try {
      const row = JSON.parse(line);
      if (row && typeof row === "object" && !Array.isArray(row)) rows.push(row);
    } catch {
      // A half-written last line is not a reason to lose the file.
    }
  }
  return rows;
}

export function writeJson(file: string, value: unknown): void {
  mkdirSync(path.dirname(file), { recursive: true });
  const temporary = `${file}.tmp`;
  writeFileSync(temporary, JSON.stringify(value, null, 2) + "\n");
  renameSync(temporary, file);
}

/** Drop rows older than `before` (milliseconds). Used once a day. */
export function pruneJsonl(file: string, before: number): void {
  const rows = readJsonl(file).filter((row) => Number(row.ts) >= before);
  mkdirSync(path.dirname(file), { recursive: true });
  const temporary = `${file}.tmp`;
  writeFileSync(temporary, rows.map((row) => JSON.stringify(row)).join("\n") + (rows.length ? "\n" : ""));
  renameSync(temporary, file);
}
