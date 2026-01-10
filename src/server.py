from http.server import BaseHTTPRequestHandler, HTTPServer
import json

HOST = "127.0.0.1"
PORT = 8080


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 健康检查：浏览器打开看到 OK
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("OK".encode("utf-8"))

    def do_POST(self):
        # 只处理 /command
        if self.path != "/command":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")

        try:
            data = json.loads(raw_body)
            text = str(data.get("text", "")).strip()
        except json.JSONDecodeError:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "invalid_json"}).encode("utf-8"))
            return

        # 目前只打印，不执行任何动作
        print(f"[COMMAND] {text}")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))

    def log_message(self, format, *args):
        return


def run_server():
    server = HTTPServer((HOST, PORT), SimpleHandler)
    print(f"Server running at http://{HOST}:{PORT}")
    print("POST /command with JSON: {\"text\":\"...\"}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()