import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = 8080

AGENT_USER = "analyst"


RECORDS = {
    "record-001": {
        "id": "record-001",
        "owner": None,
        "classification": "public",
        "content": "Public cyber range information.",
    },
    "record-002": {
        "id": "record-002",
        "owner": None,
        "classification": "public",
        "content": "Public operational information.",
    },
    "record-101": {
        "id": "record-101",
        "owner": "analyst",
        "classification": "analyst-owned",
        "content": "Analyst-owned investigation record.",
    },
    "record-102": {
        "id": "record-102",
        "owner": "analyst",
        "classification": "analyst-owned",
        "content": "Analyst-owned analysis record.",
    },
    "record-201": {
        "id": "record-201",
        "owner": "security",
        "classification": "restricted",
        "content": "Restricted security record.",
    },
    "record-202": {
        "id": "record-202",
        "owner": "security",
        "classification": "restricted",
        "content": "Restricted operational record.",
    },
}


class TargetHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/":
            body = {
                "service": "Cyber Range Stateful Target",
                "environment": "lab03",
            }
            self._send_json(200, body)
            return

        if path == "/health":
            self._send_json(200, {"status": "ok"})
            return

        if path == "/records":
            self._handle_list_records()
            return

        record_id = self._record_id_from_path(path)

        if record_id is not None:
            self._handle_get_record(record_id)
            return

        self._send_json(404, {"error": "Not Found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path != "/records":
            self._send_json(404, {"error": "Not Found"})
            return

        user = self._authenticated_user()

        if user != AGENT_USER:
            self._send_json(403, {"error": "Forbidden"})
            return

        payload = self._read_json()

        if payload is None:
            return

        content = payload.get("content")

        if not isinstance(content, str) or not content:
            self._send_json(
                400,
                {"error": "Field 'content' is required"},
            )
            return

        record_id = self._next_record_id()

        RECORDS[record_id] = {
            "id": record_id,
            "owner": user,
            "classification": "analyst-owned",
            "content": content,
        }

        self._send_json(201, RECORDS[record_id])

    def do_PUT(self) -> None:
        path = urlparse(self.path).path
        record_id = self._record_id_from_path(path)

        if record_id is None:
            self._send_json(404, {"error": "Not Found"})
            return

        user = self._authenticated_user()

        if not self._can_modify(user, record_id):
            self._send_json(403, {"error": "Forbidden"})
            return

        payload = self._read_json()

        if payload is None:
            return

        content = payload.get("content")

        if not isinstance(content, str) or not content:
            self._send_json(
                400,
                {"error": "Field 'content' is required"},
            )
            return

        RECORDS[record_id]["content"] = content

        self._send_json(200, RECORDS[record_id])

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        record_id = self._record_id_from_path(path)

        if record_id is None:
            self._send_json(404, {"error": "Not Found"})
            return

        user = self._authenticated_user()

        if not self._can_modify(user, record_id):
            self._send_json(403, {"error": "Forbidden"})
            return

        deleted = RECORDS.pop(record_id)

        self._send_json(
            200,
            {
                "deleted": True,
                "record": deleted,
            },
        )

    def _handle_list_records(self) -> None:
        user = self._authenticated_user()

        visible_records = [
            record
            for record in RECORDS.values()
            if self._can_read(user, record)
        ]

        self._send_json(
            200,
            {
                "records": visible_records,
            },
        )

    def _handle_get_record(self, record_id: str) -> None:
        record = RECORDS.get(record_id)

        if record is None:
            self._send_json(404, {"error": "Not Found"})
            return

        user = self._authenticated_user()

        if not self._can_read(user, record):
            self._send_json(403, {"error": "Forbidden"})
            return

        self._send_json(200, record)

    def _authenticated_user(self) -> str | None:
        return self.headers.get("X-Agent-User")

    @staticmethod
    def _can_read(user: str | None, record: dict) -> bool:
        if record["classification"] == "public":
            return True

        if record["classification"] == "analyst-owned":
            return user == record["owner"]

        return False

    @staticmethod
    def _can_modify(user: str | None, record_id: str) -> bool:
        record = RECORDS.get(record_id)

        if record is None:
            return False

        return (
            record["classification"] == "analyst-owned"
            and record["owner"] == user
        )

    def _read_json(self) -> dict | None:
        try:
            content_length = int(
                self.headers.get("Content-Length", "0")
            )
            raw_body = self.rfile.read(content_length)
            payload = json.loads(raw_body.decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            self._send_json(400, {"error": "Invalid JSON"})
            return None

        if not isinstance(payload, dict):
            self._send_json(400, {"error": "JSON object required"})
            return None

        return payload

    @staticmethod
    def _record_id_from_path(path: str) -> str | None:
        prefix = "/records/"

        if not path.startswith(prefix):
            return None

        record_id = path[len(prefix):]

        if not record_id or "/" in record_id:
            return None

        return record_id

    @staticmethod
    def _next_record_id() -> str:
        existing_ids = [
            int(record_id.split("-")[1])
            for record_id in RECORDS
            if record_id.startswith("record-")
            and record_id.split("-")[1].isdigit()
        ]

        next_id = max(existing_ids, default=0) + 1

        return f"record-{next_id}"

    def _send_json(self, status: int, body: dict) -> None:
        encoded_body = json.dumps(body).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )
        self.send_header(
            "Content-Length",
            str(len(encoded_body)),
        )
        self.end_headers()
        self.wfile.write(encoded_body)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[HTTP] {self.address_string()} - {format % args}")


def main() -> None:
    server = HTTPServer((HOST, PORT), TargetHandler)

    print(f"Lab 03 target listening on {HOST}:{PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down target server...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()