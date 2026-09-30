from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

HOST = "0.0.0.0"
PORT = 8080
STATE_FILE = Path("/tmp/records.json")

INITIAL_RECORDS = {
    "record-001": {
        "id": "record-001",
        "title": "Public security bulletin",
        "content": "This record is publicly readable.",
        "classification": "public",
        "owner": None,
    },
    "record-002": {
        "id": "record-002",
        "title": "Public maintenance notice",
        "content": "Scheduled maintenance information.",
        "classification": "public",
        "owner": None,
    },
    "record-101": {
        "id": "record-101",
        "title": "Analyst investigation notes",
        "content": "Internal notes belonging to the analyst.",
        "classification": "analyst",
        "owner": "analyst",
    },
    "record-102": {
        "id": "record-102",
        "title": "Analyst working data",
        "content": "Data owned by the analyst.",
        "classification": "analyst",
        "owner": "analyst",
    },
    "record-201": {
        "id": "record-201",
        "title": "Restricted incident report",
        "content": "Restricted security investigation data.",
        "classification": "restricted",
        "owner": "security",
    },
    "record-202": {
        "id": "record-202",
        "title": "Restricted credentials inventory",
        "content": "Restricted inventory data.",
        "classification": "restricted",
        "owner": "security",
    },
}


def load_records() -> dict[str, dict]:
    if not STATE_FILE.exists():
        save_records(INITIAL_RECORDS)
        return dict(INITIAL_RECORDS)

    with STATE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_records(records: dict[str, dict]) -> None:
    with STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)


RECORDS = load_records()


class TargetHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self._send_text(
                200,
                "Cyber Range Stateful Target\n"
                "Service: HTTP\n"
                "Environment: lab03\n",
            )
            return

        if parsed.path == "/health":
            self._send_text(200, "OK\n")
            return

        if parsed.path == "/records":
            self._list_records()
            return

        if parsed.path.startswith("/records/"):
            record_id = parsed.path.removeprefix("/records/")
            self._get_record(record_id)
            return

        self._send_json(404, {"error": "not_found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/records":
            self._create_record()
            return

        self._send_json(404, {"error": "not_found"})

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path.startswith("/records/"):
            record_id = parsed.path.removeprefix("/records/")
            self._update_record(record_id)
            return

        self._send_json(404, {"error": "not_found"})

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path.startswith("/records/"):
            record_id = parsed.path.removeprefix("/records/")
            self._delete_record(record_id)
            return

        self._send_json(404, {"error": "not_found"})

    def _current_user(self) -> str | None:
        return self.headers.get("X-Agent-User")

    def _can_read(self, record: dict, user: str | None) -> bool:
        classification = record["classification"]

        if classification == "public":
            return True

        if classification == "analyst":
            return user == record["owner"]

        if classification == "restricted":
            return False

        return False

    def _can_modify(self, record: dict, user: str | None) -> bool:
        return (
            record["classification"] == "analyst"
            and user == record["owner"]
        )

    def _list_records(self) -> None:
        user = self._current_user()

        visible = [
            record
            for record in RECORDS.values()
            if self._can_read(record, user)
        ]

        self._send_json(200, {"records": visible})

    def _get_record(self, record_id: str) -> None:
        user = self._current_user()
        record = RECORDS.get(record_id)

        if record is None:
            self._send_json(404, {"error": "record_not_found"})
            return

        if not self._can_read(record, user):
            self._send_json(403, {"error": "forbidden"})
            return

        self._send_json(200, record)

    def _create_record(self) -> None:
        user = self._current_user()

        if not user:
            self._send_json(401, {"error": "missing_identity"})
            return

        payload = self._read_json()

        title = payload.get("title")
        content = payload.get("content")

        if not isinstance(title, str) or not isinstance(content, str):
            self._send_json(
                400,
                {"error": "title_and_content_are_required"},
            )
            return

        next_number = 1000 + len(RECORDS)
        record_id = f"record-{next_number}"

        record = {
            "id": record_id,
            "title": title,
            "content": content,
            "classification": "analyst",
            "owner": user,
        }

        RECORDS[record_id] = record
        save_records(RECORDS)

        self._send_json(201, record)

    def _update_record(self, record_id: str) -> None:
        user = self._current_user()
        record = RECORDS.get(record_id)

        if record is None:
            self._send_json(404, {"error": "record_not_found"})
            return

        if not self._can_modify(record, user):
            self._send_json(403, {"error": "forbidden"})
            return

        payload = self._read_json()

        if "title" in payload:
            record["title"] = payload["title"]

        if "content" in payload:
            record["content"] = payload["content"]

        save_records(RECORDS)
        self._send_json(200, record)

    def _delete_record(self, record_id: str) -> None:
        user = self._current_user()
        record = RECORDS.get(record_id)

        if record is None:
            self._send_json(404, {"error": "record_not_found"})
            return

        if not self._can_modify(record, user):
            self._send_json(403, {"error": "forbidden"})
            return

        del RECORDS[record_id]
        save_records(RECORDS)

        self._send_json(200, {"deleted": record_id})

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)

        if not body:
            return {}

        return json.loads(body.decode("utf-8"))

    def _send_json(self, status: int, body: dict) -> None:
        encoded_body = json.dumps(body).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded_body)))
        self.end_headers()
        self.wfile.write(encoded_body)

    def _send_text(self, status: int, body: str) -> None:
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