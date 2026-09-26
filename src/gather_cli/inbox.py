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
    payload = {"level": level}
    headers = {"Content-Type": "application/json", "X-API-Key": KEY}
    try:
        requests.post(URL, json=payload, headers=headers, timeout=5)
    except Exception:
        pass
    # Atualiza tarefas locais se arquivo existe
    tasks = []
    if TASKS_FILE.exists():
        tasks = json.loads(TASKS_FILE.read_text())
        for t in tasks:
            if t.get("level", 0) > 11:
                t["level"] = 11
    else:
        tasks = [{"msg":"inicial","level":level}]
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))
    click.echo(f"Inbox nível definido: {level}")

@cli.command()
@click.argument("message")
def add(message):
    tasks = []
    if TASKS_FILE.exists():
        tasks = json.loads(TASKS_FILE.read_text())
    current_level = max([t.get("level", 0) for t in tasks]) if tasks else 0
    new_level = min(current_level + 1, 11)
    tasks.append({"msg": message, "level": new_level})
    payload = {"level": new_level}
    headers = {"Content-Type": "application/json", "X-API-Key": KEY}
    try:
        requests.post(URL, json=payload, headers=headers, timeout=5)
    except Exception:
        pass
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))
    click.echo(f"Tarefa adicionada: {message} (nível {new_level})")

@cli.command()
def list():
    if not TASKS_FILE.exists():
        click.echo("Nenhuma tarefa.")
        return
    tasks = json.loads(TASKS_FILE.read_text())
    for t in tasks:
        click.echo(f"Msg: {t['msg']} | Nível: {t['level']}")

if __name__ == "__main__":
    cli()
