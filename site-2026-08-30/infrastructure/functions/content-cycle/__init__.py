"""Timer-triggered content cycle for Azure Functions (v1 programming model)."""

import os
import urllib.error
import urllib.request


def main(timer: object) -> None:
    api = os.environ["API_BASE_URL"].rstrip("/")
    secret = os.environ["CONTENT_CYCLE_SECRET"]
    request = urllib.request.Request(
        f"{api}/operations/content-cycle",
        method="POST",
        headers={
            "X-Content-Cycle-Key": secret,
            "Content-Type": "application/json",
            "Content-Length": "0",
        },
        data=b"",
    )
    try:
        with urllib.request.urlopen(request, timeout=240) as response:
            response.read()
    except urllib.error.URLError as error:
        raise RuntimeError("Content cycle request failed.") from error
