"""SVG writing: absolute cubic paths, millimetre units, no surprises.

Rules that make the file open cleanly in Inkscape and stay node-editable:

- Absolute commands only, one `M` and then `C` triples. No relative arithmetic.
- Numbers are fixed-point at a stated precision, never exponent notation. SVG's
  path grammar is stricter than Python's float formatting, and `1e-05` in a `d`
  attribute is exactly the kind of thing that opens fine in one tool and not
  the next.
- One user unit is one millimetre. The document carries width and height in mm
  and a viewBox in the same numbers, so Inkscape's node readout is in mm and no
  transform is needed.
- The design JSON rides along in `<metadata>`, so a round trip has something to
  come back to.

Path data lives in a plain string. A path library is not needed to write `M`
and `C`, and adding one would be a dependency earning nothing.
"""

from __future__ import annotations

import json
import math


def num(value: float, prec: int = 4) -> str:
    """Fixed-point, trailing zeros trimmed, no exponent, no negative zero."""
    if not math.isfinite(value):
        raise ValueError(f"non-finite coordinate: {value}")
    q = round(value, prec)
    if q == 0:
        return "0"
    text = f"{q:.{prec}f}".rstrip("0").rstrip(".")
    return text if text not in ("", "-0") else "0"


def path_d(spans: list[dict], prec: int = 4, close: bool = False) -> str:
    """Absolute `M` then `C` for every span, as one path string."""
    if not spans:
        raise ValueError("no spans to write")
    first = spans[0]["p0"]
    parts = [f"M {num(first[0], prec)},{num(first[1], prec)}"]
    for span in spans:
        parts.append(
            "C {} {}, {} {}, {} {}".format(
                num(span["c1"][0], prec), num(span["c1"][1], prec),
                num(span["c2"][0], prec), num(span["c2"][1], prec),
                num(span["p3"][0], prec), num(span["p3"][1], prec),
            )
        )
    if close:
        parts.append("Z")
    return " ".join(parts)


SODIPODI = "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
INKSCAPE = "http://www.inkscape.org/namespaces/inkscape"


def read_view(path) -> str | None:
    """The Inkscape view element from an existing file, if it has one.

    Zoom, pan, document units and the current layer live in `sodipodi:namedview`,
    which Inkscape writes when it saves. Our rebuilds replace the drawing, so
    without this the view would be thrown away every time and the document would
    re-fit itself on load. Carrying it over is what makes the zoom stay put.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError:
        return None
    start = text.find("<sodipodi:namedview")
    if start < 0:
        return None
    close = text.find("</sodipodi:namedview>", start)
    if close >= 0:
        return text[start:close + len("</sodipodi:namedview>")]
    self_closing = text.find("/>", start)
    if self_closing >= 0:
        return text[start:self_closing + 2]
    return None


def _bbox(spans: list[dict]) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []
    for span in spans:
        for px, py in (span["p0"], span["c1"], span["c2"], span["p3"]):
            xs.append(px)
            ys.append(py)
    return min(xs), min(ys), max(xs), max(ys)


def document(design, chain, spine: list[dict], rails: list[dict],
             prec: int = 4, margin: float = 5.0, stroke: float | None = None,
             page: tuple[float, float] | None = None,
             view: str | None = None) -> str:
    """One SVG: the spine, one path per rail, mm units, JSON in the metadata."""
    groups = [("spine", spine, None)]
    for rail in rails:
        groups.append((f"rail {num(rail['distance'], 3)}", rail["spans"], rail["distance"]))

    all_spans = [s for _, spans, _ in groups for s in spans]
    x0, y0, x1, y1 = _bbox(all_spans)
    content_w, content_h = x1 - x0, y1 - y0

    # A fixed page is what keeps a reload from jumping. When the page is derived
    # from the drawing, every parameter change resizes the document and the
    # viewer re-fits, so the zoom moves under the hand. With a stated page the
    # viewBox is constant and the drawing moves inside it instead.
    if page is not None:
        width, height = float(page[0]), float(page[1])
        if width <= content_w or height <= content_h:
            raise ValueError(
                f"page {width:g}x{height:g} mm is smaller than the drawing "
                f"({content_w:.1f}x{content_h:.1f} mm)"
            )
        ox = x0 - (width - content_w) / 2.0
        oy = y0 - (height - content_h) / 2.0
    else:
        width = content_w + 2 * margin
        height = content_h + 2 * margin
        ox, oy = x0 - margin, y0 - margin

    def shift(spans):
        def move(p):
            return (p[0] - ox, p[1] - oy)
        out = []
        for span in spans:
            out.append({**span, "p0": move(span["p0"]), "c1": move(span["c1"]),
                        "c2": move(span["c2"]), "p3": move(span["p3"])})
        return out

    stroke = design.stroke if stroke is None else stroke
    width_mm, height_mm = num(width, prec), num(height, prec)
    ns = (f'     xmlns:sodipodi="{SODIPODI}"\n'
          f'     xmlns:inkscape="{INKSCAPE}"\n') if view else ""
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg"',
        ns + '     version="1.1"',
        f'     width="{width_mm}mm" height="{height_mm}mm"',
        f'     viewBox="0 0 {width_mm} {height_mm}">',
    ]
    if view:
        out.append("  " + view.strip())
    out += [
        f"  <title>{_escape(design.name)}</title>",
        f'  <desc id="clothoid-lab-design">{_escape(design.to_json())}</desc>',
        '  <g id="clothoid" fill="none" stroke="#000000" stroke-linecap="round"',
        f'     stroke-width="{num(stroke, prec)}">',
    ]
    for index, (name, spans, _) in enumerate(groups):
        gid = "spine" if index == 0 else f"rail-{index}"
        out.append(f'    <path id="{gid}" d="{path_d(shift(spans), prec)}"/>')
    out.append("  </g>")
    out.append("</svg>")
    return "\n".join(out) + "\n"


def _slug(name: str) -> str:
    return "".join(ch if ch.isalnum() else "-" for ch in name).strip("-")


def _escape(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace('"', "&quot;"))


def write(path, text: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def parse_d(d: str) -> list[tuple[str, list[float]]]:
    """A small reader for our own path data, for the round-trip tests.

    Not a general SVG parser: it reads `M`, `C`, `L` and `Z` with absolute
    coordinates, which is what this writer emits.
    """
    tokens = d.replace(",", " ").split()
    out: list[tuple[str, list[float]]] = []
    i = 0
    while i < len(tokens):
        cmd = tokens[i]
        if cmd in ("M", "C", "L"):
            n = {"M": 2, "L": 2, "C": 6}[cmd]
            vals = [float(tokens[i + 1 + j]) for j in range(n)]
            out.append((cmd, vals))
            i += 1 + n
        elif cmd == "Z":
            out.append(("Z", []))
            i += 1
        else:
            raise ValueError(f"unsupported path token: {cmd}")
    return out


def metadata_design(svg_text: str) -> dict:
    """Recover the design JSON from a file this writer produced."""
    marker = '<desc id="clothoid-lab-design">'
    start = svg_text.find(marker)
    end = svg_text.find("</desc>", start)
    if start < 0 or end < 0:
        raise ValueError("no design metadata in this file")
    raw = svg_text[start + len(marker):end]
    raw = (raw.replace("&quot;", '"').replace("&lt;", "<")
              .replace("&gt;", ">").replace("&amp;", "&"))
    return json.loads(raw)
