// The naming desk's page script: drafts in this browser, one Save per row.
//
// It lived inline in names.astro, where the type checker saw every element as
// a bare Element and the linter saw nothing at all. The rule it uses is
// `composeName`, which has its own test; this file is only reading the boxes
// and posting them.
import { composeName, draftState } from "../lib/name-parts.js";

const DRAFTS = "names-drafts";
const readDrafts = () => {
  try { return JSON.parse(localStorage.getItem(DRAFTS) || "{}"); } catch { return {}; }
};
const writeDrafts = (drafts) => localStorage.setItem(DRAFTS, JSON.stringify(drafts));

const drafts = readDrafts();
const compose = (row) => composeName({
  prefix: row.querySelector(".prefix").textContent,
  core: row.querySelector(".core").value,
  postfix: row.querySelector(".postfix").textContent,
});

document.querySelectorAll(".row").forEach((row) => {
  const uid = row.dataset.uid;
  const core = row.querySelector(".core");
  const preview = row.querySelector(".preview");
  const flag = row.querySelector(".flag");
  // `savedCore` is the middle of the name the record already has. A draft is an
  // edit away from it, not a copy of every box: a draft for a box nobody
  // touched made "unsaved" impossible to tell from "saved".
  let savedCore = core.value;
  // A draft carries the time it was typed; the row carries the time the record
  // was saved. A draft older than the save is not an edit any more — the
  // database is right, and the draft is what a stale tab would show. Dropping
  // it is how a saved name stops being hidden by yesterday's text.
  const draft = drafts[uid];
  const savedAt = Date.parse(row.dataset.updated || "") || 0;
  const { value: draftText, stale } = draftState(draft, savedAt);
  if (draftText !== undefined && !stale) {
    core.value = draftText;
    if (draftText !== savedCore) {
      flag.textContent = "draft, not saved";
      flag.className = "flag";
    }
  } else if (draftText !== undefined) {
    delete drafts[uid];
    writeDrafts(drafts);
  }

  const render = () => {
    const name = compose(row);
    preview.textContent = name ? `= ${name}` : "";
  };
  // Only typing writes a draft. Running the same code at load stamped old text
  // with a new time, which made every stale draft look like a fresh edit.
  core.addEventListener("input", () => {
    render();
    if (core.value === savedCore) {
      delete drafts[uid];
      flag.textContent = "";
    } else {
      drafts[uid] = { value: core.value, at: Date.now() };
      flag.textContent = "draft, not saved";
      flag.className = "flag";
    }
    writeDrafts(drafts);
  });
  render();

  row.querySelectorAll(".stars button").forEach((button) => {
    button.addEventListener("click", () => {
      row.dataset.imp = button.dataset.imp;
      row.querySelectorAll(".stars button").forEach((other) => other.classList.toggle("on", other === button));
    });
  });

  row.querySelector(".save").addEventListener("click", async () => {
    const name = compose(row);
    if (!name) {
      flag.textContent = "type a name first";
      flag.className = "flag bad";
      return;
    }
    const body = { curves: [{ uid, name, importance: Number(row.dataset.imp) || 0 }] };
    flag.textContent = "saving…";
    flag.className = "flag";
    try {
      const response = await fetch("/api/curve-notes", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(body),
      });
      const out = await response.json();
      if (!response.ok) throw new Error(out.error || "save failed");
      savedCore = core.value;
      const stamp = new Date().toISOString().slice(0, 16).replace("T", " ");
      const savedAtText = row.querySelector(".saved-at");
      if (savedAtText) savedAtText.textContent = ` · saved ${stamp}`;
      delete drafts[uid];
      writeDrafts(drafts);
      row.querySelector(".now").textContent = name;
      flag.textContent = "saved";
      flag.className = "flag";
    } catch (error) {
      flag.textContent = `not saved: ${error.message}`;
      flag.className = "flag bad";
    }
  });
});
