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