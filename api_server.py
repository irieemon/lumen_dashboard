import threading
import socket
import time
from api import app as api_app

API_PORT = 8000
API_STARTED = False


def _start_api() -> None:
    api_app.run(host="0.0.0.0", port=API_PORT, debug=False, use_reloader=False)


def _port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def ensure_api_running() -> None:
    global API_STARTED
    if API_STARTED:
        return
    if _port_in_use(API_PORT):
        API_STARTED = True
        return
    thread = threading.Thread(target=_start_api, daemon=True)
    thread.start()
    for _ in range(50):  # wait up to ~5s for the server to start
        if _port_in_use(API_PORT):
            API_STARTED = True
            return
        time.sleep(0.1)
