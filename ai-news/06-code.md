# The code that matters, and where it is

Short excerpts with exact file and line numbers; read the file around them.
The house rules are in `AGENTS.md` and `senior-dev.md`; the map in `LTMemory-int.md`.

### Which side of a turn folds — the plate's inside/outside rule

(file moved: `workbench/plate_math.js`)

### Rounding a rail's cusp spike

(file moved: `workbench/plate_math.js`)

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

`app/src/lib/class-v.js:119-125`

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

`scripts/jobq.py:80-125`

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
            # the operator is often away: a job that lands must be heard, not just written
            try:
                subprocess.Popen([str(Path.home() / "bin" / "ding"), f"{job['name']}: {job['status']}"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except OSError:
                pass
            if once:
                return 0 if code == 0 else 1


def main():
```
