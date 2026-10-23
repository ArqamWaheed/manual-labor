"""Auth0 for AI Agents: CIBA (asynchronous authorization) before the only outbound action.

Docs: https://auth0.com/ai/docs/intro/asynchronous-authorization
G8 gate: confirm the exact login_hint format and that the CIBA grant is enabled for the app.
"""
from __future__ import annotations

import json
import time

from manual_labor.config import settings
from manual_labor.net import post_form


def request_approval(binding_message: str, timeout_s: int = 300) -> bool:
    s = settings()
    base = f"https://{s.auth0_domain}"
    status, req = post_form(f"{base}/bc-authorize", {
        "client_id": s.auth0_client_id,
        "client_secret": s.auth0_client_secret,
        "scope": "openid",
        "binding_message": binding_message[:64],  # shown on the phone; keep it short and exact
        "login_hint": json.dumps({"format": "iss_sub", "iss": f"{base}/", "sub": s.auth0_user_sub}),
    })
    if status != 200:
        raise RuntimeError(f"bc-authorize failed: {status} {req}")
    deadline = time.time() + min(timeout_s, int(req.get("expires_in", timeout_s)))
    while time.time() < deadline:
        time.sleep(int(req.get("interval", 5)))
        code, tok = post_form(f"{base}/oauth/token", {
            "grant_type": "urn:openid:params:grant-type:ciba",
            "auth_req_id": req["auth_req_id"],
            "client_id": s.auth0_client_id,
            "client_secret": s.auth0_client_secret,
        })
        if code == 200:
            return True                       # approved on the phone
        if tok.get("error") == "slow_down":
            time.sleep(5)
        elif tok.get("error") != "authorization_pending":
            return False                      # access_denied, expired_token, ...
    return False
