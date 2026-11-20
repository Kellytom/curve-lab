// The hybrid desk's one rule: a decision is a save, and a save never touches another
// candidate's row. Each candidate is its own name in /api/sandbox-curves.
//
// Spec: state/SPEC-hybrids-int.md. Check: app/scripts/check-hybrids-page.mjs.

const ENDPOINT = "/api/sandbox-curves";

function cards() {
  return [...document.querySelectorAll(".hybrid-card")];
}

function readCounts() {
  const counts = { keep: 0, later: 0, reject: 0 };
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
  host.textContent = `${cards().length} candidates · ${counts.keep} kept · ` +
    `${counts.later} later · ${counts.reject} rejected`;
}

function mark(card, decision) {
  card.dataset.decision = decision;
  paintCounts();
}

async function save(card, decision) {
  const payload = {
    name: card.dataset.name,
    decision,
    crossedAt: new Date().toISOString(),
  };
  const response = await fetch(ENDPOINT, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ curves: [payload] }),
  });
  if (!response.ok) throw new Error(`save failed: ${response.status}`);
}

async function load() {
  const response = await fetch(ENDPOINT);
  if (!response.ok) throw new Error(`load failed: ${response.status}`);
  const { curves } = await response.json();
  for (const row of curves) {
    const card = document.querySelector(`.hybrid-card[data-name="${row.name}"]`);
    if (card && row.decision) mark(card, row.decision);
  }
  paintCounts();
}

export function mountHybridDesk() {
  for (const card of cards()) {
    for (const button of card.querySelectorAll("[data-decision]")) {
      button.addEventListener("click", async () => {
        const decision = button.dataset.decision;
        try {
          await save(card, decision);
          mark(card, decision);
        } catch (error) {
          const host = document.getElementById("hybrids-counts");
          if (host) host.textContent = String(error.message || error);
        }
      });
    }
  }
  load().catch((error) => {
    const host = document.getElementById("hybrids-counts");
    if (host) host.textContent = `could not load decisions: ${String(error.message || error)}`;
  });
}

mountHybridDesk();
