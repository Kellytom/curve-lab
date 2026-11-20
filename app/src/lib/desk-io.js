// The desk's input and output, in one place.
//
// Every page that decides on a curve uses these three calls, so the rules live once: a
// failed read is never a write, a save reports the server's own message, and a duplicate
// name is refused by the server and shown to the person who typed it.

const ENDPOINT = "/api/sandbox-curves";

export async function readDecisions() {
  const response = await fetch(ENDPOINT);
  if (!response.ok) throw new Error(`load failed: ${response.status}`);
  const { curves } = await response.json();
  return curves || [];
}

export async function saveDecision(curve) {
  const response = await fetch(ENDPOINT, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ curves: [curve] }),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || `save failed: ${response.status}`);
  return body;
}

export async function removeDecisions(names) {
  if (!names.length) return { removed: 0 };
  const response = await fetch(ENDPOINT, {
    method: "DELETE",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ names }),
  });
  if (!response.ok) throw new Error(`delete failed: ${response.status}`);
  return response.json();
}

/** names that two rows share, lower-cased; a duplicate is a fault, not a preference */
export function duplicateNames(rows) {
  const seen = new Map();
  const dupes = new Set();
  for (const row of rows) {
    const name = String(row.curveName || "").trim().toLowerCase();
    if (!name) continue;
    if (seen.has(name)) dupes.add(name);
    seen.set(name, row.name);
  }
  return dupes;
}
