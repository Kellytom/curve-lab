# senior-dev.md — how to work in this repository

Read this on every focus command. It is short on purpose: these are the rules
that cost the operator real time when they were learned the hard way, not a
process to satisfy.

1. **Verify where the operator looks.** A fresh browser and a fresh build prove
   the source; the operator's own browser and the page they have open prove the
   product. When they differ, the difference is the bug. Ask which page, or copy
   their profile and look.
2. **The page is the evidence.** A control that is correct in `scripts/` and
   stale in the browser reads as broken. After touching shared JavaScript, run
   `scripts/build-pages.py` and look at the page.
3. **Check the whole suite, and read the word "FAILED".** A truncated log hides
   a red test. Grep for `FAILED`, or read the summary; never report green from
   `tail -4`.
4. **One number, one definition.** Grid is grid. A crossing count is *crossing
   pairs*, not places. If two things share a name (`cone` is a width law and a
   construction), name them apart in the same breath.
5. **A failed read is never a write.** Damaged storage is repaired from a backup,
   not replaced by an empty list. Keep the last value before every write. This
   rule exists because it cost the operator a saved-curve list twice.
6. **Do not rewrite data silently.** When records are wrong, fix them with a
   script that reports the change, keep the file's formatting, and say how many
   lines moved. A 9,000-line diff for 100 numbers is a mistake.
7. **Derive expectations from data; assert structure, not wording.** Tests that
   quote a heading break when the heading improves. Find the section by its id.
8. **Commit the action when its `Proves:` line is true.** Do not stop short and do
   not keep going past it: the next step is the next row of the plan, a new
   commit. Tag a page that works (`page-works-…`) so a bad next step is one
   command away from undone.
9. **Never start a feature on a red tree.** Repair, commit, then build.
10. **A blocked decision is written down, not guessed.** Put it in `TODO.md` with
    the options and the reason it is blocked; do not quietly pick one.
11. **The operator's latest words override the older design note.** Write the
    change down in `state/DESIGN-int.md` in the same commit, so the next session
    does not re-open it.
12. **Say what you are doing and what it costs.** One line at a time, plain
    English, numbers with their units. A long silent tool chain reads as a freeze.

What is *not* here: ceremony. No gate for its own sake, no test that exists to
look thorough. If a rule above makes the work slower without catching a fault
this project has actually had, delete it and say why.
