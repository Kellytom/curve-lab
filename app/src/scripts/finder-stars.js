// The finder's stars: one list in this browser, saved to the server after a
// click, and painted back onto the cards.
//
// It lived inline in finder.astro. The reference to `title` outside its scope
// threw on every click, so a star was never added and never saved — a bug no
// test could see while the code sat in a page. The keying rule is
// `dedupeStars`, which has its own test.
import { dedupeStars } from "../lib/star-list.ts";

const KEY = "finder-stars";
let lastError = "";
const removedStars = new Set();
const nameToId = JSON.parse(document.getElementById("finder-name-to-id").textContent || "{}");
const specs = JSON.parse(document.getElementById("finder-specs").textContent || "{}");

const migrate = (list) => list.map((star) => {
  if (star.id || !star.name) return star;
  const id = nameToId[star.name];
  return id ? { ...star, id } : star;
});

const read = () => {
  try {
    // Seed from the file once, then this browser is the editor. Merging the
    // file into every read made a star impossible to remove: the file put it
    // back. One star per curve: the same curve starred under an old name and a
    // new one is collapsed on read, and the cleaned list is written back.
    const raw = localStorage.getItem(KEY);
    if (raw !== null) {
      const value = JSON.parse(raw);
      const stored = Array.isArray(value) ? value : [];
      const out = dedupeStars(migrate(stored), nameToId);
      if (out.length !== stored.length) localStorage.setItem(KEY, JSON.stringify(out));
      return out;
    }
    const seed = JSON.parse(document.getElementById("finder-stars-seed").textContent || "[]");
    const out = dedupeStars(migrate(seed), nameToId);
    localStorage.setItem(KEY, JSON.stringify(out));
    return out;
  } catch { return []; }
};
const write = (list) => localStorage.setItem(KEY, JSON.stringify(list));

const chosen = () => {
  const list = read();
  return {
    ids: new Set(list.map((star) => star.id).filter(Boolean)),
    names: new Set(list.map((star) => star.name).filter(Boolean)),
  };
};

const paint = () => {
  const pick = chosen();
  document.querySelectorAll("button.star").forEach((button) => {
    const card = button.closest(".card");
    const title = (button.parentElement.textContent || "").replace("★", "").replace("☆", "").trim();
    const on = pick.ids.has(button.dataset.id) || pick.names.has(title);
    button.textContent = on ? "★" : "☆";
    // A starred card rises to the Starred grid; an unstarred one goes home.
    // Without the second half a removed star stayed at the top of the page.
    const home = card?.dataset.home && document.getElementById(card.dataset.home);
    if (on) {
      const grid = document.getElementById("starred-grid");
      if (card && grid && card.parentElement !== grid) grid.appendChild(card);
    } else if (card && home && card.parentElement !== home) {
      home.appendChild(card);
    }
  });
  const count = document.querySelectorAll("#starred-grid article.card").length;
  const lead = document.getElementById("star-count");
  if (lead) lead.textContent = ` ${count}`;
  const status = document.getElementById("star-status");
  if (status) status.textContent = lastError;
  const empty = document.getElementById("starred-empty");
  if (empty) empty.style.display = count ? "none" : "";
};

document.querySelectorAll("button.star").forEach((button) => {
  button.addEventListener("click", () => {
    const list = read();
    const id = button.dataset.id;
    const at = list.findIndex((star) => star.id === id);
    if (at >= 0) {
      // The server keys by name, so a removal has to name the star it drops.
      const [gone] = list.splice(at, 1);
      if (gone?.name) removedStars.add(gone.name);
    } else {
      const spec = specs[id] || {};
      list.push({ id, ...spec });
      // A pending removal of this name is cancelled: it was just starred again.
      if (spec.name) removedStars.delete(spec.name);
    }
    write(list);
    paint();
  });
});

// The server keys a star by its name: a name is what survives a rename, and
// the export file the sandbox reads carries names only. A star that has an id
// but no name gets the name from this page's own table before it is sent, so
// the body can never be refused for a missing name.
const forSave = () => read().map((star) => {
  const name = star.name || specs[star.id]?.name;
  if (!name) return null;
  const { id: _id, ...rest } = star;
  return { ...rest, name };
}).filter(Boolean);

const rescue = () => {
  try {
    localStorage.setItem("finder-stars-rescue",
      JSON.stringify({ at: new Date().toISOString(), curves: read() }));
  } catch { /* storage may be full */ }
};

const post = async () => {
  const status = document.getElementById("star-status");
  try {
    const response = await fetch("/api/finder-stars", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ format: "curve-lab.finder-stars/1", curves: forSave(),
                             removed: [...removedStars] }),
    });
    const out = await response.json();
    if (response.ok) {
      lastError = "";
      removedStars.clear();
      if (status) status.textContent = "";
      return;
    }
    lastError = `save failed: ${out.error} — the stars are kept in this browser`;
    rescue();
    status.textContent = lastError;
  } catch (error) {
    lastError = `save failed: ${error} — the stars are kept in this browser`;
    rescue();
    status.textContent = lastError;
  }
};

const save = document.getElementById("save-stars");
if (save) save.addEventListener("click", post);

// Always saved, quietly: the file is what the sandbox reads, and a star that
// only lives in this browser is a star the next step cannot see.
let timer = null;
document.querySelectorAll("button.star").forEach((button) => button.addEventListener("click", () => {
  clearTimeout(timer);
  timer = setTimeout(post, 400);
}));

const exportStars = document.getElementById("export-stars");
if (exportStars) exportStars.addEventListener("click", () => {
  const blob = new Blob([JSON.stringify({ format: "curve-lab.finder-stars/1", curves: forSave() }, null, 1)],
    { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "finder-stars.json";
  link.click();
});

// Every card remembers the grid it was built in, so paint() can send it back
// when its star is removed.
document.querySelectorAll("section .grid").forEach((grid) => {
  grid.querySelectorAll("article.card").forEach((card) => { card.dataset.home = grid.id; });
});

paint();
