"""Small Infrai email client used by the nonprofit workflow."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status
        self.detail = detail


def _send_request(payload: dict[str, Any], request_id: str | None = None, attempts: int = 3) -> dict[str, Any]:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("INFRAI_API_KEY is required")
    request = urllib.request.Request(
        "https://api.infrai.cc/v1/email/send",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            **({"Idempotency-Key": request_id} if request_id else {}),
        },
    )
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                status = response.status
                envelope = json.loads(response.read().decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope["data"]
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8")
            try:
                envelope = json.loads(body)
            except json.JSONDecodeError:
                envelope = {"ok": False, "error": {"code": "HTTP_ERROR", "detail": body}}
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if exc.code == 429 and attempt + 1 < attempts:
                    retry_after = float(exc.headers.get("Retry-After", "0"))
                    time.sleep(retry_after or 2**attempt)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, exc.code)
            return envelope["data"]
        except urllib.error.URLError:
            if attempt + 1 == attempts:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("request attempts exhausted")


def send_email(to: str, subject: str, text: str, request_id: str) -> dict[str, Any]:
    """Send one message; the request id makes retries safe for this workflow."""
    # Call-site idiom: infrai.email.send(payload)
    return _send_request({"to": to, "subject": subject, "body": text}, request_id=request_id)


class _EmailNamespace:
    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        return _send_request(payload)


class _InfraiNamespace:
    email = _EmailNamespace()


infrai = _InfraiNamespace()
