import click
import json
import os
import base64
import uuid
from pathlib import Path
from dotenv import load_dotenv
from gather_cli.webhook import get_secret_bytes, sign_and_post
from gather_cli.inbox_config import get_config

load_dotenv()

TASKS_FILE = Path("tasks.json")

_config_override = None

def set_config_override(path: Path):
    global _config_override
    _config_override = path

def clear_config_override():
    global _config_override
    _config_override = None

def _get_config():
    if _config_override:
        return get_config(_config_override)
    return get_config()

def _decode_secret(key: str) -> bytes:
    """Decode whsec_ secret from base64."""
    if key.startswith("whsec_"):
        stripped = key[len("whsec_"):]
        try:
            return base64.b64decode(stripped)
        except Exception:
            return stripped.encode()
    return key.encode()

def _resolve_inbox(target: str = None):
    config = _get_config()
    
    if target:
        inbox = config.get(target)
        if not inbox:
            raise click.ClickException(f"Inbox '{target}' não encontrado. Use 'gather-inbox config list' para ver disponíveis.")
        return inbox["url"], _decode_secret(inbox["key"])
    
    default_name = config.get_default()
    if default_name:
        inbox = config.get(default_name)
        if inbox:
            return inbox["url"], _decode_secret(inbox["key"])
    
    url = os.getenv("INBOX_URL", "")
    key = get_secret_bytes("INBOX_KEY")
    if not url or not key:
        raise click.ClickException("Nenhum inbox configurado. Use 'gather-inbox config add' ou configure INBOX_URL/INBOX_KEY no .env")
    return url, key

@click.group()
def cli():
    pass

@cli.group(name="config")
def config_group():
    """Gerenciar inboxes salvos (multi-inbox)."""
    pass

@config_group.command("add")
@click.argument("name")
@click.option("--url", required=True, help="Webhook URL do inbox")
@click.option("--key", required=True, help="Signing secret (whsec_...)")
@click.option("--owner", default="", help="Nome do dono do inbox")
def config_add(name, url, key, owner):
    config = _get_config()
    config.add(name, url, key, owner)
    click.echo(f"Inbox '{name}' adicionado.")

@config_group.command("list")
def config_list():
    config = _get_config()
    inboxes = config.list()
    if not inboxes:
        click.echo("Nenhum inbox configurado.")
        return
    default = config.get_default()
    for name, inbox in inboxes.items():
        marker = " (default)" if name == default else ""
        click.echo(f"  {name}{marker}: {inbox['owner']} - {inbox['url']} - key: {inbox['key']}")

@config_group.command("remove")
@click.argument("name")
def config_remove(name):
    config = _get_config()
    config.remove(name)
    click.echo(f"Inbox '{name}' removido.")

@config_group.command("default")
@click.argument("name")
def config_default(name):
    config = _get_config()
    try:
        config.set_default(name)
        click.echo(f"Inbox '{name}' definido como default.")
    except ValueError as e:
        raise click.ClickException(str(e))

@cli.command()
@click.option("--level", default=0, type=int)
def set(level):
    url, secret = _resolve_inbox()
    payload = {"type": "counter.set", "data": {"count": level}}
    try:
        resp = sign_and_post(url, secret, payload)
        if resp.status_code == 404:
            click.echo(f"Webhook 404 (endpoint inacessível). Inbox nível: {level}")
        else:
            click.echo(f"Inbox nível definido: {level} (status: {resp.status_code})")
    except Exception as e:
        click.echo(f"Erro webhook: {e}")
    tasks = []
    if TASKS_FILE.exists():
        tasks = json.loads(TASKS_FILE.read_text())
    else:
        tasks = [{"msg": "inicial", "level": level}]
    for t in tasks:
        t["level"] = level
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))

@cli.command()
@click.argument("message")
@click.option("--to", "target", default=None, help="Enviar para inbox específico (nome salvo no config)")
def add(message, target):
    url, secret = _resolve_inbox(target)
    payload = {"type": "activity.add", "data": {"id": f"task_{uuid.uuid4().hex[:12]}", "text": message[:500]}}
    try:
        resp = sign_and_post(url, secret, payload)
        if resp.status_code == 404:
            click.echo(f"Webhook 404. Tarefa adicionada: {message}")
        else:
            click.echo(f"Tarefa adicionada: {message} (status: {resp.status_code})")
    except Exception as e:
        click.echo(f"Erro webhook: {e}")
    tasks = []
    if TASKS_FILE.exists():
        tasks = json.loads(TASKS_FILE.read_text())
    tasks.append({"msg": message, "id": payload["data"]["id"], "level": max([t.get("level", 0) for t in tasks] or [0]) + 1})
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))

@cli.command()
@click.argument("task_id")
def remove(task_id):
    url, secret = _resolve_inbox()
    payload = {"type": "activity.remove", "data": {"id": task_id}}
    try:
        resp = sign_and_post(url, secret, payload)
        if resp.status_code == 404:
            click.echo(f"Webhook 404 (endpoint inacessível). Removido: {task_id}")
        else:
            click.echo(f"Tarefa removida: {task_id} (status: {resp.status_code})")
    except Exception as e:
        click.echo(f"Erro webhook: {e}")
    if TASKS_FILE.exists():
        tasks = json.loads(TASKS_FILE.read_text())
        tasks = [t for t in tasks if t.get("id") != task_id]
        TASKS_FILE.write_text(json.dumps(tasks, indent=2))

@cli.command()
def clear():
    url, secret = _resolve_inbox()
    payload = {"type": "activity.clear", "data": {}}
    try:
        resp = sign_and_post(url, secret, payload)
        if resp.status_code == 404:
            click.echo(f"Webhook 404 (endpoint inacessível). Inbox limpo")
        else:
            click.echo(f"Inbox limpo (status: {resp.status_code})")
    except Exception as e:
        click.echo(f"Erro webhook: {e}")
    if TASKS_FILE.exists():
        TASKS_FILE.write_text(json.dumps([], indent=2))

@cli.command(name="list")
def list_tasks():
    if not TASKS_FILE.exists():
        click.echo("Nenhuma tarefa.")
        return
    tasks = json.loads(TASKS_FILE.read_text())
    for t in tasks:
        click.echo(f"ID: {t.get('id', '-')} | Msg: {t.get('msg', '-')} | Nível: {t.get('level', '-')}")

if __name__ == "__main__":
    cli()