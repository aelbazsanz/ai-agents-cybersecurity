import socket

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