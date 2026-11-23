// Draws the class V sandbox: the arch, the ghost Tschirnhausen, and the numbers.
import { arch, archPath, half, apexAngle, sizeOf, sides } from "../lib/class-v.js";

const el = (id) => document.getElementById(id);

function draw() {
  const host = el("v-preview");
  const readout = el("v-readout");
  const trim = Number(el("v-trim").value) / 100;
  const to = Number(el("v-to").value);
  const joinAt = el("v-join").value;
  el("v-trim-out").textContent = `${el("v-trim").value} %`;
  el("v-to-out").textContent = to.toFixed(1);

  const built = arch({ trim, to, joinAt });
  if (!built) {
    readout.textContent = "the trim leaves nothing to join";
    return;
  }
  const ghost = el("v-ghost").checked ? half({ from: -to, to, samples: 500 }) : [];
  const spine = archPath(built);
  const bandWidth = Number(el("v-band").value);
  const bandOn = el("v-bandon").checked;
  const band = bandOn ? sides(spine, bandWidth) : null;
  const pts = [...spine, ...(band ? [...band.left, ...band.right] : []), ...ghost];
  const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
  const x0 = Math.min(...xs), x1 = Math.max(...xs);
  const y0 = Math.min(...ys), y1 = Math.max(...ys);
  const w = 640, h = 460, margin = 30;
  const k = Math.min((w - 2 * margin) / (x1 - x0 || 1), (h - 2 * margin) / (y1 - y0 || 1));
  const ox = (w - (x1 - x0) * k) / 2, oy = (h - (y1 - y0) * k) / 2;
  const put = (p) => [ox + (p.x - x0) * k, h - (oy + (p.y - y0) * k)];
  const path = (line, colour, width, dash = "") => '<path d="M ' +
    line.map((p) => put(p).map((v) => v.toFixed(1)).join(" ")).join(" L ") +
    `" fill="none" stroke="${colour}" stroke-width="${width}"${dash ? ` stroke-dasharray="${dash}"` : ""} ` +
    'stroke-linecap="round" stroke-linejoin="round"/>';
  const apex = put(built.apex);
  host.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">
    <rect width="${w}" height="${h}" fill="#fff"/>
    ${ghost.length ? path(ghost, "#d8cbb2", 1.2, "5 5") : ""}
    ${band ? path(band.left, "#a06a2c", 1.2) + path(band.right, "#a06a2c", 1.2) : ""}
    ${band ? path([spine[0], band.left[0]], "#a06a2c", 1.2) + path([spine.at(-1), band.left.at(-1)], "#a06a2c", 1.2) : ""}
    ${band ? path([spine[0], band.right[0]], "#a06a2c", 1.2) + path([spine.at(-1), band.right.at(-1)], "#a06a2c", 1.2) : ""}
    ${path(built.left, "#2b2b2b", 2.4)}
    ${path(built.right, "#2b2b2b", 2.4)}
    <circle cx="${apex[0].toFixed(1)}" cy="${apex[1].toFixed(1)}" r="4" fill="#b03a2e"/>
    <text x="12" y="20" font-family="ui-monospace, Menlo, monospace" font-size="12" fill="#8a7a62">
      trim ${(trim * 100).toFixed(0)} % each end · length ${to.toFixed(1)} · joined ${joinAt === "tip" ? "at the tip" : "at the node"}</text>
    <text x="12" y="${h - 10}" font-family="ui-monospace, Menlo, monospace" font-size="12" fill="#5a4a36">
      apex ${apexAngle(built).toFixed(1)}° · width ${sizeOf(built).width.toFixed(2)} · height ${sizeOf(built).height.toFixed(2)}${bandOn ? ` · band ${bandWidth.toFixed(1)} %` : ""}</text>
  </svg>`;

  const a = apexAngle(built);
  const s = sizeOf(built);
  readout.innerHTML =
    `apex angle <b>${a.toFixed(1)}°</b> — 180° is a smooth join, 0° a cusp.<br>` +
    `width ${s.width.toFixed(3)} · height ${s.height.toFixed(3)} · ` +
    `feet at y ${s.foot.toFixed(3)}<br>` +
    (joinAt === "tip"
      ? "the tip is the apex, so the arch points up."
      : "the node is the apex, so the arch is round-headed — the same halves, the other way up.");
}

function mount() {
  for (const id of ["v-trim", "v-to", "v-join", "v-ghost", "v-band", "v-bandon"]) {
    el(id)?.addEventListener("input", draw);
    el(id)?.addEventListener("change", draw);
  }
  draw();
}

if (typeof document !== "undefined") {
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();
}
