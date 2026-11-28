mint

grep wlp3s0

 A dialog taller than the screen needs the keyboard, not the mouse. Three ways, in order of speed:
1. Press Enter. In a save dialog the name field has focus and Save is the default button. Type the filename, press Enter, done — no clicking required.
2. Alt + drag. Hold Alt and drag anywhere inside the dialog. The whole window moves up, bringing the buttons into view. This works on any window, in any app.
3. Alt+F8, then arrow keys. Resizes with the keyboard; press the up arrow until the dialog shortens, then Enter.
Also useful inside a file chooser: Ctrl+L replaces the file list with a text path box. Type the full path, e.g. ~/Documents/notes.txt, press Enter — you never touch the Save button.
The space you're losing
Two things eat those pixels:
The panel. Right-click it → Panel → Panel Preferences → tick Automatically hide the panel. You get ~30 px back, and it reappears when you point at the screen edge.
DPI is a trade. At 100 you have more room and smaller text. If dialogs still overflow, 96 is the true default.
The Alt+drag trick is the one worth memorising — it saves you from every oversized dialog on this machine, not just this one.

I'm here. Two keyboard tricks fix exactly this, and they work on any window that's bigger than the screen:
Resize: press Alt+F8, then the arrow keys shrink it, Enter to finish. Keep pressing the up arrow to pull the bottom edge down until the message box appears.
Move: press Alt+F7, then drag with the arrow keys or the pointer, Enter to finish. Use this if part of the window is off the bottom or right edge.
Or, holding the pointer: Alt + right-drag resizes from anywhere inside the window, no corner needed.
If it refuses to go smaller
Telegram's window has a minimum height, and if your DPI is at 110 it makes that minimum taller. Two options:
- Lower DPI to 100 in Settings → Appearance → Fonts. Everything shrinks slightly, and Telegram's floor comes down with it.
- Or double-click the title bar to maximize while you type, then un-maximize. Not ideal on a small screen, but it works.
The Alt+F8 route is the one to remember — it's the standard rescue for any oversized window, including dialogs where you can't reach the buttons.
***
 Same account on both, and use Saved Messages as the transfer channel.
On the Mac
Download from https://desktop.telegram.org (or the App Store). Sign in with your phone number — the Mac app shows a QR code, or sends a login code to your phone. If you've set a two-step password, you'll type that too.
On the laptop
Software Manager → search "Telegram" → install Telegram Desktop. It's in the Mint repository, so it updates with the rest of the system.
Better than Telegram Web on this machine: the native app uses a fraction of the RAM a browser tab does, and you only have 3.6 GB.
Launch it from the menu, choose Log in by QR code, then on your phone: Telegram → Settings → Devices → Link Desktop Device → point the phone at the laptop screen.
The transfer loop
On the Mac, open Saved Messages (your own chat, in the chat list) and paste the command.
On the laptop, open Saved Messages — the same conversation appears.
Select the text, Ctrl+C.
Click the terminal, Ctrl+Shift+V, Enter.
Both devices see the same saved chat, so it's one place for all of it, and it survives a reboot on either side.
Two practical notes
Files beat text. You can drop a .txt in Saved Messages; on the laptop it opens in the text editor with one double-click, then Ctrl+A and copy. No fiddling with selection in a chat bubble.
The laptop keeps you signed in until you remove it under Settings → Devices. On a home machine that's fine; remove it before the laptop leaves the house.


***
 Thunar, and it's in the menu as Files — same idea as Finder, one window per folder unless you open a new one.
The shortcuts that map from Finder:
Finder	Thunar
Cmd+Shift+G (go to path)	Ctrl+L — type a path, e.g. /home/you/Downloads
Cmd+Shift+. (show hidden)	Ctrl+H
Cmd+F (search)	Ctrl+F
Cmd+Up (enclosing folder)	Alt+Up
Cmd+Delete (to Trash)	Delete
Cmd+2 (list view)	Ctrl+2
Other things worth knowing:
The sidebar lists Home, Desktop, Downloads, Documents, Trash, plus any USB stick or disk you plug in. That's your Finder sidebar.
Right-click in a folder → Open Terminal Here is built in. That's how you'd ever need a terminal at a location, without typing a path.
F3 splits the window into two panes — handy for moving files, Finder can't do this without tabs.
Network shares are under Browse Network in the sidebar.
Deleting something sends it to Trash; it sits there until you empty it. Nothing vanishes immediately.
The one real difference: there's no single "All My Files" view. Your home folder is as close as it gets.


1. Touchpad that actually travels
Test it live first, in a terminal:
xinput list
That prints the touchpad's name, usually SynPS/2 Synaptics TouchPad on this ASUS. Then:
xinput set-prop "SynPS/2 Synaptics TouchPad" "libinput Accel Speed" 0.8
The range is −1 to 1, and 0 is the default. Try 0.5, then 0.8, then 1.0 and keep the one that lets you cross the screen without lifting your finger. That command lasts until logout — it's for finding your number.
Once you know it, make it stick:
sudo tee /etc/X11/xorg.conf.d/50-touchpad.conf >/dev/null <<'EOF'
Section "InputClass"
    Identifier "touchpad"
    MatchIsTouchpad "on"
    Driver "libinput"
    Option "AccelSpeed" "0.8"
    Option "Tapping" "on"
    Option "ScrollMethod" "twofinger"
EndSection
EOF
Log out and back in. If two-finger scrolling is also slow, add Option "ScrollPixelDistance" "8" inside that section — smaller means faster.



Five lines of typing. Tapping isn't needed — Mint has tap-to-click on already, and it costs you nothing. Change 0.8 to 0.5 if the pointer ends up too fast, or 1.0 if still too slow.
Save: Ctrl+O, Enter. Exit: Ctrl+X.
But consider not typing at all
The Mouse and Touchpad → Touchpad panel has an acceleration slider that writes the same setting to a different file. Zero typing, no log out. Push it to the maximum and try the pointer.
If the maximum is enough, you're done — skip the config file entirely. The file is only worth typing when the slider's top end is still too slow, because the slider c



2. Bigger, cleaner text
sudo apt install -y fonts-inter fonts-noto-core
Then Settings → Appearance → Fonts:
- Default Font: Inter 11 — a screen face drawn for small sizes. If Inter isn't offered, Noto Sans 11 is fine.
- Enable anti-aliasing: on. Hinting: Full. Sub-pixel order: RGB. Those three are what stop small text looking smeared on an LCD.
- Custom DPI setting: tick it, set 110. This is the master switch — it scales menus, panels and windows together, not just one app. 96 is the default; 110 is about 15 % bigger. Go to 120 if you still squint.
Then in Firefox: Settings → General → Zoom at 110 %, so pages match.

3. Chrome
cd ~/Downloads
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
The ./ matters: it makes apt resolve the dependencies in one pass and register Google's repository, so Chrome updates with the rest of the system.
Two things to expect:
- Disable graphics acceleration in Chrome too — chrome://settings → System → turn off "Use graphics acceleration when available". Same GeForce 310M problem you hit in Firefox.
- Chrome is heavier than Firefox on 3.6 GB of RAM. It will work; keep the tab count low.
Where is the install?
Tell me whether Mint is installed and running, or still copying — if it's still going, don't touch any of the above yet, the settings would be lost on reboot.
https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
state/parked-focus-int.md


****
I'm here. Yes — Cancel is safe at this point, because nothing has been unpacked yet. The dialog is asking before any files change, so cancelling leaves the system exactly as it is and the rest of the batch simply waits.
Two things to know:
- Cancelling stops the whole run, not just the codecs. Everything else in that batch stays uninstalled until you run Update Manager again. The already-downloaded packages are cached, so the second attempt is quicker.
- Do it soon. Modern Mint runs fine with the older codec package, but the delay is what keeps re-prompting. One Click of Install Updates later and it's done.
The unsafe moment is different and easy to spot: once it says "Installing" or "Unpacking", don't cancel or power off. That's when files are half-written. The confirmation dialog is before that line, so you're in the harmless zone.


***
 That reading tells you exactly what's wrong: location 0, 0 means no location, and with no location Redshift can't work out whether it's day or night, so 0 K / period unknown — it's running but doing nothing to the screen.
The instance in the tray was started from the menu with no arguments.
Fix it in the tray
Left-click the lightbulb → Preferences → tick Set the location manually → enter your latitude and longitude → Apply.
For London that's 51.5 and -0.12. Then the same tray menu should read something sane: a real location, a temperature around 5800 K, and Period: Day (or Night).
That writes the setting to Redshift's own config, so the menu item works from then on and the autostart entry inherits it.
If the Preferences window has no location box
Then use the file, and any launch gets it right:
mkdir -p ~/.config/redshift
nano ~/.config/redshift/redshift.conf
Paste:
[redshift]
location-provider=manual
temp-day=5800
temp-night=3600

[manual]
lat=51.5
lon=-0.12
Ctrl+O, Enter, Ctrl+X. Then right-click the lightbulb → Quit, and start it again from the menu.
Either way, the check is the same: location not 0,0 and period Day or Night, not unknown.
***

Worth one test, yes — but do it after the update is done, and use a terminal, not a website. A browser speed test burns CPU on this machine and measures the browser as much as the connection.
curl -o /dev/null -w "download %{speed_download} bytes/s\n" -L "https://speed.cloudflare.com/__down?bytes=50000000"
Divide the number by a million for MB/s. On this card, 5–9 MB/s is normal; the Centrino 1000 is an 802.11n 1×2 chip, and that's its ceiling. If you see 1–2 MB/s, the radio is negotiating badly, not the update's fault.
What the test is actually for:
A baseline for the 11n_disable=1 change. That setting costs throughput. One number before, one after, and you know what it bought you — if it bought nothing, remove the setting.
A check on the drops. If speed is fine when connected, the problem really is just re-association, not a weak signal.
For signal strength without a test at all:
nmcli -f IN-USE,SIGNAL,RATE dev wifi
Signal under about 50 means you're far from the router, and moving closer will do more for reliability than any setting.

That's the Centrino Wireless-N 1000 doing what those cards do: the driver's power saving puts the radio to sleep and the connection drops, then it wakes and rejoins. Ten seconds, then back — that's the signature.
Wait until the update finishes before changing anything, because restarting the network mid-install interrupts it.
Then, in a terminal — first find the interface name (ls /sys/class/net, the wireless one starts with wl):
sudo iw dev wlp4s0 set power_save off
That stops the drops immediately, but it resets at reboot. To make it stick:
sudo tee /etc/NetworkManager/conf.d/wifi-powersave-off.conf >/dev/null <<'EOF'
[connection]
wifi.powersave = 2
EOF
sudo systemctl restart NetworkManager
wifi.powersave = 2 means "disabled".
If it still drops
Old Intel cards also struggle with 802.11n aggregation. This costs you some speed and buys stability:
sudo tee /etc/modprobe.d/iwlwifi.conf >/dev/null <<'EOF'
options iwlwifi 11n_disable=1
EOF
sudo update-initramfs -u
Then reboot.
While the update is running
Drops are mostly harmless — apt resumes and retries on its own. If you see Failed to fetch in the update window, don't restart anything; just click Install Updates again and it picks up where it stopped.

