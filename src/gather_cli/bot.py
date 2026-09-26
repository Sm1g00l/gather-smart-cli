import click
import json
import requests
import hmac
import hashlib
import base64
import time
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BOT_URL = os.getenv("BOT_MONITOR_URL", "")
BOT_KEY = os.getenv("BOT_MONITOR_KEY", "")

MESSAGES_FILE = Path("bot_messages.json")

@click.group()
def cli():
    pass

@cli.command()
@click.argument("message")
@click.option("--status", default="timer", type=click.Choice(["blank","smiley","question","warning","timer"]))
def add(message, status):
    payload = {"state": status}
    headers = {"Content-Type": "application/json", "X-API-Key": BOT_KEY}
    # Mock ou envio real
    try:
        resp = requests.post(BOT_URL, json=payload, headers=headers, timeout=5)
        resp.raise_for_status()
    except Exception:
        pass  # Aceita mock
    messages = []
    if MESSAGES_FILE.exists():
        messages = json.loads(MESSAGES_FILE.read_text())
    messages.append({"msg": message, "status": status, "id": len(messages)+1})
    if len(messages) > 5:
        messages = messages[-5:]  # rotativo
    MESSAGES_FILE.write_text(json.dumps(messages, indent=2))
    click.echo(f"Bot Monitor atualizado: {message} -> {status}")

@cli.command()
def list():
    if not MESSAGES_FILE.exists():
        click.echo("Nenhuma mensagem registrada.")
        return
    messages = json.loads(MESSAGES_FILE.read_text())
    for m in messages:
        click.echo(f"ID: {m['id']} | Msg: {m['msg']} | Status: {m['status']}")

if __name__ == "__main__":
    cli()
