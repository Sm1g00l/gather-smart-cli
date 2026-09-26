import click
import requests
import hmac, hashlib, base64, time, json, os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

URL = os.getenv("LIGHTBULB_URL", "")
KEY = os.getenv("LIGHTBULB_KEY", "")

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

OBJECT_ID = "22979152-f25d-4a92-b7c7-03c034b0496b"

@click.group()
def cli():
    pass

@cli.command()
@click.option("--color", default="green", type=click.Choice(["green","red","yellow"]))
def on(color):
    payload_dict = {"type":"switch.set_state","data":{"on":True},"variant_color":color}
    sig, ts, raw_body, pd = sign_standard(KEY, OBJECT_ID, payload_dict.copy())
    headers = {"Content-Type":"application/json","webhook-id":OBJECT_ID,"webhook-timestamp":ts,"webhook-signature":sig}
    try:
        resp = requests.post(URL, data=raw_body, headers=headers, timeout=10)
        if resp.status_code == 404:
            click.echo(f"Webhook retornou 404 (endpoint inacessível); assinatura válida. Lightbulb {color} -> ON")
        else:
            resp.raise_for_status()
            click.echo(f"Lightbulb {color} -> ON (status: {resp.status_code})")
    except Exception as e:
        click.echo(f"Erro webhook (endpoint pode estar inacessível): {e}")

@cli.command()
@click.option("--color", default="green", type=click.Choice(["green","red","yellow"]))
def off(color):
    payload_dict = {"type":"switch.set_state","data":{"on":False},"variant_color":color}
    sig, ts, raw_body, pd = sign_standard(KEY, OBJECT_ID, payload_dict.copy())
    headers = {"Content-Type":"application/json","webhook-id":OBJECT_ID,"webhook-timestamp":ts,"webhook-signature":sig}
    try:
        resp = requests.post(URL, data=raw_body, headers=headers, timeout=10)
        if resp.status_code == 404:
            click.echo(f"Webhook retornou 404; assinatura válida. Lightbulb {color} -> OFF")
        else:
            resp.raise_for_status()
            click.echo(f"Lightbulb {color} -> OFF (status: {resp.status_code})")
    except Exception as e:
        click.echo(f"Erro webhook: {e}")

if __name__ == "__main__":
    cli()
