// The hybrid desk's one rule: a decision is a save, and a save never touches another
// candidate's row. Each candidate is its own name in /api/sandbox-curves.
//
// Spec: state/SPEC-hybrids-int.md. Check: app/scripts/check-hybrids-page.mjs.

const ENDPOINT = "/api/sandbox-curves";

// The naming desk's first rule: a failed read is never a write. Until the decisions have
// loaded, nothing on the page may be saved — otherwise an empty card would overwrite a
// real one.
const state = { readOk: false, message: "" };

// The naming desk's draft rule: a name being typed is kept in this browser, and a refresh
// restores it. A draft never hides a newer save, and a save clears it.
const DRAFTS = "hybrid-name-drafts";

function readDrafts() {
  try { return JSON.parse(localStorage.getItem(DRAFTS) || "{}"); } catch { return {}; }
}

function writeDrafts(drafts) {
  try { localStorage.setItem(DRAFTS, JSON.stringify(drafts)); } catch { /* a full disk is not a lost save */ }
}

function setBusy(host, text) {
  state.message = text;
  if (host) host.textContent = text;
}

function cards() {
  return [...document.querySelectorAll(".hybrid-card")];
}

function readCounts() {
  const counts = { saved: 0, notes: 0, rejected: 0 };
  for (const card of cards()) {
    const decision = card.dataset.decision;
    if (decision && decision in counts) counts[decision] += 1;
  }
  return counts;
}

function paintCounts() {
  const host = document.getElementById("hybrids-counts");
  if (!host) return;
  const counts = readCounts();
  host.textContent = `${cards().length} candidates · ${counts.saved} saved · ` +
    `${counts.notes} moved to notes · ${counts.rejected} rejected`;
}

function mark(card, decision) {
  card.dataset.decision = decision;
  paintCounts();
}

function paintStars(card, importance) {
  card.dataset.importance = String(importance || 0);
  card.querySelectorAll(".stars button").forEach((button) => {
    button.classList.toggle("on", Number(button.dataset.imp) <= (importance || 0));
  });
  paintCounts();
}

async function save(card, patch) {
  if (!state.readOk) throw new Error("decisions have not loaded; refusing to write");
  const payload = {
    name: card.dataset.name,
    decision: card.dataset.decision || "",
    importance: Number(card.dataset.importance) || 0,
    curveName: card.querySelector(".hybrid-name")?.value.trim() || "",
    ...patch,
    crossedAt: new Date().toISOString(),
  };
  const response = await fetch(ENDPOINT, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ curves: [payload] }),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error || `save failed: ${response.status}`);
  }
}

async function load() {
  const response = await fetch(ENDPOINT);
  if (!response.ok) throw new Error(`load failed: ${response.status}`);
  const { curves } = await response.json();
  state.readOk = true;
  for (const row of curves) {
    const card = document.querySelector(`.hybrid-card[data-name="${row.name}"]`);
    if (!card) continue;
    if (row.decision) mark(card, row.decision);
    if (row.importance) paintStars(card, row.importance);
    const input = card.querySelector(".hybrid-name");
    if (input && row.curveName) input.value = row.curveName;
    const drafts = readDrafts();
    const draft = drafts[card.dataset.name];
    if (input && draft && draft.value && draft.value !== (row.curveName || "")) {
      input.value = draft.value;
      const flag = card.querySelector(".hybrid-flag");
      if (flag) flag.textContent = "draft, not saved";
    }
  }
  paintCounts();
}

export function mountHybridDesk() {
  for (const card of cards()) {
    const input = card.querySelector(".hybrid-name");
    if (input) {
      input.dataset.saved = input.value;
      input.addEventListener("input", () => {
        const drafts = readDrafts();
        const flag = card.querySelector(".hybrid-flag");
        if (input.value.trim() === (input.dataset.saved || "")) {
          delete drafts[card.dataset.name];
          if (flag) flag.textContent = "";
        } else {
          drafts[card.dataset.name] = { value: input.value, at: Date.now() };
          if (flag) flag.textContent = "draft, not saved";
        }
        writeDrafts(drafts);
      });
      input.addEventListener("change", async () => {
        const previous = input.dataset.saved || "";
        const flag = card.querySelector(".hybrid-flag");
        try {
          await save(card, { curveName: input.value.trim() });
          input.dataset.saved = input.value.trim();
          const drafts = readDrafts();
          delete drafts[card.dataset.name];
          writeDrafts(drafts);
          if (flag) flag.textContent = "saved";
        } catch (error) {
          input.value = previous;
          if (flag) flag.textContent = `not saved — ${String(error.message || error)}`;
          const host = document.getElementById("hybrids-counts");
          if (host) host.textContent = String(error.message || error);
        }
      });
    }
    card.querySelectorAll(".stars button").forEach((button) => {
      button.addEventListener("click", async () => {
        const importance = Number(button.dataset.imp) || 0;
        const previous = Number(card.dataset.importance) || 0;
        paintStars(card, importance);
        try {
          await save(card, { importance });
        } catch (error) {
          paintStars(card, previous);
          const host = document.getElementById("hybrids-counts");
          if (host) host.textContent = String(error.message || error);
        }
      });
    });
    for (const button of card.querySelectorAll("[data-decision]")) {
      button.addEventListener("click", async () => {
        const decision = button.dataset.decision;
        const previous = card.dataset.decision || "";
        try {
          await save(card, { decision });
          mark(card, decision);
        } catch (error) {
          mark(card, previous);
          const host = document.getElementById("hybrids-counts");
          if (host) host.textContent = String(error.message || error);
        }
      });
    }
  }
  load().catch((error) => {
    state.readOk = false;
    const host = document.getElementById("hybrids-counts");
    if (host) {
      host.textContent = `could not load decisions — saving is off until they load: ` +
        `${String(error.message || error)}`;
    }
  });
}

mountHybridDesk();
