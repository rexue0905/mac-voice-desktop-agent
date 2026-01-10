from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

HOST = "127.0.0.1"
PORT = 8080

# 从环境变量读取 Token
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 健康检查
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("OK".encode("utf-8"))

    def do_POST(self):
        # 只允许 /command
        if self.path != "/command":
            self.send_response(404)
            self.end_headers()
            return

        # ===== 鉴权开始 =====
        auth_header = self.headers.get("Authorization", "")
        expected = f"Bearer {AUTH_TOKEN}"

        if not AUTH_TOKEN or auth_header != expected:
            self.send_response(401)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                json.dumps({"ok": False, "error": "unauthorized"}).encode("utf-8")
            )
            return
        # ===== 鉴权结束 =====

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")

        try:
            data = json.loads(raw_body)
            text = str(data.get("text", "")).strip()
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(
                json.dumps({"ok": False, "error": "invalid_json"}).encode("utf-8")
            )
            return

        # 目前只打印，不执行
        print(f"[COMMAND] {text}")

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
    print("POST /command requires Authorization: Bearer <TOKEN>")
    server.serve_forever()


if __name__ == "__main__":
    run_server()