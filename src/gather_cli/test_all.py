import click
import requests
import hmac, hashlib, base64, time, json, os, uuid
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

def get_secret(env_key):
    val = os.getenv(env_key, "")
    if val.startswith("whsec_"):
        stripped = val[len("whsec_"):]
        try:
            return base64.b64decode(stripped)
        except Exception:
            return stripped.encode()
    return val.encode()

def sign_payload(secret_bytes, webhook_id, payload_dict):
    timestamp = int(time.time())
    raw_body = json.dumps(payload_dict, separators=(",",":"))
    signed_content = f"{webhook_id}.{timestamp}.{raw_body}"
    sig_bytes = hmac.new(secret_bytes, signed_content.encode(), hashlib.sha256).digest()
    sig = f"v1,{base64.b64encode(sig_bytes).decode()}"
    payload_dict["timestamp"] = timestamp
    headers = {
        "Content-Type": "application/json",
        "webhook-id": webhook_id,
        "webhook-timestamp": str(timestamp),
        "webhook-signature": sig,
    }
    return headers, raw_body

OBJECTS = [
    ("Bot Monitor", "BOT_MONITOR_URL", "BOT_MONITOR_KEY", "status"),
    ("Lightbulb", "LIGHTBULB_URL", "LIGHTBULB_KEY", "switch"),
    ("Inbox", "INBOX_URL", "INBOX_KEY", "inbox"),
]

@click.group()
def cli():
    pass

@cli.command()
@click.option("--full", is_flag=True, help="Mostrar body completo da resposta")
def all(full):
    results = []
    for name, url_key, key_key, preset in OBJECTS:
        url = os.getenv(url_key, "")
        secret_raw = os.getenv(key_key, "")
        if not url or not secret_raw:
            click.echo(f"[SKIP] {name}: URL ou KEY faltando no .env")
            results.append((name, "SKIP", "URL ou KEY faltando"))
            continue
        if not secret_raw.startswith("whsec_"):
            click.echo(f"[ERRO] {name}: secret não começa com whsec_ (token inválido)")
            results.append((name, "ERRO", "secret não começa com whsec_"))
            continue
        secret_bytes = get_secret(key_key)
        webhook_id = str(uuid.uuid4())
        payload = {"type": "webhook.ping"}
        headers, raw_body = sign_payload(secret_bytes, webhook_id, payload.copy())
        try:
            resp = requests.post(url, data=raw_body, headers=headers, timeout=15)
            body_text = resp.text
            if resp.status_code == 200:
                # Tenta extrair capabilities do pong
                pong_info = "pong recebido"
                try:
                    pong_json = resp.json()
                    if "preset" in pong_json:
                        pong_info = f"preset={pong_json.get('preset')}, capabilities={pong_json.get('capabilities', [])}"
                except Exception:
                    pass
                click.echo(f"[OK] {name}: 200 | {pong_info}")
                results.append((name, "OK", pong_info))
            elif resp.status_code == 404:
                msg = body_text[:200]
                click.echo(f"[404] {name}: endpoint inacessível | body: {msg}")
                results.append((name, "404", msg))
            elif resp.status_code == 410:
                msg = body_text[:200]
                click.echo(f"[410] {name}: token_revoked | body: {msg}")
                results.append((name, "410", msg))
            elif resp.status_code == 400:
                msg = body_text[:200]
                click.echo(f"[400] {name}: invalid_request/args | body: {msg}")
                results.append((name, "400", msg))
            elif resp.status_code == 415:
                msg = body_text[:200]
                click.echo(f"[415] {name}: unsupported_media | body: {msg}")
                results.append((name, "415", msg))
            elif resp.status_code == 429:
                msg = body_text[:200]
                reset = resp.headers.get("RateLimit-Reset", "?")
                click.echo(f"[429] {name}: rate_limited (Reset={reset}) | body: {msg}")
                results.append((name, "429", msg))
            else:
                msg = body_text[:200]
                click.echo(f"[{resp.status_code}] {name}: {msg}")
                results.append((name, str(resp.status_code), msg))
        except Exception as e:
            click.echo(f"[EXCEÇÃO] {name}: {str(e)[:200]}")
            results.append((name, "EXCEÇÃO", str(e)[:200]))
    click.echo("\n=== RESUMO ===")
    for name, status, detail in results:
        click.echo(f"{name}: {status} ({detail})")

if __name__ == "__main__":
    cli()
