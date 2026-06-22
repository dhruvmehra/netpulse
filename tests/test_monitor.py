import socket
from unittest.mock import patch, MagicMock
import pytest
from monitor import ConnectivityMonitor


def test_check_returns_true_when_connected():
    with patch("monitor.socket.socket") as MockSocket:
        instance = MockSocket.return_value.__enter__.return_value
        instance.connect.return_value = None  # no exception = success
        m = ConnectivityMonitor(on_change=lambda _: None)
        assert m._check() is True


def test_check_returns_false_when_oserror():
    with patch("monitor.socket.socket") as MockSocket:
        instance = MockSocket.return_value.__enter__.return_value
        instance.connect.side_effect = OSError("timeout")
        m = ConnectivityMonitor(on_change=lambda _: None)
        assert m._check() is False


def test_on_change_called_on_transition():
    calls = []

    with patch("monitor.socket.socket") as MockSocket:
        instance = MockSocket.return_value.__enter__.return_value
        instance.connect.return_value = None
        m = ConnectivityMonitor(on_change=calls.append)
        # Simulate first check (None → True)
        m._poll()
        assert calls == [True]


def test_on_change_not_called_when_no_transition():
    calls = []

    with patch("monitor.socket.socket") as MockSocket:
        instance = MockSocket.return_value.__enter__.return_value
        instance.connect.return_value = None
        m = ConnectivityMonitor(on_change=calls.append)
        m._poll()   # None → True
        m._poll()   # True → True (no change)
        assert calls == [True]


def test_on_change_called_on_disconnect():
    calls = []
    results = [True, False]

    def fake_check(self_):
        return results.pop(0)

    with patch.object(ConnectivityMonitor, "_check", fake_check):
        m = ConnectivityMonitor(on_change=calls.append)
        m._poll()  # None → True
        m._poll()  # True → False
        assert calls == [True, False]
