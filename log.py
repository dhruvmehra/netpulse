import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

DATA_DIR = Path.home() / ".net_mapper"
LOG_FILE = DATA_DIR / "events.json"


def _read(path: Path) -> list:
    if not path.exists():
        return []
    with open(path) as f:
        return json.load(f)


def _write(events: list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(events, f, indent=2)
    tmp.replace(path)


def append_event(event: dict, path: Path = LOG_FILE) -> None:
    events = _read(path)
    events.append(event)
    _write(events, path)


def events_last_24h(path: Path = LOG_FILE) -> list:
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    return [e for e in _read(path) if e["timestamp"] >= cutoff]


def disconnection_summary(path: Path = LOG_FILE) -> tuple:
    events = events_last_24h(path)
    lines = []
    pending_start = None

    for e in events:
        if e["type"] == "disconnect":
            pending_start = e["timestamp"]
        elif e["type"] == "reconnect" and pending_start is not None:
            d = e["duration_seconds"]
            start_dt = datetime.fromisoformat(pending_start)
            start_str = start_dt.strftime("%H:%M")
            end_dt = start_dt + timedelta(seconds=d)
            end_str = end_dt.strftime("%H:%M")
            dur_str = f"{d // 60}m" if d >= 60 else "<1m"
            lines.append(f"• {start_str} – {end_str} ({dur_str})")
            pending_start = None

    if pending_start is not None:
        start_str = datetime.fromisoformat(pending_start).strftime("%H:%M")
        lines.append(f"• {start_str} – ongoing")

    count = sum(1 for e in events if e["type"] == "disconnect")
    return count, list(reversed(lines))[-10:]
