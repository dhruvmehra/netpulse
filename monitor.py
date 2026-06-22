import socket
import threading


class ConnectivityMonitor:
    INTERVAL = 30  # seconds
    HOST = "8.8.8.8"
    PORT = 53
    TIMEOUT = 3

    def __init__(self, on_change):
        self._on_change = on_change
        self._connected = None
        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def _check(self) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.TIMEOUT)
                s.connect((self.HOST, self.PORT))
            return True
        except OSError:
            return False

    def _poll(self):
        is_connected = self._check()
        if is_connected != self._connected:
            self._connected = is_connected
            self._on_change(is_connected)

    def _run(self):
        while not self._stop_event.is_set():
            self._poll()
            self._stop_event.wait(self.INTERVAL)
