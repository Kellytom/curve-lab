# Hardware — the workstation build

The operator, 2026-11-25, in three messages:

> "google recommended a tower pc and stylus with display and a 5 ft cable with
> wireless keyboard. lenovo thinkstateion p340 MT build your own PC server and
> parts."

> (a cart from PC Server & Parts: ThinkStation P520 900 W, Xeon W-2245 $184.99,
> 8 GB 1× 8 GB DDR4 ECC RDIMM 2666 $59.99, empty tray $10.49, 512 GB M.2 $59.99,
> 1-year warranty, no OS — $500.44; plus a Dell Radeon Pro WX 3200 at $55.99)

> "use the internet if you wish, but most of all see if there are mistakes. the
> idea is a linux box that can run opencode, inkscape, and maybe in the future an
> llm with upgrades. fedora"

**The job, in one line:** Fedora on a desk machine that runs OpenCode and
Inkscape today, drives a pen display, and takes one large graphics card later
for local language models.

### The settled plan, 2026-11-25

The operator, 2026-11-25: "it sounds like the safest plan is to have a wired or
wireless keyboard and mouse, along with a basic screen just to see what is going
on. in that case, the tablet becomes a much simpler idea..."

Agreed, and it simplifies every section below.

| Role | Device | Cost |
|---|---|---|
| See POST, UEFI setup, installer, desktop | plain 22–24 in 1080p monitor, mini-DP → DisplayPort cable, or mini-DP → HDMI adapter | $50–80 used, $100 new |
| Type | wired keyboard, or a 2.4 GHz dongle set | $25 for a wired keyboard and mouse |
| Point | the mouse in that set | included |
| Draw | anything, because it no longer has to boot the machine | $25 screenless tablet, or a pen display later |

Because the **monitor** owns the boot, the pen display stops being a system
requirement and goes back to being an accessory. That removes every constraint
in §9: no HDMI-versus-USB-C trap, no "will it survive POST", no keyboard
dependency, no 13 in as the only screen.

The monitor is never wasted either: when a pen display does arrive, the monitor
becomes the second screen that §9 says you want anyway.

**A working machine is about $100–150**, and the drawing device can be chosen
later on price alone. §9 stays as the reference for the day the pen display does
have to be the primary screen.

### The monitor cable, named correctly

The card's four outputs are **mini DisplayPort**, not mini HDMI. Mini HDMI is a
different plug, the small one found on cameras; it does not exist on this card
and you should not buy for it.

| Monitor input | Buy | Cost | Risk |
|---|---|---|---|
| **DisplayPort** (best) | **mini-DP → DisplayPort cable**, 2–3 m, passive | $10–15 | none — the signal never changes form |
| HDMI | mini-DP → HDMI **active** adapter | $24–34 | low |
| HDMI, cheapest | mini-DP → HDMI passive | $12–15 | low at 1080p, because the card supports DP++ |
| DVI | mini-DP → DVI cable | $15–20 | fine |
| VGA | active converter | $20 | avoid: analogue, and another box |

So: if you are choosing the monitor anyway, **pick one with a DisplayPort
input** and use a single passive cable. It is the cheapest, the most reliable,
and there is no converter to fail at POST.

Touch is not needed at all: a wired mouse handles the pointer, and nothing in
Fedora, Inkscape or OpenCode needs a touchscreen.

Prices checked on the open web on **2026-11-25**: Intel ARK (W-2245),
Microsoft Learn (Windows 11 lists), PCSP product and search pages, Fedora
Project. All in **US dollars before sales tax**.

---

## 1. Mistakes in the audited cart

Ordered by what they cost you.

| # | Mistake | What it costs | Fix |
|---|---|---|---|
| 1 | **W-2245 at $184.99** for 8 cores | **$120 extra** for two cores you will not feel in Inkscape or OpenCode | Take the **W-2235, $64.99** on their own shelf: 6 cores, 3.80 GHz base, 4.60 boost, 130 W. Same single-thread feel, 25 W less |
| 2 | **8 GB in one stick** | a quarter of the memory speed, on a four-channel machine | **4× 8 GB, one per channel.** Not 1, not 2 |
| 3 | **512 GB used NVMe as the boot drive** | too small for Fedora + Inkscape + one 30B model (~20 GB), and a worn drive in the worst place | **1 TB, and the "New" option**, not the refurbished one |
| 4 | **The card is treated as optional** | with no card the machine has **no picture at all** — the W-2245 has no integrated graphics | The $55.99 WX 3200 is **mandatory** |
| 5 | **The WX 3200 has mini-DisplayPort only** | no way to plug an HDMI pen display | **active mini-DP → HDMI 2.0 adapter, $24–34** — take the active one, not the $12 passive |
| 6 | **The listing says "High-Profile" in the title and "Low Profile" in the body** | wrong bracket, card does not seat | Ask them to ship the **full-height bracket fitted** |
| 7 | **Fedora 43 from them** | Fedora 43 goes **end of life on 9 December 2026**; Fedora 45 shipped 3 November 2026 | Do not pay an install fee. **Install Fedora 45 yourself** |
| 8 | **No Bluetooth and no Wi-Fi card** | a Bluetooth keyboard will not connect | Buy a keyboard with its **own 2.4 GHz USB dongle** |
| 9 | **"x4x4x4x4 bifurcation"** | it is not a P520 feature I can find; it also is not needed | Ignore the RAID-0-across-slots plan. Do **not** buy the VROC key |
| 10 | **The CPU heatsink is not named** | a bare LGA2066 CPU is a stopper | Ask: "does $64.99 include the Lenovo heatsink fitted?" |

Two smaller ones:

- **Memory speed.** The W-2235 runs DDR4-2933. The cart's 2666 stick will run at
  2666, and mixing the two makes everything 2666. If you buy a kit, buy **2933**.
- **The empty tray at $10.49** is worth it: the Lenovo 3.5 in sled is a
  proprietary part and harder to find later than $10.

## 2. The corrected cart

| Line | Choice | ~$ |
|---|---|---|
| P520 900 W chassis, BYO 2nd Gen | chassis only | 184.98 |
| CPU | **Xeon W-2235** (6C, 3.80 GHz) | 64.99 |
| Memory from PCSP | 8 GB 1× 8 GB 2933, for burn-in and warranty | 59.99 |
| 3.5 in sled | empty tray | 10.49 |
| Boot drive | **1 TB New** M.2 NVMe (ask the price) | 110 |
| Card | Dell Radeon Pro WX 3200, VTR4J | 55.99 |
| **Machine total** | | **~$486** |
| Memory, added separately | 4× 8 GB DDR4-2933 ECC RDIMM, matched kit | 70 |
| Adapter | active mini-DP → HDMI 2.0 | 28 |
| **Ready to install Fedora** | | **~$584** |

That is **$15 less than the audited cart** and it has four times the memory and
twice the disk. The 8 GB stick becomes a spare, or stays in the second slot of
channel A (works, slightly unbalanced).

Their own RAM is expensive — their September guide prices 16 GB modules at
$107.99, so 32 GB from them would be about $216. A matched 4× 8 GB kit
elsewhere is about $70.

## 3. The honest ceiling on "an LLM later"

This is where the audit oversells the machine. From the P520 900 W page:

> "the 900W limit is one 295W card with a 75W card, or two 250W cards", with
> **two 6+2-pin graphics leads**.

So the future is bounded and it is easy to see:

| Plan | Reality |
|---|---|
| One 24 GB card (RTX 3090, 350 W) | **Just fits** if you cap it to ~290 W with `nvidia-smi -pl 290`. A 3090 needs two 8-pin plugs, which is exactly the two leads you have |
| One 24 GB card (RTX A5000, 230 W, one 8-pin) | **Fits comfortably.** The cleanest upgrade |
| One 48 GB card (RTX A6000, 300 W) | At the 295 W ceiling; two 8-pin; expensive |
| Two 24 GB cards | **No.** Two 3090s are 700 W of card and four 8-pin plugs |
| Two small cards (2× 3060 12 GB, 170 W each) | Fits, but 24 GB split over two cards with no NVLink is worse for models than one 24 GB card |

What one 24 GB card runs, in plain terms: a 70B model at 4-bit does not fit; a
32B at 4-bit does, at about 20 GB; 8B and 14B models run fast.

Two more limits to know:

- **PCIe 3.0, not 4.0.** Costs a few percent on model loading. Nothing for
  Inkscape.
- **Physical size.** Two dual-slot cards fit. A three-slot card (4090, 5090)
  does not. Measure the length before buying: about 12 in of room.

**Do not buy a GPU for the language model now.** PCSP's own September 2026 note
is that a new RTX 5090 was $4,999 in the US, roughly double a year earlier. Buy
the $55 card to drive the display, and revisit when the model is real.

## 4. Fedora, specifically

Fedora 45 is the current release (3 November 2026, support to December 2027).
Five setup facts for this box and this project:

1. **Node 24.** This repository needs Node 24 (its own `AGENTS.md` says so).
   Fedora ships an older Node. Install 24 from the NodeSource repository, or
   with `fnm`.
2. **Secure Boot: turn it off at install.** If you later add an NVIDIA card,
   the driver module has to be signed or Secure Boot disabled. Choosing "off"
   now saves a MOK enrolment later. The WX 3200 is AMD and needs nothing.
3. **The pen display must be Wacom on Linux.** Wacom tablets are handled by the
   in-kernel driver. XP-Pen and Huion depend on the community DIGImend driver,
   which breaks on kernel updates, and Fedora ships kernels fast.
4. **Python 3.15** ships with Fedora 45. This project is mostly standard
   library, so that is fine, but check any pip dependency in the virtualenv.
5. **Intel's end of servicing (30 June 2025) does not strand you.** Fedora
   carries the microcode in its own updates. That risk was a Windows risk.

## 5. Peripherals

| Item | Pick | ~$ |
|---|---|---|
| Pen display, 13 in, Linux | **Wacom One 13** (DTC133); check libwacom's device list for the exact model | 300 |
| Pen display, 16 in, Linux | **Wacom Cintiq 16** (DTK-1660) | 650 |
| Cable | 10 ft (3 m) HDMI + 10 ft USB-A extension, behind the mini-DP adapter | 25 |
| Keyboard | Logitech Pebble Keys 2 (**own dongle**), US ANSI | 40 |
| Keyboard, better | Logitech MX Keys S (Bolt receiver or Bluetooth) | 110 |

**5 ft (1.5 m) is too short** for a tower on the floor. That is the one number in
the original ask that is simply wrong for the job.

A 13 in screen is small for this work: the curve labels and the integer hit
points need room. The 16 in is the better desk if the budget allows.

## 6. What to put in the PCSP order comments

Short and specific, one box, no separate email:

> Please fit the full-height bracket to the WX 3200 (VTR4J) in Slot 4 and test
> video output on both the card and the onboard NIC during burn-in. Confirm the
> W-2235 arrives with the Lenovo LGA2066 heatsink fitted. Please use the 1 TB
> New M.2 as the boot drive and confirm the M.2 heatsink carrier is included.
> Enquire about Intel PTT (firmware TPM 2.0) being enabled in the BIOS.

Test it the day it lands: 90-day returns, but a **20% restocking fee** on
anything "ordered in error", and a dead-on-arrival unit should be their cost,
not yours.

## 7. Other boxes on the same shelf, for comparison

| Box | Price | Note |
|---|---|---|
| P520 690 W, BYO | from $159.98 | $25 cheaper chassis, but the GPU limit drops to 265 W per card. **Keep the 900 W** |
| P520 900 W, BYO | from $184.98 | the one in the cart |
| Dell Precision T5820, W-2155 10C, 32 GB, 2 TB, RTX 3080, Win 11 | $1,268.01 | a whole machine with a 10 GB card. More money, worse for models, fine for Inkscape |
| ThinkStation P340 Tower (30DK), i7-10700, refurb | ~$400 elsewhere | half the size and noise, one small card slot, no ECC |

The P520 is the right choice **only if the language model is a real plan**. For
OpenCode and Inkscape alone, the P340 is the better desk machine and the P520's
extra $150 buys a slot you may never fill.

## 8. The Surface Go idea: a remote terminal, not a pen display

The operator, 2026-11-25: "what if i used a refurbished surface go for display
and input by remote".

**It works, but it is a remote terminal, not a pen display.** Use it to run
OpenCode over SSH, or Inkscape over RDP for node editing and exact-coordinate
work. Do not plan to draw freehand on it through the wire.

### Why pen pressure does not cross the wire

- RDP does have a pen channel (RDPEI) that carries pressure and tilt.
- The **Linux servers do not implement it today**: neither `xrdp` nor GNOME
  Remote Desktop (which is what Fedora 45 uses) delivers RDPEI pen input to the
  host. The 2026 xrdp Wayland work uses libei, which does have a tablet
  capability, so this may change — but do not buy on that.
- So a remote session gives you an **absolute mouse pointer**. Inkscape's
  freehand tool then draws at one fixed width. Node editing, snapping to
  integer hits, and every exact-number operation in this project are unaffected.

Latency is the second issue: a LAN RDP session is roughly 30–60 ms, which is
noticeable while drawing and invisible while clicking.

### The USB-C port does not help

The Surface's single USB-C is an **output** port (DisplayPort alternate mode).
You cannot feed video *into* the tablet through it. Driving the Surface as a
second screen needs an HDMI capture dongle, and capture carries video only —
no pen back.

### If you buy one anyway

| Model | Reality |
|---|---|
| Surface Go 1 (4415Y) | the one to skip; outside Microsoft's Windows 11 processor list |
| **Surface Go 2 (4425Y or m3-8100Y)** | **Microsoft's own support page says it can be upgraded to Windows 11.** The m3 model is 8th-gen Core m, which is on the list |
| Surface Go 3 (6500Y or i3-10100Y) | ships with Windows 11; the latest of the three |

Three costs people forget: **the pen is usually not included** in a refurb
(budget $60–100), the **Type Cover is not included**, and the **4 GB / 64 GB
eMMC** model is the one that looks cheapest and is the one to avoid. Take
**8 GB and 128 GB SSD**.

On Linux the Surface's digitiser and cameras need the community
`linux-surface` kernel patches, which do cover Fedora. That is tolerable on a
client tablet and a nuisance on a working machine.

### What it actually costs, against the alternatives

| Plan | Cost | Drawing |
|---|---|---|
| Surface Go 2 or 3, refurb, 8 GB, plus pen | $210–360 | pointer only, 10.5 in |
| **24 in monitor + One by Wacom Small** | **~$150** | **real pressure, zero latency, Linux-native** |
| Wacom One 13 pen display | ~$300 | real pressure on the screen |
| Wacom Cintiq 16 | ~$650 | best of that kind |

### The cheapest pen tablet, and why it is still the right buy

The operator, 2026-11-25: "even if the curves dont draw well". Then the answer
is short, and it needs no compromise on brand: **a used One by Wacom Small,
model CTL-472, for $20–30.**

| Step | Cost | Note |
|---|---|---|
| Mouse and Inkscape's node tool | $0 | for pure coordinate work this is honestly equal |
| used Wacom Bamboo (CTL-470, CTH-470), 2010 | $12–20 | fine, but old micro-USB and often missing its pen |
| **used One by Wacom Small (CTL-472)** | **$20–30** | **the answer: pen included, no battery, plug and play** |
| new One by Wacom Small (CTL-472) | $40 | what the used one is a copy of |
| new One by Wacom Medium (CTL-672) | $60 | 216 × 135 mm instead of 152 × 95 mm |

Why the small one is enough **for this project specifically**: the pen is not
there to produce the curves. The curves come from exact numbers typed into the
tuner. The pen captures the **gesture** — the hand movement that a principle
card in `reference/principles.json` records as gesture, three numbers, and
not-this. A gesture is imprecise by nature, so a small cheap tablet loses
nothing that the work needs.

What you give up, plainly:

- **152 × 95 mm of active area.** Your hand travels 6 in for a 24 in screen, so
  long smooth strokes are hard and you will zoom a lot. This is the "curves
  draw badly" part, and it cannot be tuned away.
- **No express keys, no multi-touch, no tilt.** 2048 pressure levels only.
- **micro-USB.** It is the part that fails on used units.

Verified on 2026-11-25 from Wacom's own device table: the CTL-472 and CTL-672
have been in the Linux kernel since **4.16**, and in libwacom since **0.28**, so
Fedora 45 (kernel 7.2, libwacom 2.x) runs it with nothing installed. Wacom's
spec page confirms a battery-free pen (LP-190K), 2048 pressure levels, and no
ExpressKeys.

Two buying traps on a used one:

1. **Sold without the pen.** A replacement Wacom pen costs more than the
   tablet. The listing must say pen included.
2. **Worn nib.** Check the tip; a 5-pack of nibs is about $10.

On Fedora's Wayland session, map the tablet in **Settings → Wacom Tablet (or
Graphic Tablets)**, not with `xsetwacom`, which is X11 only.

So:

- **Want to draw curves properly, and the tower stays at the desk?** A 24 in
  monitor plus a One by Wacom Small, about **$150** all in.
- **Already accepted that the curves will not draw well?** Buy the $25 used
  CTL-472 and stop there. Nothing else in the chain gets cheaper without
  becoming junk.

**A screenless pen tablet is the cheapest thing that actually solves the
problem.** Wacom has in-kernel Linux support; pressure, tilt and absolute
mapping all work on Fedora with no driver. The pen display is the luxury; the
pen tablet is the tool.

So:

- **Want to draw curves properly, and the tower stays at the desk?** A 24 in
  monitor plus an Intuos S, about $210.
- **Want to draw on the screen?** Wacom One 13, about $300.
- **Want a portable terminal for the headless tower, and drawing is mostly
  clicking?** The Surface Go is genuinely good at that, and it kills the 5 ft
  cable problem completely. Just do not buy it expecting pressure.

## 9. A pen display as the only screen (the corrected ask)

The operator, 2026-11-25: "i made a mistake; i copied the screenless pen tablet
idea, but i meant with a screen so i can boot up linux, move the 'mouse' and
type text from the very beginning, and then use the fedora linux (or omarchy)
for inkscape etc."

That is a **pen display used as the primary screen**, not an accessory. Four
things must be true before price matters at all.

### Requirement 1: video in, on HDMI or DisplayPort

The firmware sees a pen display as a plain monitor, so POST, the UEFI setup and
the installer all appear on it with no driver. What matters is the **input
type**. This tower's card (Radeon Pro WX 3200) has **four mini-DisplayPort
outputs and no USB-C**. So:

- **Buy a display with HDMI or DisplayPort input.** ✓
- **Avoid USB-C-only displays.** They need the host to supply DisplayPort
  alternate mode over USB-C, which this card cannot do. A mini-DP→USB-C
  "sink" adapter exists and is the flakiest part of the chain.

### Requirement 2: its own power

A pen display with HDMI input also has a power brick, so it lights up at POST
without the operating system doing anything. Good.

### Requirement 3: the digitiser is in the kernel

Verified today against Wacom's own device table (every entry below is native, no
driver package):

| Model | Device | Linux since | libwacom | Input |
|---|---|---|---|---|
| **DTC133 — Wacom One Creative Pen Display (2019)** | 056a:03a6 | **4.10** | 1.3 | **HDMI + USB-A + power** |
| DTK-1300/1301 — Cintiq 13HD (2013) | 056a:0304 | 3.1 | 0.8 | proprietary 3-in-1 |
| DTK-1660 — Cintiq 16 | 056a:0390 | 4.10 | 0.33 | HDMI + USB-A + power |
| DTC121 — Wacom One 12 (2023) | 056a:03ce | 4.11 | 2.8 | USB-C |
| DTH134 — Wacom One 13 (2023) | 056a:03cb | 4.11 | 2.8 | USB-C |
| DTC141 — Wacom One 14 | 056a:040f | 4.11 | 2.17 | USB-C |
| DTK168 — Cintiq 16 (current) | 056a:03e6 | 5.19 | 2.16 | HDMI/DP |

Fedora 45 runs kernel 7.2 and libwacom 2.x, so **all of these work**. The
cheapest that also meets requirements 1 and 2 is the **DTC133**, the 2019
"Wacom One": about **$180 used, $280 new**.

**Naming trap:** two different products are both sold as "Wacom One 13". The
**DTC133** (2019) is HDMI; the **DTH134** (2023) is USB-C. For this tower you
want the **DTC133**.

### Requirement 4: a keyboard that works before any OS exists

**A pen display cannot type.** And a pen-only screen does not raise an
on-screen keyboard — GNOME shows that only when a touchscreen is present.

**Nor can there be one at POST, ever.** The pen display holds no computer: it is
a panel plus a digitiser. A keyboard on that screen would have to be drawn by the
operating system on the tower, and at POST no operating system is running — the
firmware is. The Lenovo UEFI has no virtual keyboard and accepts input only from
a real USB or PS/2 keyboard. There is no path by which a pen stroke becomes
`ESC` or `F1`. In the desktop you can force GNOME's screen keyboard on under
Accessibility, but it types characters, not function keys.

So:

- The wireless keyboard must be a **2.4 GHz USB dongle** type, or wired.
  Bluetooth-only keyboards (the Pebble Keys 2 K380s, for example) are dead at
  POST, because there is no Bluetooth stack yet.
- **Keep a $15 wired USB keyboard in the drawer.** It is the only thing
  guaranteed to work at POST, in the UEFI setup and inside the installer, and it
  saves you if the wireless battery dies mid-install.

At the UEFI setup a pen may work as a mouse, but do not plan on it: use the
keyboard there, as everyone does.

### The honest costs of using 13 in as the only screen

OpenCode in a terminal beside an Inkscape window on a 13.3 in 1080p screen is
cramped. Budget a **used 22–24 in 1080p monitor at $60–80** as a second screen,
and put the pen display beside it. Then the pen display is a drawing surface and
the monitor is where you read code.

| Plan | Cost | Boots Linux | Draws on screen |
|---|---|---|---|
| used 22 in monitor + One by Wacom Small | ~$130 | yes | no |
| **used Wacom One DTC133 (13 in)** | **~$180** | **yes, HDMI** | **yes** |
| Wacom One DTC133 new | ~$280 | yes | yes |
| used Cintiq 13HD DTK-1300 | $120–200 | yes | yes, but the **proprietary cable is often missing** and costs $50+ to replace |
| Cintiq 16 DTK-1660 | ~$600 | yes | yes, and a usable size |
| XP-Pen Artist 13 / Huion Kamvas 13 | $200–260 | yes (video) | yes, but the **pen** needs the community DIGImend driver — wrong choice for a primary screen |

### Fedora or Omarchy

- **Fedora 45 + GNOME**: the pen needs nothing installed, and Settings → Wacom
  Tablet gives the mapping. With one screen there is nothing to calibrate.
- **Omarchy** is Arch plus Hyprland, not Fedora. Newer kernel, but the tablet is
  configured in a text file rather than a settings panel, and a rolling release
  can break a working setup. Both boot to the pen display the same way.

For a machine whose job is Inkscape plus a coding agent, Fedora is the shorter
path. Omarchy is a choice about taste, not about hardware.

### Does the card need to change? No

The operator, 2026-11-25: "does this mean the video card or another card on the
box should change? that one was only 39$".

The WX 3200 stays. It has **four mini-DisplayPort 1.4 outputs** and draws **65 W
from the slot**, and that combination is better than it looks:

- one **active mini-DP → HDMI 2.0 adapter** drives the pen display;
- two or three outputs stay free for a second monitor;
- it uses **neither** of the two 6+2-pin graphics leads, so a future 24 GB card
  can have both;
- it is a single-slot card, so it does not block the second x16 slot.

That is the arrangement to want: the cheap card keeps the display, the expensive
card does the models. The display never eats model memory either.

Adapter prices, checked 2026-11-25: an **active** mini-DP → HDMI 2.0 unit is
**$24–34** (StarTech MDP2HD4K60S at $27.99 on CDW; 2M-MDP-HDMI2-4K60 at $24.16
on CompSource). A generic passive one is $12–15 and usually works at 1080p,
because the card supports DP++. **Buy the active one**: it is the single piece
that has to survive POST.

**On the $39 figure:** PCSP lists the Dell VTR4J at **$55.99**, down from
$67.19, 24 in stock. If $39 was seen, check the part number first. Three trap
cards sit in the same configurator and none of them will do:

- **AMD Radeon Pro WX 2100** — 2 GB, two outputs;
- **Quadro NVS 300 / NVS 295** — DMS-59 or dual DisplayPort, dead connectors;
- **"Generic 128MB Graphics Card"** — not a display solution.

Nothing else on the box needs a card. No network card (1 GbE onboard), no USB
card (four USB 3.2 Gen 1 front and rear), no Bluetooth (the keyboard's dongle
covers it). The one $15 accessory worth having is a **powered USB 2.0 hub** if
the pen display's USB cable must run far: the digitiser is a slow USB device and
long passive runs drop it.

**Test POST on the pen display before you install anything.** A bad adapter
fails exactly like a dead machine. Have the old monitor or a TV to hand for the
first boot.

To be honest about the odds: **this should just work.** A Radeon Pro WX 3200
driving a 1920 × 1080 HDMI panel through a branded active adapter is an ordinary
supported configuration, and a pen display is a plain monitor to the firmware.
The check is insurance against an awkward failure, not a prediction of one. It
is worth five minutes because the failure is silent and expensive to diagnose,
not because it is likely.

## 10. What a systems engineer uses for displays

The operator, 2026-11-25: "so what do systems engineers use for displays?
assuming it is displayport wired".

Two different answers, for two different machines.

**Servers: no display at all.** A rack server has no desk. It exposes **VGA**
from its baseboard management controller (iDRAC, iLO, IPMI) and you reach it
over the network, so the local screen is only for provisioning. When a screen is
needed, the trade uses a **crash cart**: a trolley with a VGA monitor, keyboard
and mouse, rolled to whatever machine is being built. That is why servers still
have VGA and not DisplayPort — every BMC speaks VGA.

**Workstations: business-class IPS, DisplayPort, height-adjustable.** The de
facto desk monitor in engineering is not a gaming panel. It is:

- **Dell UltraSharp 24** (U2412M, U2415, U2422H)
- HP EliteDisplay / Z-series
- Lenovo ThinkVision T24

Why that class, and not a cheap consumer 24 in:

1. **DisplayPort in *and* out.** The DP-out lets a second monitor daisy-chain
   from the first, so one cable from the card serves two screens.
2. **A height-adjustable stand, pivot and VESA 100.** At a desk for hours, the
   stand matters more than the panel.
3. **Several inputs**, which is the poor engineer's KVM: the tower on DisplayPort
   and a laptop on HDMI, switched from the monitor's own menu, with no KVM box.
4. **Cheap on the refurb market**, because offices replace them by the pallet.

**The 16:10 point.** 1920 × 1200 gives 120 more vertical lines than 1080p, and
those lines are where code and toolbars go. That is why the U2415 is still a
favourite a decade after release.

### The pick for this desk

The **Dell UltraSharp U2415**: 24 in, 1920 × 1200 IPS, **mini-DisplayPort input
and DisplayPort output**, height-adjustable, VESA 100. The mini-DP input means
the WX 3200 connects with **one straight mini-DP cable and no adapter at all**,
and the DP-out carries a second screen later.

Prices, checked in the US on 2026-11-25:

| Model | Spec | Used / refurb |
|---|---|---|
| Dell U2412M | 24 in, 1920 × 1200 | ~$90 |
| **Dell U2415** | 24 in, 1920 × 1200, mDP in, DP out | **$75–125** |
| Dell U2422H | 23.8 in, 1920 × 1080, USB-C | $155–169 |

What engineers do **not** use: a television (overscan and wrong scaling), a
touchscreen (nothing here needs touch), a 240 Hz gaming panel unless they also
game, and anything VGA-only.

Colour accuracy is the one spec that does not matter yet. It starts to matter the
day a **book plate is printed**, and then the fix is a calibrator (Calibrite or
Datacolor, about $150), not a more expensive monitor.

### The crash cart, and what a workstation cannot do

The operator, 2026-11-25: "in other words, i am a server engineer. i go to the
server room with my wired keyboard, my wired displayport portable monitor, and
the keyboard as a mouse ball perhaps."

That is a crash cart, and the instinct is right. Three corrections:

- **Racks are VGA, desks are DisplayPort.** What meets you in a server room is
  VGA from the management chip, or a 1U console drawer. A DisplayPort portable
  monitor is the wrong end of that chain.
- **Portable monitors are almost all USB-C**, a few on mini-HDMI. This card has
  mini-DisplayPort, so a portable monitor needs a conversion anyway. The U2415's
  mini-DP input is the cleaner match.
- **A keyboard with a built-in trackball does exist** — it is how 1U rack
  consoles are built, because a rack shelf has no room for a mouse. On a desk a
  $10 mouse is simply better.

The difference that matters: **a workstation has no management chip.** A
ThinkStation P520 cannot be managed headlessly the way a server can, so the
server-engineer habit of never touching the box does not transfer for free.

If headless work is wanted, the substitute is a **KVM over IP**. KVM means
keyboard, video, mouse. An IP-KVM is a small box that sits between you and the
machine: it **captures the machine's HDMI output** and **pretends to be a USB
keyboard and mouse**. You open a web page and see the machine's screen and type
into it. Because it sits *below* the operating system, it works in the UEFI
setup, at the boot menu, during an install, and when the OS is dead. Most also
pretend to be a **USB DVD drive**, so you can mount an ISO over the network and
reinstall an OS with no stick and no walk to the machine.

Prices, checked 2026-11-26 (my earlier "$70 / $200" was low):

| | JetKVM | PiKVM V4 Mini | GL.iNet Comet |
|---|---|---|---|
| Price | **$103** | $238–275 | $99.99 |
| Video capture | 1080p60 | 1920 × 1200@60 | 4K@30 |
| Network | 100 Mbps | Gigabit | Gigabit |
| Remote power | **$19 add-on** | included | add-on |
| Virtual ISO | yes | yes, the mature one | yes |
| Software | app GPLv2, firmware partly closed | fully GPLv3, IPMI and Redfish emulation | UI forked from PiKVM |
| Best for | one cheap box | scripting, ISO installs at scale | reading BIOS screens at 4K |

**PiKVM** is the open-source reference: it runs on a Raspberry Pi CM4, has been
iterated for years, adds serial console, GPIO, an API, and emulates IPMI and
Redfish so server tooling can drive it. **JetKVM** is the cheap, polished
appliance: a Rockchip board in a small box with a touchscreen, 1080p over
WebRTC at a measured 59.8 ms glass-to-glass, now with a full-size HDMI port
rather than the launch mini-HDMI.

Three honest limits:

1. **It is not a management chip.** No temperature sensors, no fan control, no
   inventory. It is eyes and hands only.
2. **EDID matters.** If the capture side presents a resolution the target's
   firmware dislikes, you get a black screen. Prove it on the boot screen before
   you rely on it.
3. **It is a device that can type into your machine.** Change the default
   password, keep it patched, and do not expose it to the internet without a
   tunnel.

**The verdict for this desk:** a $90 used monitor is cheaper than a $103 KVM,
and a keyboard is needed either way. Buy the monitor now. The KVM earns its
money only if the tower actually moves to a cupboard or a rack.

## 11. The portable screen

The operator, 2026-11-26: "i would prefer a mobil screen".

It works, and it is the same crash-cart object: a portable monitor is a plain
display, so POST, the UEFI setup and the installer all appear on it.

**Buying rule: it must have HDMI input.** Portable monitors come in two kinds,
and the second kind is wrong for this card:

| Kind | Ports | Works with the WX 3200? |
|---|---|---|
| **HDMI in + USB-C for power** | mini or micro HDMI, plus USB-C | **yes** — mini-DP → HDMI adapter for video, USB-C charger for power |
| USB-C only | one or two USB-C, video over DisplayPort alt mode | no — needs a DP-alt-mode *sink* adapter, the flakiest link in the chain |

In the ASUS ZenScreen range the USB-C-only models are the MB16AC, MB16ACV and
MB166C; the ones with mini-HDMI are the **MB169CK**, MB16AHV and MB16AHG. Check
the port list, never the model number alone.

Prices, checked 2026-11-26:

| Model | Size | Ports | ~$ |
|---|---|---|---|
| **ASUS MB169CK** | 15.6 in, 1080p IPS | 2× USB-C, **mini-HDMI**, 360° kickstand, 7.6 W | **90** |
| ASUS MB16AHV | 15.6 in, 1080p IPS | 2× USB-C, mini-HDMI, ErgoStand | 150 |
| ASUS MB16AHG | 15.6 in, 1080p 144 Hz | 2× USB-C, mini-HDMI | 210 |

The whole kit:

| Part | ~$ |
|---|---|
| ASUS MB169CK | 90 |
| mini-DP → HDMI active adapter | 24–34 |
| mini-HDMI → HDMI cable, if the box does not include one | 8 |
| 20 W USB-C charger and cable for the panel | 15 |
| **Total** | **~$140–150** |

### Three traps specific to a portable screen

1. **Power it from a charger, not the tower's USB port.** A 15.6 in panel wants
   about 10 W; a PC USB-A port gives 4.5 W, so the picture dims or flickers.
2. **Set the input to HDMI by hand.** Many portable monitors default to USB-C
   and do not switch cleanly when HDMI arrives before the panel has woken. This
   is the one way a portable screen can leave you blind at boot: the machine is
   fine, the screen is on the wrong input. Test it once, from cold.
3. **No height adjustment, often no VESA.** The kickstand is fine for an hour,
   poor for a day.

### The honest comparison

| | used 24 in U2415 | portable 15.6 in |
|---|---|---|
| Price | $75–125 | $140–150 all in |
| Cables | one mini-DP, no power brick | adapter + mini-HDMI + charger |
| Inkscape beside a terminal | comfortable | tight |
| Movable | no | yes |
| Height-adjustable | yes | no |

If portability is the point, the portable is the right buy. It also doubles as
the crash-cart screen: add an HDMI → VGA converter ($15–20) and it can see a
server's VGA output too.

## 12. Sources

- Intel ARK, Xeon W-2245: 8C/16T, 3.90 GHz base, 4.50 all-core, 4.70 max,
  16.5 MB, 155 W, DDR4-2933 four channels, ECC, 48 PCIe 3.0 lanes, AVX-512,
  no integrated graphics, servicing ended 30 June 2025.
- Microsoft Learn: the general Windows 11 Intel list includes Xeon W-2200; the
  24H2 and 25H2 lists omit W-2100 to W-3200. So Windows 11 is arguable, not
  clean — which is another reason Fedora is the right answer here.
- PCSP: P520 900 W page (power rule, two 6+2-pin leads, 8 DIMMs, two M.2, two
  3.5 in); W-2235 listing at $64.99, 64 in stock; WX 3200 listing at $55.99,
  24 in stock, 4 GB GDDR5, 640 cores, 65 W.
- Fedora Project: Fedora 45 released 3 November 2026; Fedora 43 reaches end of
  life 9 December 2026.
