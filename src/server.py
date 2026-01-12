from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

from actions import validate_command
from queue_manager import QueueManager

HOST = "0.0.0.0"
PORT = 8080

AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
QUEUE_MANAGER = QueueManager()


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/status":
            if not self._is_authorized():
                self._send_json(401, {"ok": False, "error": "unauthorized"})
                return
            self._send_json(200, {"ok": True, "data": QUEUE_MANAGER.status()})
            return

        if self.path == "/logs":
            if not self._is_authorized():
                self._send_json(401, {"ok": False, "error": "unauthorized"})
                return
            self._send_json(200, {"ok": True, "data": QUEUE_MANAGER.logs()})
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("OK".encode("utf-8"))

    def do_POST(self):
        if self.path == "/stop":
            if not self._is_authorized():
                self._send_json(401, {"ok": False, "error": "unauthorized"})
                return
            result = QUEUE_MANAGER.stop_all()
            self._send_json(200, result)
            return

        if self.path != "/command":
            self.send_response(404)
            self.end_headers()
            return

        # ===== 鉴权 =====
        if not self._is_authorized():
            self._send_json(401, {"ok": False, "error": "unauthorized"})
            return

        # ===== 读取 body =====
        raw_body = self._read_body()

        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            self._send_json(400, {"ok": False, "error": "invalid_json"})
            return

        # ===== 白名单校验 =====
        ok, error = validate_command(payload)
        if not ok:
            self._send_json(400, {"ok": False, "error": error})
            return

        action = payload["action"]
        params = payload["params"]

        task_id = QUEUE_MANAGER.enqueue(action, params)

        self._send_json(200, {"ok": True, "task_id": task_id})

    def log_message(self, format, *args):
        return

    def _read_body(self) -> str:
        content_length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(content_length).decode("utf-8")

    def _send_json(self, status: int, payload: dict) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _is_authorized(self) -> bool:
        auth_header = self.headers.get("Authorization", "")
        return bool(AUTH_TOKEN) and auth_header == f"Bearer {AUTH_TOKEN}"


def run_server():
    if not AUTH_TOKEN:
        print("ERROR: AUTH_TOKEN is not set")
        return

    server = HTTPServer((HOST, PORT), SimpleHandler)
    print(f"Server running at http://{HOST}:{PORT}")
    print("POST /command requires Authorization and action/params")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped")


if __name__ == "__main__":
    run_server()
