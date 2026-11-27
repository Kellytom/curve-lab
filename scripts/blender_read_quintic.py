"""Runs INSIDE Blender: build the exported NURBS span and report its vertices.

Called by `scripts/check_blender_quintic.py`; not run by hand except for
debugging.

    blender -b -P scripts/blender_read_quintic.py -- /tmp/points.json 60

The point of it: the extension claims that "six points + order_u = 6 +
use_endpoint_u" is one exact degree-5 Bézier span. This is Blender's own
evaluation of that claim, with no code of ours in the loop except the control
points.
"""

import json
import sys

import bpy

arguments = sys.argv[sys.argv.index("--") + 1:]
points_path = arguments[0]
resolution = int(arguments[1]) if len(arguments) > 1 else 60

data = json.load(open(points_path))
points = data["points"]

# a clean scene: nothing from a previous run can contribute vertices
bpy.ops.wm.read_factory_settings(use_empty=True)

curve = bpy.data.curves.new("quintic", "CURVE")
curve.dimensions = "2D"
spline = curve.splines.new("NURBS")
spline.points.add(len(points) - 1)
for vertex, coordinate in zip(spline.points, points):
    vertex.co = (coordinate[0], coordinate[1], 0.0, 1.0)
spline.order_u = 6
spline.use_endpoint_u = True
spline.resolution_u = resolution
obj = bpy.data.objects.new("quintic", curve)
bpy.context.collection.objects.link(obj)

mesh = obj.to_mesh()
vertices = [[round(v.co.x, 9), round(v.co.y, 9)] for v in mesh.vertices]
print("QUINTIC_VERTICES " + json.dumps({
    "count": len(vertices),
    "resolution": resolution,
    "vertices": vertices,
}))
obj.to_mesh_clear()
