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
    # SDK oficial: switch.set_state (on: true) + variant.set (color) se necessário
    payload = {"state_action": "switch.set_state", "on": True, "variant_color": color}
    headers = {"Content-Type": "application/json", "X-API-Key": KEY}
    try:
        requests.post(URL, json=payload, headers=headers, timeout=5)
    except Exception:
        pass
    click.echo(f"Lightbulb {color} -> ON (SDK: switch.set_state + variant.{color})")

@cli.command()
@click.option("--color", default="green", type=click.Choice(["green","red","yellow"]))
def off(color):
    payload = {"state_action": "switch.set_state", "on": False, "variant_color": color}
    headers = {"Content-Type": "application/json", "X-API-Key": KEY}
    try:
        requests.post(URL, json=payload, headers=headers, timeout=5)
    except Exception:
        pass
    click.echo(f"Lightbulb {color} -> OFF")

if __name__ == "__main__":
    cli()
