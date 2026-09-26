import click
import requests
import os
from dotenv import load_dotenv
load_dotenv()

URL = os.getenv("LIGHTBULB_URL", "")
KEY = os.getenv("LIGHTBULB_KEY", "")

@click.group()
def cli():
    pass

@cli.command()
@click.option("--color", default="green", type=click.Choice(["green","red","yellow"]))
def on(color):
    payload = {"variation": color, "state": "on"}
    headers = {"Content-Type": "application/json", "X-API-Key": KEY}
    try:
        requests.post(URL, json=payload, headers=headers, timeout=5)
    except Exception:
        pass
    click.echo(f"Lightbulb {color} -> ON")

@cli.command()
@click.option("--color", default="green", type=click.Choice(["green","red","yellow"]))
def off(color):
    payload = {"variation": color, "state": "off"}
    headers = {"Content-Type": "application/json", "X-API-Key": KEY}
    try:
        requests.post(URL, json=payload, headers=headers, timeout=5)
    except Exception:
        pass
    click.echo(f"Lightbulb {color} -> OFF")

if __name__ == "__main__":
    cli()
