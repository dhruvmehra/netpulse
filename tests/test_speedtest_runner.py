import time
from unittest.mock import patch, MagicMock
import pytest
from speedtest_runner import SpeedTester


def _make_mock_st(download_bps=100_000_000, upload_bps=20_000_000):
    mock = MagicMock()
    mock.download.return_value = download_bps
    mock.upload.return_value = upload_bps
    return mock


def test_run_calls_on_start_then_on_result():
    starts = []
    results = []

    def fake_speedtest():
        return _make_mock_st()

    tester = SpeedTester(
        on_start=lambda: starts.append(1),
        on_result=lambda d, u: results.append((d, u)),
        _speedtest_factory=fake_speedtest,
    )
    tester.run()

    # Wait for background thread
    deadline = time.time() + 5
    while not results and time.time() < deadline:
        time.sleep(0.05)

    assert starts == [1]
    assert results == [(100.0, 20.0)]


def test_run_converts_to_mbps():
    results = []

    def fake_speedtest():
        return _make_mock_st(download_bps=142_300_000, upload_bps=18_700_000)

    tester = SpeedTester(
        on_start=lambda: None,
        on_result=lambda d, u: results.append((d, u)),
        _speedtest_factory=fake_speedtest,
    )
    tester.run()

    deadline = time.time() + 5
    while not results and time.time() < deadline:
        time.sleep(0.05)

    assert results[0] == (142.3, 18.7)


def test_run_noop_if_already_running():
    starts = []
    barrier = __import__("threading").Event()

    def slow_speedtest():
        barrier.wait(timeout=3)
        return _make_mock_st()

    tester = SpeedTester(
        on_start=lambda: starts.append(1),
        on_result=lambda d, u: None,
        _speedtest_factory=slow_speedtest,
    )
    tester.run()
    tester.run()  # second call should be ignored
    barrier.set()

    deadline = time.time() + 5
    while tester.running and time.time() < deadline:
        time.sleep(0.05)

    assert len(starts) == 1


def test_running_flag():
    barrier = __import__("threading").Event()

    def slow_speedtest():
        barrier.wait(timeout=3)
        return _make_mock_st()

    tester = SpeedTester(
        on_start=lambda: None,
        on_result=lambda d, u: None,
        _speedtest_factory=slow_speedtest,
    )
    assert not tester.running
    tester.run()
    assert tester.running
    barrier.set()
