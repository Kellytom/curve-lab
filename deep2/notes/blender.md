blender
Blender 4.2.23 LTS, Intel build installed at /Applications/Blender.app (885 MB).
Headless launch: exit code 0, printed 4.2.23 LTS.
Workbench render succeeded: 320×240 PNG written with no error.
Quarantine flag removed, so it opens without right-click.
The gap: I ran it headless, so I have not confirmed the GUI opens its window on the Iris 550. That needs a real display, and I do not launch apps for you. If it fails, the message will name Metal or a GPU backend — send it to me.
Known limits, all irrelevant to 2D curves:
EEVEE hung in my headless test. Unverified in the GUI; if it stalls, use Workbench.
Cycles is CPU-only here, two cores, so slow.
8 GB RAM caps scene size, not curve editing.
Version situation, checked against Blender's server: 5.0 ships no Intel macOS build, 4.5 LTS and 4.2 LTS both do. You are on 4.2 LTS, which is the right one to stay on.
So: Finder → Applications → Blender, double-click. If the window appears, the question is answered, and the answer is yes.
/Applications/Blender.app

***

There is no native SVG export in Blender 4.2 — the add-on you are thinking of only imports. Evidence from your own install:
addons_core/io_curve_svg/
  __init__.py   →  "name": "Scalable Vector Graphics (SVG) 1.1 format"
                   "description": "Import SVG as curves"
  import_svg.py
  svg_util.py
  svg_colors.py
No export_svg.py anywhere in the bundle. The only two things that write SVG are io_mesh_uv_layout/export_uv_svg.py (UV layouts, not curves) and the Freestyle line renderer, which is not even shipped in 4.2's add-on folder on this install.
So the answer to "what about it" has two parts.
Practical: you can import SVG into Blender as curves and you cannot get curves back out as SVG. The route out is a mesh export (OBJ/GLTF) or a PNG render.
Fundamental, and this is the one that matters for quintics: SVG has no degree-5 path primitive. An SVG path offers M, L, C (cubic), Q (quadratic), A (arc). A quintic must therefore be either sampled into a polyline or approximated by cubic spans. Even a perfect exporter cannot hand you back six exact control points — it has nowhere to put them.
That means for curve-lab the exactness lives in the six numbers, not in the file: the six control points are the record, and any SVG is the drawing. Which is the rule already in the project: stations exact, drawing approximate.
If you want an export, the honest options are:
1. Sample it — convert to mesh, write the vertices as an SVG M/L polyline. Exact at the sample points, no curvature between them.
2. Fit cubics — approximate the quintic with the fewest cubic spans within a stated tolerance. This is the same G3 question the project already asks, and it needs a tolerance number before it means anything.
3. Skip Blender for output — keep the six exact points in the project's own format and draw the SVG from them with Inkscape or the existing curve-lab painter.
I can write a 30-line Blender script for option 1 or 2 if you want to see the actual deviation numbers, but I would want the tolerance first.
/Applications/Blender.app/Contents/Resources/4.2/scripts/addons_core/io_curve_svg/init.py

