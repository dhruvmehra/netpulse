import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path

import rumps

import log
from monitor import ConnectivityMonitor
from speedtest_runner import SpeedTester

PLIST_PATH = Path.home() / "Library/LaunchAgents/com.netmapper.app.plist"
PLIST_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>          <string>com.netmapper.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key>      <true/>
    <key>KeepAlive</key>      <false/>
</dict>
</plist>"""


class NetMapperApp(rumps.App):
    def __init__(self):
        super().__init__("🟢", quit_button=None)

        self._dl_item = rumps.MenuItem("⬇ Download: —")
        self._ul_item = rumps.MenuItem("⬆ Upload: —")
        self._speed_btn = rumps.MenuItem("Run Speed Test", callback=self._on_speed_click)
        self._disc_item = rumps.MenuItem("Disconnections (24h): 0")

        self.menu = [
            self._dl_item,
            self._ul_item,
            None,
            self._speed_btn,
            None,
            self._disc_item,
            None,
            rumps.MenuItem("Quit", callback=rumps.quit_application),
        ]

        self._disconnect_start = None  # ISO timestamp of current outage start
        self._state_lock = threading.Lock()

        self._monitor = ConnectivityMonitor(on_change=self._on_connectivity)
        self._tester = SpeedTester(
            on_start=self._on_speed_start,
            on_result=self._on_speed_result,
        )

        self._write_plist_if_needed()
        self._refresh_disconnections()
        self._monitor.start()

    # ── Speed test ───────────────────────────────────────────────────────────

    def _on_speed_click(self, _):
        if not self._tester.running:
            self._tester.run()

    def _on_speed_start(self):
        self._speed_btn.title = "Running…"

    def _on_speed_result(self, download: float, upload: float):
        self._dl_item.title = f"⬇ Download: {download} Mbps"
        self._ul_item.title = f"⬆ Upload: {upload} Mbps"
        self._speed_btn.title = "Run Speed Test"

    # ── Connectivity ─────────────────────────────────────────────────────────

    def _on_connectivity(self, is_connected: bool):
        now = datetime.now(timezone.utc)
        with self._state_lock:
            if is_connected:
                self.title = "🟢"
                if self._disconnect_start is not None:
                    start = datetime.fromisoformat(self._disconnect_start)
                    duration = int((now - start).total_seconds())
                    log.append_event({
                        "type": "reconnect",
                        "timestamp": now.isoformat(),
                        "duration_seconds": duration,
                    })
                    self._disconnect_start = None
            else:
                self.title = "🔴"
                ts = now.isoformat()
                self._disconnect_start = ts
                log.append_event({
                    "type": "disconnect",
                    "timestamp": ts,
                    "duration_seconds": None,
                })
        self._refresh_disconnections()

    # ── Menu refresh ─────────────────────────────────────────────────────────

    def _refresh_disconnections(self):
        count, lines = log.disconnection_summary()
        self._disc_item.title = f"Disconnections (24h): {count}"
        self._disc_item.clear()
        for line in lines:
            self._disc_item.add(rumps.MenuItem(line))

    # ── Auto-start ───────────────────────────────────────────────────────────

    def _write_plist_if_needed(self):
        if PLIST_PATH.exists():
            return
        PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Resolve the MacOS binary relative to this file's bundle location
        app_path = str(
            Path(__file__).resolve().parents[2] / "MacOS" / "NetMapper"
        )
        PLIST_PATH.write_text(PLIST_TEMPLATE.format(app_path=app_path))


if __name__ == "__main__":
    NetMapperApp().run()
