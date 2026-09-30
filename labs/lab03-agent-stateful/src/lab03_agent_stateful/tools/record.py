import json
import os
import urllib.error
import urllib.request


TARGET_HOST = os.environ["TARGET_HOST"]
TARGET_PORT = 8080
AGENT_USER = os.environ["AGENT_USER"]


def _request(
    method: str,
    path: str,
    payload: dict | None = None,
) -> dict:
    url = f"http://{TARGET_HOST}:{TARGET_PORT}{path}"

    headers = {
        "X-Agent-User": AGENT_USER,
    }

    data = None

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers=headers,
    )

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            body = response.read().decode("utf-8")

            return {
                "status_code": response.status,
                "body": json.loads(body),
            }

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")

        return {
            "status_code": exc.code,
            "body": json.loads(body),
        }

    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            "error": str(exc),
        }

def get_record(record_id: str) -> dict:
    return _request(
        "GET",
        f"/records/{record_id}",
    )

def list_records() -> dict:
    return _request(
        "GET",
        "/records",
    )

def create_record(title: str, content: str) -> dict:
    return _request(
        "POST",
        "/records",
        {
            "title": title,
            "content": content,
        },
    )

def update_record(
    record_id: str,
    title: str | None = None,
    content: str | None = None,
) -> dict:
    payload = {}

    if title is not None:
        payload["title"] = title

    if content is not None:
        payload["content"] = content

    return _request(
        "PUT",
        f"/records/{record_id}",
        payload,
    )