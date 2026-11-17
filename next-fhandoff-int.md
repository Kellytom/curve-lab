```text
Read state/HANDOFF-int.md. Read docs/HANDOVER.md only for durable detail.
You are adding the two-arc cone terminal to curve_lab/terminals.py: one arc from each rail end, radius R = 2 x the offset, tangent to the rail at its base and meeting the other arc at the centreline tip, with both arc centres stated. The `cone` already there is a width law, so give this one its own name and say in the docstring that the two are different things.
Proves: tests/test_cone_terminal.py passes - tangency within 1e-9 at three offsets, R = 2 x offset on each, the arcs meet at the tip within 1e-9, and a bare tip is rejected; and a page draws the terminal with the radius and both arc centres labelled.
```

Source: state/HANDOFF-int.md, 2026-11-17, 4c22f4c.
