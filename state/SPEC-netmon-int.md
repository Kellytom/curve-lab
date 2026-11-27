# SPEC-netmon-int — the internet monitor

**The operator's ask, 2026-11-27:** "i need a program that is always on to monitor the
internet", "it should be not handrolled, able to measure when speeds go down from 40 mb
to 6", and "can you run networkquality all the time and log it and keep an eye for when
opencode drops?"

**What it is for.** One question, answered with two logs: when OpenCode drops, did the
link lose capacity (Wi-Fi, repeater, extender), or did the link keep its speed and the name
look-up / provider fail above it? Those are different faults and they need different fixes.

## Where things live

| Path | What it is |
|---|---|
| `scripts/netmon/daemon.ts` | the always-on process: probe every 10 s, speed test on a timer |
| `scripts/netmon/probe.ts` | resolve the host, open TCP 443 |
| `scripts/netmon/speed.ts` | run `/usr/bin/networkQuality -s -c` and read its JSON |
| `scripts/netmon/link.ts` | `airport -I`: SSID, channel, RSSI, noise, rate |
| `scripts/netmon/analysis.ts` | drop pairing, statistics, durations (pure) |
| `scripts/netmon/report.ts` | the plain-text report |
| `scripts/netmon/sample.ts` | one speed test, by hand |
| `scripts/netmon/install.ts` | install or remove the LaunchAgent |
| `~/.local/share/netmon/*.jsonl` | the logs — outside the repo, because it is public |
| `local.netmon` | the LaunchAgent label; KeepAlive, runs at login |
| `tests/js/netmon.test.ts` | parsers and roll-ups, no network |

## The words it owns

- **probe** — one DNS look-up plus one TCP connection to port 443. It sends no request.
- **drop** — probes failing from one success to the next; it has a start and an end.
- **speed sample** — one complete `networkQuality` run: downlink, uplink, responsiveness.
- **network change** — the SSID or the channel changed between two probes. On a mesh or
  extender network this is the Mac moving to another access point.
- **capacity** — Mbit/s, the number the operator means by "40 mb" and "6".

## Rules, each with a check that can fail

1. **The speed number is Apple's, not ours.** Only `runNetworkQuality` writes a speed
   sample; nothing computes capacity from byte counts or ping times. Check: `grep -n
   "networkQuality" scripts/netmon/*.ts` finds one runner, and the speed log is written in
   one place.
2. **Units are stated and tested.** `dl_throughput` is bits per second; Mbps = ÷1e6.
   Measured 2026-11-27: a run read 24,853,812 and moved 42.15 MB in 17.5 s = 2.41 MB/s
   averaged over the whole run, so a 24.85 Mbit/s (3.11 MB/s) peak fits and an
   eight-times-larger bytes reading does not. (The first reading summed three `en0` rows
   in `netstat -ib`, which carry the same counters.) Check: `tests/js/netmon.test.ts`
   ("1,000,000 bits per second is 1 Mbit/s").
3. **A drop is DNS or TCP, and it is paired.** `pairDrops` closes each start with the next
   end; an unclosed drop shows as ongoing. Check: the unit test with an out-of-order start
   and an open drop.
4. **Every sample carries the link.** SSID, channel, RSSI and noise are read beside every
   probe and every speed test, so the report can group by network and channel. Check: the
   "By network and channel" table; a sample with no link prints `? · ch —`.
5. **A drop gets a speed test 15 s in, and only one test runs at a time.** A single failed
   look-up is not proof; the 15 s wait filters a blip. Check: `speedRunning` guard and the
   `reason: "drop"` row in the speed log.
6. **Logs never enter git, and they are pruned.** The default directory is
   `~/.local/share/netmon`; rows older than 30 days are dropped once a day. Check:
   `git check-ignore` finds nothing under the repo; `NETMON_KEEP_DAYS` changes the age.
7. **One daemon only.** A second instance finds a live pid and exits. Check: start the
   daemon twice by hand; the second prints nothing and exits 0.
8. **Plain English and named units.** The report says "Mbit/s", "dBm", "s / min", and it
   never prints a bare number without one. Check: read one report.
9. **Sampling is configurable, and the defaults are stated.** 10 s probe; Apple's test at
   start-up (unless a sample is newer than the baseline interval), every 6 h, and 15 s into
   a drop (at most once per 10 min). Each run measured 580 MB on 2026-11-27 (151 MB down,
   430 MB up at 36/155 Mbit/s), so an hourly timer would be tens of gigabytes a day;
   `NETMON_SPEED_MS` changes the baseline and `scripts/netmon/sample.ts` takes one reading
   by hand.
10. **It starts at login and comes back if it dies.** Check: `launchctl list | grep
    local.netmon` shows a pid, and killing it brings a new pid within a few seconds.

## Not this

No dashboard, no web page, no Homebrew install, no sudo, no packet capture, and no
per-packet claims. A probe time is not a bandwidth measurement; the two are logged
separately and the report keeps them apart.

## Inherited from the last page's spec

New code is TypeScript; generated output and personal data stay out of git; a rule that
cannot fail a command is a wish, so every rule above names its check.
