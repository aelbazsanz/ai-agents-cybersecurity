# WebApp for the target server in lab02-agent-isolated-target.

# imports
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "0.0.0.0"
PORT = 8080

# Class to handle HTTP requests for the target server
class TargetHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/":
            body = (
                "Cyber Range Target\n"
                "Service: HTTP\n"
                "Environment: lab02\n"
            )
            self._send_response(200, body)
            return

        if self.path == "/health":
            self._send_response(200, "OK\n")
            return

        self._send_response(404, "Not Found\n")

    def _send_response(self, status: int, body: str) -> None:
        encoded_body = body.encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded_body)))
        self.end_headers()
        self.wfile.write(encoded_body)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[HTTP] {self.address_string()} - {format % args}")


def main() -> None:
    server = HTTPServer((HOST, PORT), TargetHandler)

    print(f"Target HTTP server listening on {HOST}:{PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down target server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()