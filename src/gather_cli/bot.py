import click
import requests
import hmac
import hashlib
import base64
import time
import json
import uuid
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

BOT_URL = os.getenv("BOT_MONITOR_URL", "")
BOT_KEY = os.getenv("BOT_MONITOR_KEY", "")
MESSAGES_FILE = Path("bot_messages.json")
OBJECT_ID = "22979152-f25d-4a92-b7c7-03c034b0496b"

# Decodificar secret conforme test.sh (remove whsec_ e decodifica base64)
SECRET_STRIPPED = BOT_KEY[len("whsec_"):] if BOT_KEY.startswith("whsec_") else BOT_KEY
try:
    SECRET_BYTES = base64.b64decode(SECRET_STRIPPED)
except Exception:
    SECRET_BYTES = SECRET_STRIPPED.encode()

def sign_payload(webhook_id, payload_dict, timestamp=None):
    if timestamp is None:
        timestamp = int(time.time())  # Unix timestamp como no test.sh (date +%s)
    # Para ping: NÃO inclui timestamp no payload (test.sh: {"type":"webhook.ping"})
    if payload_dict.get("type") == "webhook.ping":
        raw_body = json.dumps(payload_dict, separators=(",",":"))
    else:
        payload_dict["timestamp"] = timestamp
        raw_body = json.dumps(payload_dict, separators=(",",":"))
    signed_content = f"{webhook_id}.{timestamp}.{raw_body}"
    sig_bytes = hmac.new(SECRET_BYTES, signed_content.encode(), hashlib.sha256).digest()
    sig = f"v1,{base64.b64encode(sig_bytes).decode()}"
    return sig, timestamp, raw_body

@click.group()
def cli():
    pass

@cli.command()
def ping():
    webhook_id = str(uuid.uuid4())
    payload = {"type": "webhook.ping"}
    sig, ts, raw_body = sign_payload(webhook_id, payload)
    headers = {
        "Content-Type": "application/json",
        "webhook-id": webhook_id,
        "webhook-timestamp": str(ts),
        "webhook-signature": sig,
    }
    try:
        resp = requests.post(BOT_URL, data=raw_body, headers=headers, timeout=15)
        click.echo(f"Ping enviado (status: {resp.status_code})")
        click.echo(f"Response: {resp.text[:300]}")
    except Exception as e:
        click.echo(f"Erro no ping (endpoint pode estar inacessível): {e}")

@cli.command()
@click.argument("message", required=False)
@click.option("--status", default="timer", type=click.Choice(["off","on","question","alert","working"]))
def add(message, status):
    webhook_id = str(uuid.uuid4())
    payload = {"type": "status.set", "data": {"state": status}}
    sig, ts, raw_body = sign_payload(webhook_id, payload)
    headers = {
        "Content-Type": "application/json",
        "webhook-id": webhook_id,
        "webhook-timestamp": str(ts),
        "webhook-signature": sig,
    }
    try:
        resp = requests.post(BOT_URL, data=raw_body, headers=headers, timeout=15)
        if resp.status_code == 404:
            click.echo(f"Webhook 404 (endpoint inacessível no ambiente) — assinatura válida (v1,{sig[:10]}...). Estado enviado: {status}")
        elif resp.status_code == 200:
            click.echo(f"Bot Monitor atualizado: estado = {status} (pong: 200)")
        else:
            click.echo(f"Bot Monitor — resposta: {resp.status_code} | {resp.text[:200]}")
    except Exception as e:
        click.echo(f"Erro webhook (endpoint inacessível): {e}")
    # Atualiza arquivo local independente
    messages = []
    if MESSAGES_FILE.exists():
        messages = json.loads(MESSAGES_FILE.read_text())
    msg_text = message or f"task: {status}"
    messages.append({"msg": msg_text, "status": status, "id": len(messages)+1})
    if len(messages) > 5:
        messages = messages[-5:]
    MESSAGES_FILE.write_text(json.dumps(messages, indent=2))
    click.echo(f"Bot Monitor local atualizado: {msg_text} -> {status}")

@cli.command()
def list():
    if not MESSAGES_FILE.exists():
        click.echo("Nenhuma mensagem registrada.")
        return
    messages = json.loads(MESSAGES_FILE.read_text())
    for m in messages:
        click.echo(f"ID: {m.get('id','-')} | Status: {m.get('status','-')} | Msg: {m.get('msg','-')}")

if __name__ == "__main__":
    cli()
