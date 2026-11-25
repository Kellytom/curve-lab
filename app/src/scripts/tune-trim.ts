// The door from a curve's tuning page to its trim page, carrying the values on screen.
//
// The operator, 2026-11-24: "connect /tune/ to the trim function, eg /tune/c-0022 could be
// trimmed". The trim page defaults to the record's own side values; this keeps the link true when
// the sliders have been moved but not yet saved, so the cut is made with the band being looked at.
const link = document.getElementById("tune-trim") as HTMLAnchorElement | null;
const form = document.getElementById("tune-form") as HTMLFormElement | null;

if (link && form) {
  const sync = (): void => {
    const data = new FormData(form);
    const params = new URLSearchParams();
    for (const key of ["widthPct", "plus", "minus", "profile"]) {
      const value = data.get(key);
      if (value !== null) params.set(key, String(value));
    }
    link.href = `/trim/${link.dataset.uid}?${params.toString()}`;
  };
  for (const event of ["input", "change"]) form.addEventListener(event, sync);
  sync();
}
