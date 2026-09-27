import click
import json
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from gather_cli.webhook import get_secret_bytes, sign_and_post

load_dotenv()

BOT_URL = os.getenv("BOT_MONITOR_URL", "")
BOT_KEY = os.getenv("BOT_MONITOR_KEY", "")
MESSAGES_FILE = Path("bot_messages.json")

@click.group()
def cli():
    pass

@cli.command()
def ping():
    secret = get_secret_bytes("BOT_MONITOR_KEY")
    url = os.getenv("BOT_MONITOR_URL", "")
    if not url or not secret:
        click.echo("Erro: BOT_MONITOR_URL ou BOT_MONITOR_KEY não configurados")
        return
    payload = {"type": "webhook.ping"}
    try:
        resp = sign_and_post(url, secret, payload)
        click.echo(f"Ping enviado (status: {resp.status_code})")
        click.echo(f"Response: {resp.text[:300]}")
    except Exception as e:
        click.echo(f"Erro no ping: {e}")

@cli.command()
@click.argument("message", required=False)
@click.option("--status", default="working", type=click.Choice(["timer", "on", "question", "alert", "working", "off"]))
def add(message, status):
    # "timer" não é um estado aceito pelo Gather (400 invalid_args); mantido como alias de "working"
    if status == "timer":
        status = "working"
    secret = get_secret_bytes("BOT_MONITOR_KEY")
    url = os.getenv("BOT_MONITOR_URL", "")
    if not url or not secret:
        click.echo("Erro: BOT_MONITOR_URL ou BOT_MONITOR_KEY não configurados")
        return
    payload = {"type": "status.set", "data": {"state": status}}
    try:
        if message:
            sign_and_post(url, secret, {"type": "activity.add", "data": {"id": f"msg_{uuid.uuid4().hex[:12]}", "text": message[:500]}})
        resp = sign_and_post(url, secret, payload)
        if resp.status_code == 404:
            click.echo(f"Webhook 404 (endpoint inacessível) — assinatura válida. Estado: {status}")
        elif resp.status_code == 200:
            click.echo(f"Bot Monitor atualizado: estado = {status}")
        else:
            click.echo(f"Bot Monitor — resposta: {resp.status_code} | {resp.text[:200]}")
    except Exception as e:
        click.echo(f"Erro webhook: {e}")
    messages = []
    if MESSAGES_FILE.exists():
        messages = json.loads(MESSAGES_FILE.read_text())
    msg_text = message or f"task: {status}"
    messages.append({"msg": msg_text, "status": status, "id": len(messages) + 1})
    if len(messages) > 5:
        messages = messages[-5:]
    MESSAGES_FILE.write_text(json.dumps(messages, indent=2))
    click.echo(f"Bot Monitor local: {msg_text} -> {status}")

@cli.command()
def clear():
    secret = get_secret_bytes("BOT_MONITOR_KEY")
    url = os.getenv("BOT_MONITOR_URL", "")
    if not url or not secret:
        click.echo("Erro: BOT_MONITOR_URL ou BOT_MONITOR_KEY não configurados")
        return
    try:
        resp = sign_and_post(url, secret, {"type": "activity.clear", "data": {}})
        click.echo(f"Bot Monitor: mensagens limpas (status: {resp.status_code})")
    except Exception as e:
        click.echo(f"Erro webhook: {e}")
    if MESSAGES_FILE.exists():
        MESSAGES_FILE.write_text(json.dumps([], indent=2))

@cli.command(name="list")
def list_messages():
    if not MESSAGES_FILE.exists():
        click.echo("Nenhuma mensagem registrada.")
        return
    messages = json.loads(MESSAGES_FILE.read_text())
    for m in messages:
        click.echo(f"ID: {m.get('id', '-')} | Status: {m.get('status', '-')} | Msg: {m.get('msg', '-')}")

if __name__ == "__main__":
    cli()