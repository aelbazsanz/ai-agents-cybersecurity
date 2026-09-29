# imports
import socket
import urllib.error
import urllib.request

# define resolve_host tool
def resolve_host(host: str) -> dict:
    try:
        ip = socket.gethostbyname(host)
        return {
            "host": host,
            "resolved": True,
            "ip": ip,
        }
    except socket.gaierror as exc:
        return {
            "host": host,
            "resolved": False,
            "error": str(exc),
        }

# define check_tcp_port tool
def check_tcp_port(host: str, port: int) -> dict:
    try:
        with socket.create_connection((host, port), timeout=2):
            return {
                "host": host,
                "port": port,
                "reachable": True,
            }
    except (socket.timeout, ConnectionRefusedError, OSError) as exc:
        return {
            "host": host,
            "port": port,
            "reachable": False,
            "error": str(exc),
        }

# define http_get tool
def http_get(host: str, port: int, path: str) -> dict:
    url = f"http://{host}:{port}{path}"

    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            body = response.read().decode("utf-8", errors="replace")

            return {
                "host": host,
                "port": port,
                "path": path,
                "status_code": response.status,
                "body": body,
            }

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")

        return {
            "host": host,
            "port": port,
            "path": path,
            "status_code": exc.code,
            "body": body,
        }

    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            "host": host,
            "port": port,
            "path": path,
            "error": str(exc),
        }