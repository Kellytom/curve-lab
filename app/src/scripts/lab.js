
const $ = (id) => document.getElementById(id);
const stage = $("sf-stage");
const readout = $("sf-readout");
const params = new URLSearchParams(location.search);
const STAR_KEY = "square-lab-stars";
let rows = null;

function readStars() {
  try { return JSON.parse(localStorage.getItem(STAR_KEY) || "[]"); }
  catch { return []; }
}
function writeStars(stars) {
  localStorage.setItem(STAR_KEY, JSON.stringify(stars));
  renderStars();
}
function currentSpec() {
  const aName = $("sf-a").value;
  const choice = $("sf-b").value;
  const bName = choice === "none" ? null : choice === "same" ? aName : choice;
  let form = $("sf-form").value;
  if (form === "leaf" && !bName) form = "single";
  const natural = $("sf-natural").checked;
  return {
    descriptor: `${aName}-${form}`,
    form, curve: aName, curveB: bName,
    perWidth: Number($("sf-per-w").value), perHeight: Number($("sf-per-h").value),
    pattern: $("sf-pattern").value,
    leg: natural ? null : Number($("sf-leg").value),
    frame: $("sf-frame").checked && form !== "single",
    alternate: $("sf-alternate").checked,
    width: Number($("sf-width").value), plus: Number($("sf-plus").value),
    minus: Number($("sf-minus").value), profile: $("sf-profile").value,
  };
}
function starDesign() {
  const stars = readStars();
  const max = stars.reduce((m, star) => Math.max(m, Number(star.serial) || 0), 300);
  const spec = currentSpec();
  spec.serial = max + 1;
  stars.push(spec);
  writeStars(stars);
}
function renderStars() {
  const stars = readStars();
  $("sf-stars").innerHTML = stars.length
    ? stars.map((star, index) => `<div class="star-row"><span>${star.descriptor} · `
      + `${String(star.serial).padStart(4, "0")}</span>`
      + `<button type="button" data-index="${index}">remove</button></div>`).join("")
    : `<p class="empty">no stars yet</p>`;
}
function gallerySvg(name) {
  let group;
  try { group = PlateMath.group(rows[name]); } catch { return ""; }
  const paths = group.paths;
  const box = PlateMath.bbox(paths.flat());
  const w = 160, h = 110, margin = 8;
  const [x0, y0, x1, y1] = box;
  const k = Math.min((w - 2 * margin) / (x1 - x0), (h - 2 * margin) / (y1 - y0));
  const ox = (w - (x1 - x0) * k) / 2 - x0 * k;
  const oy = (h - (y1 - y0) * k) / 2 - y0 * k;
  const to = ([x, y]) => [ox + x * k, h - (oy + y * k)];
  const lines = paths.map((path) => {
    const text = path.map((p) => to(p).map((v) => v.toFixed(1)).join(",")).join(" ");
    return `<polyline points="${text}" fill="none" stroke="#2e2413" stroke-width="1.2" `
      + `stroke-linecap="round" stroke-linejoin="round"/>`;
  }).join("");
  return `<svg viewBox="0 0 ${w} ${h}" aria-hidden="true">`
    + `<rect width="${w}" height="${h}" fill="#ffffff"/>${lines}</svg>`;
}

function renderGallery() {
  const names = Object.keys(rows).sort();
  $("sf-gallery").innerHTML = names.map((name) => {
    const category = rows[name].category
      || (rows[name].symmetry && rows[name].symmetry.symmetric ? "symmetric" : "asymmetric");
    return `<button type="button" class="curve-card" data-name="${name}">`
      + gallerySvg(name) + `<span>${name}<br><i>${category}</i></span></button>`;
  }).join("");
}

function starredRows() {
  return readStars().map((star) => {
    const { serial, ...rest } = star;
    return { ...rest, variant: 1, kind: "star", serial,
             id: `${star.descriptor}-1-t-exp-c-${String(serial).padStart(4, "0")}` };
  });
}

function downloadStars() {
  const blob = new Blob(
    [JSON.stringify({ format: "starred/1", plates: starredRows() }, null, 1)],
    { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "starred.json";
  link.click();
  URL.revokeObjectURL(link.href);
}

async function saveToWorkbench() {
  const status = $("sf-save-status");
  status.textContent = "saving…";
  try {
    const response = await fetch("/api/stars", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ format: "starred/1", plates: starredRows() }),
    });
    const out = await response.json();
    status.textContent = response.ok
      ? `saved ${out.saved} star(s) to workbench/starred.json`
      : `save failed: ${out.error}`;
  } catch (error) {
    status.textContent = `save failed: ${error}`;
  }
}

function show(id, value) {
  const el = $(id + "-v");
  if (el) el.textContent = value;
}

function loadCharacter(name) {
  const row = rows[name];
  if (!row) return;
  const width = (row.width && row.width.percent) || 1.5;
  const character = row.character || {};
  $("sf-width").value = width;
  $("sf-plus").value = character.plus ?? 2;
  $("sf-minus").value = character.minus ?? 2;
  $("sf-profile").value = ["bow", "s", "taper"].includes(character.profile)
    ? character.profile : "bow";
}

function start() {
  const curveData = JSON.parse(document.getElementById("curve-data").textContent);
  rows = Object.fromEntries(curveData.curves.map((row) => [row.name, row]));
  const names = Object.keys(rows).sort();
  const groups = { symmetric: [], asymmetric: [] };
  names.forEach((name) => {
    const category = rows[name].category
      || (rows[name].symmetry && rows[name].symmetry.symmetric ? "symmetric" : "asymmetric");
    groups[category].push(name);
  });
  ["sf-a", "sf-b"].forEach((id) => {
    const extra = id === "sf-b" ? ["none", "same"] : [];
    const grouped = ["symmetric", "asymmetric"].map((label) =>
      `<optgroup label="${label}">`
      + groups[label].map((name) => `<option>${name}</option>`).join("")
      + "</optgroup>").join("");
    $(id).innerHTML = extra.map((name) => `<option>${name}</option>`).join("") + grouped;
  });
  $("sf-a").value = "u-bowl";
  $("sf-b").value = "none";
  $("sf-form").value = "single";
  $("sf-natural").checked = true;
  loadCharacter($("sf-a").value);
  if (params.has("width")) $("sf-width").value = params.get("width");
  renderStars();
  renderGallery();
  draw();
}

function draw() {
  if (!rows) return;
  const aName = $("sf-a").value;
  const bChoice = $("sf-b").value;
  const bName = bChoice === "none" ? null : bChoice === "same" ? aName : bChoice;
  let form = $("sf-form").value;
  let fallback = "";
  if (form === "leaf" && !bName) {
    form = "single";
    fallback = " · curve b none, drawn single";
  }
  const perW = Number($("sf-per-w").value);
  const perH = Number($("sf-per-h").value);
  const pattern = $("sf-pattern").value;
  const natural = $("sf-natural").checked;
  const leg = natural ? null : Number($("sf-leg").value);
  const sizeIn = Number($("sf-size").value);
  const fill = Number($("sf-fill").value);
  const alternate = $("sf-alternate").checked;
  const showFrame = $("sf-frame").checked;
  const width = Number($("sf-width").value);
  const plus = Number($("sf-plus").value);
  const minus = Number($("sf-minus").value);
  const profile = $("sf-profile").value;

  show("sf-per-w", perW);
  show("sf-per-h", perH);
  show("sf-leg", natural ? "natural" : leg + "°");
  show("sf-size", sizeIn.toFixed(2) + " in");
  show("sf-fill", Math.round(fill * 100) + "%");
  show("sf-width", width.toFixed(1) + "%");
  show("sf-plus", plus.toFixed(1) + " / " + minus.toFixed(1));

  const patch = (name) => ({ ...rows[name], width: { percent: width },
    character: { plus, minus, profile } });
  const patched = { ...rows, [aName]: patch(aName) };
  if (bName) patched[bName] = patch(bName);

  let data;
  try {
    if (form === "single") {
      const group = PlateMath.group(patched[aName]);
      data = { paths: group.paths, bbox: PlateMath.bbox(group.paths.flat()), note: group.note };
    } else {
      data = PlateMath.design({
        form, curve: aName, curveB: bName || undefined, leg,
        frame: showFrame ? { perWidth: perW, perHeight: perH } : null,
        pattern, alternate,
      }, patched);
    }
  } catch (error) {
    stage.innerHTML = "";
    readout.textContent = String(error);
    return;
  }

  const W = sizeIn * 72;
  const H = W;
  const margin = W * 0.06;
  const [x0, y0, x1, y1] = data.bbox;
  const k = Math.min((W - 2 * margin) / (x1 - x0), (H - 2 * margin) / (y1 - y0)) * fill;
  const ox = (W - (x1 - x0) * k) / 2 - x0 * k;
  const oy = (H - (y1 - y0) * k) / 2 - y0 * k;
  const toSvg = ([x, y]) => [ox + x * k, H - (oy + y * k)];
  const stroke = PlateMath.strokeFor(W);

  stage.setAttribute("viewBox", `0 0 ${W} ${H}`);
  stage.setAttribute("width", W);
  stage.setAttribute("height", H);
  stage.innerHTML = data.paths.map((path) => {
    const text = path.map((p) => toSvg(p).map((v) => v.toFixed(2)).join(",")).join(" ");
    return `<polyline points="${text}" fill="none" stroke="#2e2413" `
      + `stroke-width="${stroke.toFixed(2)}" stroke-linecap="round" `
      + `stroke-linejoin="round"/>`;
  }).join("");

  readout.textContent =
    `${((x1 - x0) * k / 72).toFixed(2)} × ${((y1 - y0) * k / 72).toFixed(2)} in · `
    + `${data.paths.length} paths · stroke ${stroke.toFixed(2)} pt · ${data.note}`
    + ` · curve a ${rows[aName].category || "?"}`
    + ` (${rows[aName].symmetry ? rows[aName].symmetry.kind : "?"})`
    + fallback;
}

["sf-per-w", "sf-per-h", "sf-pattern", "sf-leg", "sf-natural", "sf-size",
 "sf-fill", "sf-alternate", "sf-frame", "sf-width", "sf-plus", "sf-minus",
 "sf-profile"].forEach((id) => $(id).addEventListener("input", draw));
$("sf-a").addEventListener("input", () => { loadCharacter($("sf-a").value); draw(); });
$("sf-b").addEventListener("input", draw);
$("sf-gallery").addEventListener("click", (event) => {
  const card = event.target.closest(".curve-card");
  if (!card) return;
  $("sf-a").value = card.dataset.name;
  loadCharacter($("sf-a").value);
  draw();
});
$("sf-star").addEventListener("click", starDesign);
$("sf-save").addEventListener("click", saveToWorkbench);
$("sf-download").addEventListener("click", downloadStars);
$("sf-stars").addEventListener("click", (event) => {
  const index = event.target.dataset.index;
  if (index === undefined) return;
  const stars = readStars();
  stars.splice(Number(index), 1);
  writeStars(stars);
});
start();
