# Next action

Take the 40 sample curves in `workbench/septic-samples.json` (gallery D) and
promote the interesting ones: add each to `scripts/septic_curves.py` as a named
curve with its eight-speed recipe, regenerate, and check the JSON against the
metrics. `lazy-s-2` is the model of what "interesting" means: small integers,
pitch under a few hundred, inflection inside (0, 1), closest above 0.1.

Then check `gh run list -L 1` - the last push (84ff0b7) was still running at
handoff.
