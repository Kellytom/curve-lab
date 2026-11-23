# The code that matters, and where it is

Short excerpts with exact file and line numbers; read the file around them.
The house rules are in `AGENTS.md` and `senior-dev.md`; the map in `LTMemory-int.md`.

### Which side of a turn folds — the plate's inside/outside rule

`workbench/plate_math.js:140-162`

```js
  function curvatureWorstSide(u, v, side, strength, profileName, samples = 400) {
    const u2 = multiply(u, u), v2 = multiply(v, v), uv = multiply(u, v);
    const x1 = add(u2, scalePoly(v2, -1));
    const y1 = scalePoly(uv, 2);
    const x2 = scalePoly(add(multiply(u, derivative(u)), scalePoly(multiply(v, derivative(v)), -1)), 2);
    const y2 = scalePoly(add(multiply(derivative(u), v), multiply(u, derivative(v))), 2);
    const clamped = Math.max(-0.95, Math.min(4, Number(strength) || 0));
    let worst = 0;
    for (let i = 0; i <= samples; i += 1) {
      const t = i / samples;
      const a = value(x1, t), b = value(y1, t);
      const speed = Math.hypot(a, b);
      if (speed < 1e-12) return Infinity;
      const cross = a * value(y2, t) - b * value(x2, t);
      if (Math.sign(cross) !== side) continue;
      const curvature = Math.abs(cross) / speed ** 3;
      const factor = Math.abs(1 + clamped * profileAt(profileName, t));
      worst = Math.max(worst, curvature * factor);
    }
    return worst;
  }

  function integrate(start, u, v, steps, eps = 0, bump = null) {
```

### Rounding a rail's cusp spike

`workbench/plate_math.js:337-357`

```js
  function roundSpikes(rail, limit = 100) {
    const out = rail.map((p) => [p[0], p[1]]);
    const turnAt = (pts, i) => {
      const a = pts[i - 1], b = pts[i], c = pts[i + 1];
      const v1x = b[0] - a[0], v1y = b[1] - a[1];
      const v2x = c[0] - b[0], v2y = c[1] - b[1];
      const l1 = Math.hypot(v1x, v1y) || 1, l2 = Math.hypot(v2x, v2y) || 1;
      const dot = (v1x * v2x + v1y * v2y) / (l1 * l2);
      return (Math.acos(Math.max(-1, Math.min(1, dot))) * 180) / Math.PI;
    };
    for (let pass = 0; pass < 4; pass += 1) {
      for (let i = 1; i < out.length - 1; i += 1) {
        if (turnAt(out, i) > limit) {
          out[i] = [(out[i - 1][0] + out[i + 1][0]) / 2, (out[i - 1][1] + out[i + 1][1]) / 2];
        }
      }
    }
    return out;
  }

  const rotate = (points, deg) => {
```

### The glue connector: a cubic whose ends lie on typed slopes

`app/src/lib/glue.js:51-70`

```js
export function controls(p0, p3, slope0, slope1, h0, h1) {
  const d0 = direction(slope0);
  const d1 = direction(slope1);
  if (!d0 || !d1) return null;
  const chord = Math.hypot(p3.x - p0.x, p3.y - p0.y);
  // a handle may be given as a fraction (exact) or a plain number
  const size = (value) => (value && typeof value === "object" ? fracValue(value) : Number(value));
  const H0 = chord * size(h0);
  const H1 = chord * size(h1);
  const u0 = unitDirection(slope0);
  const u1 = unitDirection(slope1);
  return [
    p0,
    { x: p0.x + H0 * u0.x, y: p0.y + H0 * u0.y },
    { x: p3.x - H1 * u1.x, y: p3.y - H1 * u1.y },
    p3,
  ];
}

// the derivative of a cubic at t (Bezier), for checking the ends
```

### Class V: the arch as one stroke

`app/src/lib/class-v.js:59-65`

```js
export function archPath(built) {
  if (!built) return [];
  // both halves run foot -> apex; the arch is the left half, then the right half reversed
  return [...built.left, ...built.right.slice().reverse().slice(1)];
}

// side curves for a sampled outline, the plate's law: outside at the ask, inside capped at
```

### The plate preset: a measured gap, not a fixed width

`scripts/lib/plate-row.mjs:28-49`

```js
export function presetWidthPercent(character) {
  const strength = (Math.abs(Number(character.plus) || 0) + Math.abs(Number(character.minus) || 0)) / 2;
  return Math.round((TARGET_GAP_PERCENT / medianFactor(character.profile, strength)) * 100) / 100;
}

// The operator, 2026-11-21: "the offset curves should look the same on both sides of the
// curve, not thin on the right and wide on the left." The two sides take one strength, the
// average of the saved pair; the profile is zero at both ends, so the start and end gaps are
// the base and the ends balance.
export const symmetricStrength = (plus, minus) =>
  (Math.abs(Number(plus) || 0) + Math.abs(Number(minus) || 0)) / 2;

// A zero in a note is the placeholder the 2026-11 note migration wrote, not a choice: every
// plate then drew a 0 % parallel band. The note wins only when it holds a real value; a zero
// falls through to the desk row, then the default. A deliberate zero belongs in the desk row.
const choose = (noteValue, deskValue, defaultValue) => {
  if (noteValue !== undefined && noteValue !== null && Number(noteValue) !== 0) return noteValue;
  if (deskValue !== undefined && deskValue !== null) return deskValue;
  return defaultValue;
};

export function rowFor(record, context = {}) {
```

### The workhorse queue: one runner, a lock, one log per job

`scripts/jobq.py:80-119`

```js
def run(once=False, quiet=False):
    DIR.mkdir(parents=True, exist_ok=True)
    with open(LOCK, "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("another runner holds the queue")
            return 1
        while True:
            data = load()
            job = next((j for j in data["jobs"] if j["status"] == "queued"), None)
            if job is None:
                if not quiet:
                    print("nothing queued")
                return 0
            job["status"] = "running"
            job["started"] = now()
            save(data)
            started = time.time()
            if not quiet:
                print(f"running {job['id']}  {job['name']}")
            log = ROOT / job["log"]
            log.parent.mkdir(parents=True, exist_ok=True)
            with open(log, "w") as out:
                out.write(f"# {job['id']} {job['name']}\n# {job['command']}\n# from {job['cwd']}\n\n")
                out.flush()
                code = subprocess.call(job["command"], shell=True, cwd=job["cwd"],
                                       stdout=out, stderr=subprocess.STDOUT)
            job["seconds"] = time.time() - started
            job["finished"] = now()
            job["status"] = "done" if code == 0 else f"failed ({code})"
            save(data)
            if not quiet:
                print(f"{job['status']}  {job['id']}  {job['seconds']:.1f}s  "
                      f"log {job['log']}")
            if once:
                return 0 if code == 0 else 1


def main():
```
