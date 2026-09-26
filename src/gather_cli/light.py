import click
import os
from dotenv import load_dotenv
from gather_cli.webhook import get_secret_bytes, sign_and_post

load_dotenv()

@click.group()
def cli():
    pass

@cli.command()
@click.option("--color", default="green", type=click.Choice(["green", "red", "yellow"]))
def on(color):
    url = os.getenv("LIGHTBULB_URL", "")
    secret = get_secret_bytes("LIGHTBULB_KEY")
    if not url or not secret:
        click.echo("Erro: LIGHTBULB_URL ou LIGHTBULB_KEY não configurados")
        return
    payload = {"type": "switch.set_state", "data": {"on": True}, "variant_color": color}
    try:
        resp = sign_and_post(url, secret, payload)
        if resp.status_code == 404:
            click.echo(f"Webhook 404 (endpoint inacessível). Lightbulb {color} -> ON")
        else:
            click.echo(f"Lightbulb {color} -> ON (status: {resp.status_code})")
    except Exception as e:
        click.echo(f"Erro webhook: {e}")

@cli.command()
@click.option("--color", default="green", type=click.Choice(["green", "red", "yellow"]))
def off(color):
    url = os.getenv("LIGHTBULB_URL", "")
    secret = get_secret_bytes("LIGHTBULB_KEY")
    if not url or not secret:
        click.echo("Erro: LIGHTBULB_URL ou LIGHTBULB_KEY não configurados")
        return
    payload = {"type": "switch.set_state", "data": {"on": False}, "variant_color": color}
    try:
        resp = sign_and_post(url, secret, payload)
        if resp.status_code == 404:
            click.echo(f"Webhook 404. Lightbulb {color} -> OFF")
        else:
            click.echo(f"Lightbulb {color} -> OFF (status: {resp.status_code})")
    except Exception as e:
        click.echo(f"Erro webhook: {e}")

if __name__ == "__main__":
    cli()
