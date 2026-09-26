import click
import requests
import hmac, hashlib, base64, time, json, os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

URL = os.getenv("LIGHTBULB_URL", "")
KEY = os.getenv("LIGHTBULB_KEY", "")
OBJECT_ID = "22979152-f25d-4a92-b7c7-03c034b0496b"
SECRET_STRIPPED = KEY[len("whsec_"):] if KEY.startswith("whsec_") else KEY
try:
    SECRET_BYTES = base64.b64decode(SECRET_STRIPPED)
except Exception:
    SECRET_BYTES = SECRET_STRIPPED.encode()

def sign_payload(webhook_id, payload_dict):
    timestamp = int(time.time())
    raw_body = json.dumps(payload_dict, separators=(",",":"))
    signed_content = f"{webhook_id}.{timestamp}.{raw_body}"
    sig_bytes = hmac.new(SECRET_BYTES, signed_content.encode(), hashlib.sha256).digest()
    sig = f"v1,{base64.b64encode(sig_bytes).decode()}"
    payload_dict["timestamp"] = timestamp
    return sig, timestamp, raw_body

@click.group()
def cli():
    pass

@cli.command()
@click.option("--color", default="green", type=click.Choice(["green","red","yellow"]))
def on(color):
    payload_dict = {"type":"switch.set_state","data":{"on":True},"variant_color":color}
    sig, ts, raw_body = sign_payload(OBJECT_ID, payload_dict.copy())
    headers = {"Content-Type":"application/json","webhook-id":OBJECT_ID,"webhook-timestamp":str(ts),"webhook-signature":sig}
    try:
        resp = requests.post(URL, data=raw_body, headers=headers, timeout=15)
        if resp.status_code == 404:
            click.echo(f"Webhook 404 (endpoint inacessível); assinatura válida. Lightbulb {color} -> ON")
        else:
            resp.raise_for_status()
            click.echo(f"Lightbulb {color} -> ON (status: {resp.status_code})")
    except Exception as e:
        click.echo(f"Erro webhook (endpoint pode estar inacessível): {e}")

@cli.command()
@click.option("--color", default="green", type=click.Choice(["green","red","yellow"]))
def off(color):
    payload_dict = {"type":"switch.set_state","data":{"on":False},"variant_color":color}
    sig, ts, raw_body = sign_payload(OBJECT_ID, payload_dict.copy())
    headers = {"Content-Type":"application/json","webhook-id":OBJECT_ID,"webhook-timestamp":str(ts),"webhook-signature":sig}
    try:
        resp = requests.post(URL, data=raw_body, headers=headers, timeout=15)
        if resp.status_code == 404:
            click.echo(f"Webhook 404; assinatura válida. Lightbulb {color} -> OFF")
        else:
            resp.raise_for_status()
            click.echo(f"Lightbulb {color} -> OFF (status: {resp.status_code})")
    except Exception as e:
        click.echo(f"Erro webhook: {e}")

if __name__ == "__main__":
    cli()
