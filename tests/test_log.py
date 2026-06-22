import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import pytest
import log


@pytest.fixture
def tmp_log(tmp_path):
    return tmp_path / "events.json"


def _iso(dt):
    return dt.isoformat()


def now():
    return datetime.now(timezone.utc)


def test_append_creates_file(tmp_log):
    log.append_event({"type": "disconnect", "timestamp": _iso(now()), "duration_seconds": None}, tmp_log)
    assert tmp_log.exists()
    data = json.loads(tmp_log.read_text())
    assert len(data) == 1
    assert data[0]["type"] == "disconnect"


def test_append_accumulates(tmp_log):
    log.append_event({"type": "disconnect", "timestamp": _iso(now()), "duration_seconds": None}, tmp_log)
    log.append_event({"type": "reconnect", "timestamp": _iso(now()), "duration_seconds": 45}, tmp_log)
    data = json.loads(tmp_log.read_text())
    assert len(data) == 2


def test_events_last_24h_filters_old(tmp_log):
    old = now() - timedelta(hours=25)
    recent = now() - timedelta(hours=1)
    log.append_event({"type": "disconnect", "timestamp": _iso(old), "duration_seconds": None}, tmp_log)
    log.append_event({"type": "disconnect", "timestamp": _iso(recent), "duration_seconds": None}, tmp_log)
    result = log.events_last_24h(tmp_log)
    assert len(result) == 1
    assert result[0]["timestamp"] == _iso(recent)


def test_events_last_24h_empty_file(tmp_log):
    assert log.events_last_24h(tmp_log) == []


def test_disconnection_summary_count(tmp_log):
    t1 = now() - timedelta(hours=2)
    t2 = t1 + timedelta(seconds=120)
    log.append_event({"type": "disconnect", "timestamp": _iso(t1), "duration_seconds": None}, tmp_log)
    log.append_event({"type": "reconnect", "timestamp": _iso(t2), "duration_seconds": 120}, tmp_log)
    count, lines = log.disconnection_summary(tmp_log)
    assert count == 1
    assert len(lines) == 1
    assert "2m" in lines[0]


def test_disconnection_summary_ongoing(tmp_log):
    log.append_event({"type": "disconnect", "timestamp": _iso(now() - timedelta(minutes=5)), "duration_seconds": None}, tmp_log)
    count, lines = log.disconnection_summary(tmp_log)
    assert count == 1
    assert "ongoing" in lines[0]


def test_disconnection_summary_under_1m(tmp_log):
    t1 = now() - timedelta(hours=1)
    log.append_event({"type": "disconnect", "timestamp": _iso(t1), "duration_seconds": None}, tmp_log)
    log.append_event({"type": "reconnect", "timestamp": _iso(t1 + timedelta(seconds=45)), "duration_seconds": 45}, tmp_log)
    _, lines = log.disconnection_summary(tmp_log)
    assert "<1m" in lines[0]


def test_disconnection_summary_max_10(tmp_log):
    for i in range(15):
        t = now() - timedelta(hours=i + 0.5)
        log.append_event({"type": "disconnect", "timestamp": _iso(t), "duration_seconds": None}, tmp_log)
        log.append_event({"type": "reconnect", "timestamp": _iso(t + timedelta(seconds=30)), "duration_seconds": 30}, tmp_log)
    count, lines = log.disconnection_summary(tmp_log)
    assert count == 15
    assert len(lines) == 10
