import click
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from gather_cli.webhook import get_secret_bytes, sign_and_post

load_dotenv()

TASKS_FILE = Path("tasks.json")

@click.group()
def cli():
    pass

@cli.command()
@click.option("--level", default=0, type=int)
def set(level):
    url = os.getenv("INBOX_URL", "")
    secret = get_secret_bytes("INBOX_KEY")
    if not url or not secret:
        click.echo("Erro: INBOX_URL ou INBOX_KEY não configurados")
        return
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
def add(message):
    url = os.getenv("INBOX_URL", "")
    secret = get_secret_bytes("INBOX_KEY")
    if not url or not secret:
        click.echo("Erro: INBOX_URL ou INBOX_KEY não configurados")
        return
    payload = {"type": "activity.add", "data": {"id": f"task_{len(message)}", "text": message[:500]}}
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
    url = os.getenv("INBOX_URL", "")
    secret = get_secret_bytes("INBOX_KEY")
    if not url or not secret:
        click.echo("Erro: INBOX_URL ou INBOX_KEY não configurados")
        return
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
    url = os.getenv("INBOX_URL", "")
    secret = get_secret_bytes("INBOX_KEY")
    if not url or not secret:
        click.echo("Erro: INBOX_URL ou INBOX_KEY não configurados")
        return
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