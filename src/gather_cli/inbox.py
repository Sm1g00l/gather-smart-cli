import click
import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

URL = os.getenv("INBOX_URL", "")
KEY = os.getenv("INBOX_KEY", "")
TASKS_FILE = Path("tasks.json")

@click.group()
def cli():
    pass

@cli.command()
@click.option("--level", default=0, type=int)
def set(level):
    # SDK oficial: inbox.counter.set (número) ou inbox.activity (feed)
    payload = {"counter_action": "counter.set", "count": level}
    headers = {"Content-Type": "application/json", "X-API-Key": KEY}
    try:
        requests.post(URL, json=payload, headers=headers, timeout=5)
    except Exception:
        pass
    tasks = []
    if TASKS_FILE.exists():
        tasks = json.loads(TASKS_FILE.read_text())
    else:
        tasks = [{"msg":"inicial","level":level}]
    # Atualiza o nível da primeira tarefa para refletir no arquivo
    for t in tasks:
        t["level"] = level
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))
    click.echo(f"Inbox nível definido: {level} (SDK: counter.set)")

@cli.command()
@click.argument("message")
def add(message):
    # SDK oficial: inbox.activity.add (id, text, url?)
    payload = {"activity_action": "activity.add", "id": f"task-{len(message)}", "text": message[:500]}
    headers = {"Content-Type": "application/json", "X-API-Key": KEY}
    try:
        requests.post(URL, json=payload, headers=headers, timeout=5)
    except Exception:
        pass
    tasks = []
    if TASKS_FILE.exists():
        tasks = json.loads(TASKS_FILE.read_text())
    current_level = max([t.get("level", 0) for t in tasks]) if tasks else 0
    new_level = min(current_level + 1, 11)
    tasks.append({"msg": message, "id": payload["id"], "level": new_level})
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))
    click.echo(f"Tarefa adicionada (feed): {message} (SDK: activity.add)")

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
