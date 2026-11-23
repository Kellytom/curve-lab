# Open faults and undecided questions

This is where your criticism earns its keep. Each item is written as the fault, what is known,
and the decision it waits on.

## Drawing

1. **G3 joins are not built.** A cubic has 8 numbers; matching position, direction, curvature and
   its rate at both ends is 10 conditions. The glue sandbox is G1 and exact there. The next step
   is a quintic connector, and it needs each curve's curvature and curvature rate at its leg —
   data the records do not carry today. *Question: is G3 worth the extra data, or is G1 enough?*
2. **The multi-branch curves still break.** `c-0416` (cruciform) and `c-0418` (absx-gerono) draw
   as fragments. Branches are now stored separately (`record.branches`) and the plate writer
   prefers them, but these two still show gaps. *Fault, not a decision.*
3. **A cusp's outside rail is rounded, not offset.** A true offset of a cusp is discontinuous;
   the plate rounds the spike so the band does not shoot out. That is a drawing choice and the
   spec says so. *Question: is a rounded cusp acceptable on a plate, or must it be cut?*

## Data

4. **158 stored paths have no exact measurement.** The crossing × inflection grid counts only the
   262 measured curves, so some "empty" cells may be occupied. *Question: is a sampled count
   (labelled approximate) better than no count?*
5. **The 13 absent uids** in `c-0338`–`c-0364` do not exist. They are either renumbered or
   were never made. *Decision needed: renumber, or leave the gap.*
6. **The turn lives in two places** (registry and database note) and drifted by 45° for days.
   They are synced by a script, not by construction. *Question: should the note be derived
   from the registry, so drift is impossible?*

## Art

7. **The human figure** is the biggest open problem: a human form at the centre of the design
   (the Virgin, Christ, or the two hearts). The hearts sandbox exists; nothing is stored.
   *Decision: which emblem, at what size, and where in the composition.*
8. **The plates carry working marks** — red cut points, blue start, orange end, blue cusp dots.
   They are for judgement, not for print. *Decision: when do the marks come off?*

## Process

9. **The launch agent loops** every ten seconds on Node 22 and fails; it no longer reloads pages
   (the ornament writer is idempotent) but it snapshots the database each time. *A one-line plist
   fix, outside the repository.*
10. **The `workhorse` queue** has no scheduler; the operator must start it in a third terminal.
    *Question: should it be a LaunchAgent, and if so, who owns the lock?*
