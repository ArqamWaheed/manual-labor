"""Tiny stdlib HTTP helpers (keeps the core install light)."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any


def get_json(url: str, params: dict[str, Any] | None = None, timeout: float = 30) -> Any:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=timeout) as r:  # noqa: S310 (trusted endpoints)
        return json.loads(r.read())


def post_json(url: str, payload: dict[str, Any], timeout: float = 120) -> Any:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310
        return json.loads(r.read())


def post_form(url: str, form: dict[str, str], timeout: float = 30) -> tuple[int, Any]:
    """POST x-www-form-urlencoded; returns (status, json) without raising on 4xx."""
    req = urllib.request.Request(url, data=urllib.parse.urlencode(form).encode())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:  # type: ignore[attr-defined]
        return e.code, json.loads(e.read() or b"{}")
