import hashlib
import hmac
import base64
import time
import json
import uuid
import os
import requests
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

MESSAGES_FILE = Path("bot_messages.json")

def get_secret_bytes(env_key: str) -> bytes:
    val = os.getenv(env_key, "")
    if val.startswith("whsec_"):
        stripped = val[len("whsec_"):]
        try:
            return base64.b64decode(stripped)
        except Exception:
            return stripped.encode()
    return val.encode()

def sign_and_post(url: str, secret_bytes: bytes, payload: dict) -> requests.Response:
    webhook_id = str(uuid.uuid4())
    unix_ts = int(time.time())
    
    # Clone payload e adiciona timestamp ISO-8601 para eventos não-ping
    body_payload = payload.copy()
    if payload.get("type") != "webhook.ping":
        iso_ts = datetime.fromtimestamp(unix_ts, tz=timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
        body_payload["timestamp"] = iso_ts
    
    raw_body = json.dumps(body_payload, separators=(",", ":"))
    signed_content = f"{webhook_id}.{unix_ts}.{raw_body}"
    sig_bytes = hmac.new(secret_bytes, signed_content.encode(), hashlib.sha256).digest()
    signature = f"v1,{base64.b64encode(sig_bytes).decode()}"
    headers = {
        "Content-Type": "application/json",
        "webhook-id": webhook_id,
        "webhook-timestamp": str(unix_ts),
        "webhook-signature": signature,
    }
    return requests.post(url, data=raw_body, headers=headers, timeout=15)

def rate_limit_info(resp: requests.Response) -> dict:
    """Headers de rate limit do Gather (60 req/min por space).

    Em toda resposta: ratelimit-limit, ratelimit-remaining, ratelimit-policy ("60;w=60").
    No 429: retry-after (segundos). RateLimit-Reset é exposto via CORS mas não vem.
    """
    def as_int(name):
        val = resp.headers.get(name, "")
        return int(val) if val.strip().isdigit() else None

    info = {
        "limit": as_int("RateLimit-Limit"),
        "remaining": as_int("RateLimit-Remaining"),
        "policy": resp.headers.get("RateLimit-Policy"),
        "retry_after": as_int("Retry-After"),
    }
    if info["retry_after"] is None:
        info["retry_after"] = as_int("RateLimit-Reset")
    return info
