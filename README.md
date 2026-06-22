# Netpulse

A lightweight macOS menubar app that silently monitors your internet connection, logs every dropout, and runs on-demand speed tests — all without leaving the menubar.

---

## Why this exists

Most internet problems are invisible until they're catastrophic. You notice the Wi-Fi dropped only when a call dies or a file upload fails. Netpulse sits in your menubar and does the watching for you: it checks your connection every 30 seconds, records every outage with a precise duration, and keeps a rolling 24-hour log you can inspect at a glance.

Speed tests are a separate frustration — they require opening a browser, navigating to a site, and waiting. Netpulse puts a single click between you and a real download/upload measurement.

The result is a small, native app that answers two questions at any moment: *is my internet working right now?* and *how fast is it?*

---

## Features

- **🟢 / 🔴 menubar icon** — live connectivity status at a glance
- **30-second connectivity checks** via TCP to `8.8.8.8:53` (no ICMP required)
- **Disconnection log** — every outage in the last 24 hours with start time, end time, and duration
- **On-demand speed test** — download and upload in Mbps, runs in the background
- **Persistent event log** at `~/.net_mapper/events.json`
- **Auto-start on login** via a launchd plist written on first run
- **No Dock icon** — runs purely in the menubar

---

## Requirements

- macOS 12 Monterey or later (arm64 or x86_64)
- Python 3.9+
- Xcode Command Line Tools (`xcode-select --install`)

---

## Installation

### Option A — Run from source

```bash
# 1. Clone
git clone https://github.com/dhruvmehra/netpulse.git
cd netpulse

# 2. Create a virtual environment and install dependencies
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Launch
.venv/bin/python app.py
```

A 🟢 icon will appear in your menubar. The app will write a launchd plist to `~/Library/LaunchAgents/com.netmapper.app.plist` on first run so it starts automatically at login.

---

### Option B — Build a standalone `.app`

This packages everything into a self-contained macOS app bundle that does not require Python to be installed.

```bash
# 1. Clone and set up the virtual environment (same as above)
git clone https://github.com/dhruvmehra/netpulse.git
cd netpulse
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2. Build the app bundle
.venv/bin/python setup.py py2app

# 3. Move to Applications (optional)
cp -r dist/NetMapper.app /Applications/

# 4. Launch
open /Applications/NetMapper.app
```

> **Note:** macOS may show a security prompt on first launch. If so, go to **System Settings → Privacy & Security** and click **Open Anyway**.

---

## Usage

| Menu item | Description |
|---|---|
| ⬇ Download: `X` Mbps | Last measured download speed |
| ⬆ Upload: `X` Mbps | Last measured upload speed |
| Run Speed Test | Starts a background speed test; shows **Running…** while active |
| Disconnections (24h): `N` | Count of outages in the last 24 hours |
| ↳ `• HH:MM – HH:MM (Xm)` | Individual outage entries, newest first |
| Quit | Exits the app |

Speed test results and disconnection history update automatically — no manual refresh needed.

---

## Event log

All connectivity events are stored in `~/.net_mapper/events.json`:

```json
[
  { "type": "disconnect", "timestamp": "2026-06-22T09:11:04+00:00", "duration_seconds": null },
  { "type": "reconnect",  "timestamp": "2026-06-22T09:11:52+00:00", "duration_seconds": 48  }
]
```

The file is append-only and written atomically (temp file + rename) to prevent corruption.

---

## Auto-start

On first launch, Netpulse writes:

```
~/Library/LaunchAgents/com.netmapper.app.plist
```

macOS will load this plist at next login and start the app automatically. To disable auto-start:

```bash
launchctl unload ~/Library/LaunchAgents/com.netmapper.app.plist
rm ~/Library/LaunchAgents/com.netmapper.app.plist
```

---

## Development

```bash
# Run tests
.venv/bin/pytest -v

# Alias build (symlinks to source — no recompile needed during development)
.venv/bin/python setup.py py2app -A
open dist/NetMapper.app
```

The test suite covers event log persistence, connectivity state transitions, and speed tester concurrency — all without network I/O.

---

## Project structure

```
netpulse/
├── app.py              # NetMapperApp — menubar UI, wires all modules
├── monitor.py          # ConnectivityMonitor — 30s TCP socket check
├── speedtest_runner.py # SpeedTester — on-demand background speed test
├── log.py              # Event persistence to ~/.net_mapper/events.json
├── setup.py            # py2app build configuration
├── requirements.txt
└── tests/
    ├── test_log.py
    ├── test_monitor.py
    └── test_speedtest_runner.py
```

---

## Dependencies

| Package | License | Purpose |
|---|---|---|
| [rumps](https://github.com/jaredks/rumps) | BSD-3-Clause | macOS menubar app framework |
| [speedtest-cli](https://github.com/sivel/speedtest-cli) | Apache-2.0 | Download/upload measurement |
| [py2app](https://github.com/ronaldoussoren/py2app) | MIT | macOS `.app` bundle packaging |
| [pytest](https://github.com/pytest-dev/pytest) | MIT | Test runner |

---

## License

MIT — see [LICENSE](LICENSE).
