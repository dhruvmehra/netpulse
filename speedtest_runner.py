import threading
import speedtest as _st_lib


def _default_speedtest_factory():
    s = _st_lib.Speedtest()
    s.get_best_server()
    return s


class SpeedTester:
    def __init__(self, on_start, on_result, _speedtest_factory=None):
        self._on_start = on_start
        self._on_result = on_result
        self._factory = _speedtest_factory or _default_speedtest_factory
        self._running = False
        self._lock = threading.Lock()

    @property
    def running(self) -> bool:
        return self._running

    def run(self):
        with self._lock:
            if self._running:
                return
            self._running = True
        self._on_start()
        threading.Thread(target=self._execute, daemon=True).start()

    def _execute(self):
        try:
            s = self._factory()
            download = round(s.download() / 1_000_000, 1)
            upload = round(s.upload() / 1_000_000, 1)
            self._on_result(download, upload)
        finally:
            self._running = False
