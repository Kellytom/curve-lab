// One caption and one drawing per plate. The exporter and the Astro gallery
// both call this, so the caption the operator reads is written once.
//
// Loads through require from Node; the page never needs it in the browser.
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory(require("./plate_math.js"));
  } else {
    root.PlateCompose = factory(root.PlateMath);
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function (PlateMath) {
  "use strict";

  // A starred design carries the settings the lab had on screen. The curve row
  // is patched with them, so the plate is the star, not the saved default.
  function patchStar(plate, rows) {
    const patched = { ...rows };
    const patch = (name) => {
      if (!name || !rows[name]) return;
      patched[name] = {
        ...rows[name],
        width: { percent: plate.width ?? (rows[name].width || {}).percent ?? 1.5 },
        character: {
          plus: plate.plus ?? (rows[name].character || {}).plus ?? 2,
          minus: plate.minus ?? (rows[name].character || {}).minus ?? 2,
          profile: plate.profile ?? (rows[name].character || {}).profile ?? "bow",
        },
      };
    };
    patch(plate.curve);
    patch(plate.curveB);
    return patched;
  }

  function composePlate(plate, rows) {
    if (plate.kind === "star") {
      const patched = patchStar(plate, rows);
      if (plate.form === "single") {
        const group = PlateMath.group(patched[plate.curve]);
        return { paths: group.paths, bbox: PlateMath.bbox(group.paths.flat()),
                 note: `${group.note} · starred` };
      }
      const data = PlateMath.design({
        form: plate.form, curve: plate.curve, curveB: plate.curveB,
        leg: plate.leg, pattern: plate.pattern, alternate: plate.alternate,
        frame: plate.frame ? { perWidth: plate.perWidth, perHeight: plate.perHeight } : null,
      }, patched);
      return { paths: data.paths, bbox: data.bbox, note: `${data.note} · starred` };
    }
    if (plate.kind === "design") {
      const data = PlateMath.design(plate, rows);
      const symmetry = rows[plate.curve] && rows[plate.curve].symmetry;
      return { paths: data.paths, bbox: data.bbox,
               note: data.note + (symmetry ? ` · curve ${symmetry.kind}` : "") };
    }
    const group = PlateMath.group(rows[plate.name]);
    const symmetry = rows[plate.name] && rows[plate.name].symmetry;
    return { paths: group.paths, bbox: PlateMath.bbox(group.paths.flat()),
             note: group.note + (symmetry ? ` · ${symmetry.kind}` : "") };
  }

  return { composePlate };
});
