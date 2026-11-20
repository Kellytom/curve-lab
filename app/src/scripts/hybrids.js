// The hybrid desk's browser side: decisions, stars and names, saved through desk-io.
//
// Rules that matter here, and are checked in app/scripts/check-hybrids-page.mjs:
//   * a failed read is never a write (state.readOk);
//   * a save says so, with the time;
//   * a name being typed is a draft that survives a refresh;
//   * a duplicate name is refused by the endpoint and the card shows why.

import { readDecisions, saveDecision } from "../lib/desk-io.js";

const state = { readOk: false };
const DRAFTS = "hybrid-name-drafts";

function cards() {
  return [...document.querySelectorAll(".hybrid-card")];
}

function readDrafts() {
  try { return JSON.parse(localStorage.getItem(DRAFTS) || "{}"); } catch { return {}; }
}

function writeDrafts(drafts) {
  try { localStorage.setItem(DRAFTS, JSON.stringify(drafts)); } catch { /* a full disk is not a lost save */ }
}

function say(text) {
  const host = document.getElementById("hybrids-counts");
  if (host) host.textContent = text;
}

function paintCounts() {
  const counts = { saved: 0, notes: 0, rejected: 0 };
  for (const card of cards()) {
    const decision = card.dataset.decision;
    if (decision && decision in counts) counts[decision] += 1;
  }
  const host = document.getElementById("hybrids-counts");
  if (host) {
    host.textContent = `${cards().length} candidates · ${counts.saved} saved · ` +
      `${counts.notes} moved to notes · ${counts.rejected} rejected`;
  }
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
}

function stamp(text, when) {
  const time = when ? new Date(when).toLocaleString([], { day: "numeric", month: "short",
    hour: "2-digit", minute: "2-digit" }) : "";
  return time ? `${text} ${time}` : text;
}

function flag(card, text) {
  const node = card.querySelector(".hybrid-flag");
  if (node) node.textContent = text;
}

const TURNS = {
  0: { matrix: [[1, 0], [0, 1]], exact: true },
  45: { matrix: [["√2/2", "-√2/2"], ["√2/2", "√2/2"]], exact: false },
  "-45": { matrix: [["√2/2", "√2/2"], ["-√2/2", "√2/2"]], exact: false },
  90: { matrix: [[0, -1], [1, 0]], exact: true },
  "-90": { matrix: [[0, 1], [-1, 0]], exact: true },
};

function paintTurn(card, degrees) {
  const value = String(degrees || 0);
  const group = card.querySelector(".rotate");
  if (group) group.dataset.degrees = value;
  const img = card.querySelector("img");
  if (img) img.style.transform = `rotate(${value}deg)`;
  if (group) {
    group.querySelectorAll("button").forEach((button) =>
      button.classList.toggle("on", button.dataset.turn === value));
  }
}

async function save(card, patch) {
  if (!state.readOk) throw new Error("decisions have not loaded; refusing to write");
  const input = card.querySelector(".hybrid-name");
  const payload = {
    name: card.dataset.name,
    decision: card.dataset.decision || "",
    importance: Number(card.dataset.importance) || 0,
    curveName: input ? input.value.trim() : "",
    construction: (() => {
      try { return JSON.parse(card.dataset.construction || "{}"); } catch { return {}; }
    })(),
    ...patch,
    crossedAt: new Date().toISOString(),
  };
  await saveDecision(payload);
  return payload;
}

async function load() {
  const rows = await readDecisions();
  state.readOk = true;
  const drafts = readDrafts();

  for (const row of rows) {
    const card = document.querySelector(`.hybrid-card[data-name="${row.name}"]`);
    if (!card) continue;
    if (row.decision) {
      mark(card, row.decision);
      flag(card, stamp(
        row.decision === "saved" ? "saved" : row.decision === "notes" ? "moved to notes" : "rejected",
        row.crossedAt || row.savedAt));
    }
    if (row.importance) paintStars(card, row.importance);
    const degrees = row.transform && row.transform.degrees;
    if (degrees !== undefined && degrees !== null) paintTurn(card, degrees);
    const input = card.querySelector(".hybrid-name");
    if (input && row.curveName) { input.value = row.curveName; input.dataset.saved = row.curveName; }
  }

  for (const card of cards()) {
    const draft = drafts[card.dataset.name];
    const input = card.querySelector(".hybrid-name");
    if (!input || !draft || !draft.value) continue;
    if (draft.value !== (input.dataset.saved || "")) {
      input.value = draft.value;
      flag(card, "draft, not saved");
    }
  }
  paintCounts();
}

export function mountHybridDesk() {
  for (const card of cards()) {
    const input = card.querySelector(".hybrid-name");
    if (input) {
      input.dataset.saved = input.dataset.saved || input.value;
      input.addEventListener("input", () => {
        const drafts = readDrafts();
        if (input.value.trim() === (input.dataset.saved || "")) {
          delete drafts[card.dataset.name];
          flag(card, "");
        } else {
          drafts[card.dataset.name] = { value: input.value, at: Date.now() };
          flag(card, "draft, not saved");
        }
        writeDrafts(drafts);
      });
      input.addEventListener("change", async () => {
        const previous = input.dataset.saved || "";
        try {
          await save(card, { curveName: input.value.trim() });
          input.dataset.saved = input.value.trim();
          const drafts = readDrafts();
          delete drafts[card.dataset.name];
          writeDrafts(drafts);
          flag(card, stamp("saved"));
        } catch (error) {
          input.value = previous;
          flag(card, `not saved — ${String(error.message || error)}`);
        }
      });
    }

    const mirror = card.querySelector(".mirror-make");
    if (mirror) {
      mirror.addEventListener("click", async () => {
        mirror.disabled = true;
        try {
          const response = await fetch("/api/mirror-double", {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ parent: card.dataset.name }),
          });
          const body = await response.json();
          if (!response.ok) throw new Error(body.error || "could not mirror");
          location.reload();
        } catch (error) {
          mirror.disabled = false;
          flag(card, `not mirrored — ${String(error.message || error)}`);
        }
      });
    }

    card.querySelectorAll(".rotate button").forEach((button) => {
      button.addEventListener("click", async () => {
        const degrees = button.dataset.turn;
        const previous = card.querySelector(".rotate")?.dataset.degrees || "0";
        paintTurn(card, degrees === "0" ? 0 : degrees);
        try {
          const turn = TURNS[degrees] || TURNS[0];
          await save(card, { transform: { degrees: Number(degrees), ...turn } });
        } catch (error) {
          paintTurn(card, previous);
          say(String(error.message || error));
        }
      });
    });

    card.querySelectorAll(".stars button").forEach((button) => {
      button.addEventListener("click", async () => {
        const importance = Number(button.dataset.imp) || 0;
        const previous = Number(card.dataset.importance) || 0;
        paintStars(card, importance);
        try {
          await save(card, { importance });
        } catch (error) {
          paintStars(card, previous);
          say(String(error.message || error));
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
          flag(card, stamp(decision === "saved" ? "saved"
            : decision === "notes" ? "moved to notes" : "rejected"));
        } catch (error) {
          mark(card, previous);
          flag(card, `not saved — ${String(error.message || error)}`);
        }
      });
    }
  }

  load().catch((error) => {
    state.readOk = false;
    say(`could not load decisions — saving is off until they load: ${String(error.message || error)}`);
  });
}

mountHybridDesk();
