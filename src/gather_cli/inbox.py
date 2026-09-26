import click
import requests
import hmac, hashlib, base64, time, json, os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

URL = os.getenv("INBOX_URL", "")
KEY = os.getenv("INBOX_KEY", "")
TASKS_FILE = Path("tasks.json")
OBJECT_ID = "22979152-f25d-4a92-b7c7-03c034b0496b"

def sign_standard(secret, webhook_id, payload_dict):
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    raw_body = json.dumps(payload_dict, separators=(",",":"))
    secret_stripped = secret[len("whsec_"):] if secret.startswith("whsec_") else secret
    try:
        secret_bytes = base64.b64decode(secret_stripped)
    except Exception:
        secret_bytes = secret_stripped.encode()
    signed_payload = f"{webhook_id}.{timestamp}.{raw_body}"
    sig_bytes = hmac.new(secret_bytes, signed_payload.encode(), hashlib.sha256).digest()
    sig = f"v1,{base64.b64encode(sig_bytes).decode()}"
    payload_dict["timestamp"] = timestamp
    return sig, timestamp, raw_body, payload_dict

@click.group()
def cli():
    pass

@cli.command()
@click.option("--level", default=0, type=int)
def set(level):
    payload_dict = {"type":"counter.set","data":{"count":level}}
    sig, ts, raw_body, pd = sign_standard(KEY, OBJECT_ID, payload_dict.copy())
    headers = {"Content-Type":"application/json","webhook-id":OBJECT_ID,"webhook-timestamp":ts,"webhook-signature":sig}
    try:
        resp = requests.post(URL, data=raw_body, headers=headers, timeout=10)
        if resp.status_code == 404:
            click.echo(f"Webhook 404 (endpoint inacessível); assinatura válida. Inbox nível: {level}")
        else:
            resp.raise_for_status()
            click.echo(f"Inbox nível definido: {level} (status: {resp.status_code})")
    except Exception as e:
        click.echo(f"Erro webhook: {e}")
    tasks = []
    if TASKS_FILE.exists():
        tasks = json.loads(TASKS_FILE.read_text())
    else:
        tasks = [{"msg":"inicial","level":level}]
    for t in tasks:
        t["level"] = level
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))

@cli.command()
@click.argument("message")
def add(message):
    payload_dict = {"type":"activity.add","data":{"id":f"task_{len(message)}","text":message[:500]}}
    sig, ts, raw_body, pd = sign_standard(KEY, OBJECT_ID, payload_dict.copy())
    headers = {"Content-Type":"application/json","webhook-id":OBJECT_ID,"webhook-timestamp":ts,"webhook-signature":sig}
    try:
        resp = requests.post(URL, data=raw_body, headers=headers, timeout=10)
        if resp.status_code == 404:
            click.echo(f"Webhook 404; assinatura válida. Tarefa adicionada (feed): {message}")
        else:
            resp.raise_for_status()
            click.echo(f"Tarefa adicionada (feed): {message} (status: {resp.status_code})")
    except Exception as e:
        click.echo(f"Erro webhook: {e}")
    tasks = []
    if TASKS_FILE.exists():
        tasks = json.loads(TASKS_FILE.read_text())
    current_level = max([t.get("level", 0) for t in tasks]) if tasks else 0
    new_level = min(current_level + 1, 11)
    tasks.append({"msg": message, "id": pd["data"]["id"], "level": new_level})
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))

@cli.command()
def list():
    if not TASKS_FILE.exists():
        click.echo("Nenhuma tarefa.")
        return
    tasks = json.loads(TASKS_FILE.read_text())
    for t in tasks:
        click.echo(f"ID: {t.get('id','-')} | Msg: {t.get('msg','-')} | Nível: {t.get('level','-')}")

if __name__ == "__main__":
    cli()
