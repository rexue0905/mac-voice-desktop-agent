from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

from actions import validate_command

HOST = "127.0.0.1"
PORT = 8080

AUTH_TOKEN = os.environ.get("AUTH_TOKEN")


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("OK".encode("utf-8"))

    def do_POST(self):
        if self.path != "/command":
            self.send_response(404)
            self.end_headers()
            return

        # ===== 鉴权 =====
        auth_header = self.headers.get("Authorization", "")
        if not AUTH_TOKEN or auth_header != f"Bearer {AUTH_TOKEN}":
            self.send_response(401)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                json.dumps({"ok": False, "error": "unauthorized"}).encode("utf-8")
            )
            return

        # ===== 读取 body =====
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")

        try:
            payload = json.loads(raw_body)
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                json.dumps({"ok": False, "error": "invalid_json"}).encode("utf-8")
            )
            return

        # ===== 白名单校验 =====
        ok, error = validate_command(payload)
        if not ok:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                json.dumps({"ok": False, "error": error}).encode("utf-8")
            )
            return

        action = payload["action"]
        params = payload["params"]

        print(f"[ACTION] {action} | params={params}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))

    def log_message(self, format, *args):
        return


def run_server():
    if not AUTH_TOKEN:
        print("ERROR: AUTH_TOKEN is not set")
        return

    server = HTTPServer((HOST, PORT), SimpleHandler)
    print(f"Server running at http://{HOST}:{PORT}")
    print("POST /command requires Authorization and action/params")
    server.serve_forever()


if __name__ == "__main__":
    run_server()