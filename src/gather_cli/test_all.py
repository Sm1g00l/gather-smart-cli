import click
import os
from dotenv import load_dotenv
from gather_cli.webhook import get_secret_bytes, rate_limit_info, sign_and_post

load_dotenv()

OBJECTS = [
    ("Bot Monitor", "BOT_MONITOR_URL", "BOT_MONITOR_KEY"),
    ("Lightbulb", "LIGHTBULB_URL", "LIGHTBULB_KEY"),
    ("Inbox", "INBOX_URL", "INBOX_KEY"),
]

@click.group()
def cli():
    pass

@cli.command()
@click.option("--full", is_flag=True, help="Mostrar body completo da resposta")
def all(full):
    results = []
    last_rl = None
    for name, url_key, key_key in OBJECTS:
        url = os.getenv(url_key, "")
        secret_raw = os.getenv(key_key, "")
        if not url or not secret_raw:
            click.echo(f"[SKIP] {name}: URL ou KEY faltando no .env")
            results.append((name, "SKIP", "URL ou KEY faltando"))
            continue
        if not secret_raw.startswith("whsec_"):
            click.echo(f"[ERRO] {name}: secret não começa com whsec_")
            results.append((name, "ERRO", "secret inválido"))
            continue
        secret = get_secret_bytes(key_key)
        payload = {"type": "webhook.ping"}
        try:
            resp = sign_and_post(url, secret, payload)
            last_rl = rate_limit_info(resp)
            if resp.status_code == 200:
                pong_info = "pong recebido"
                try:
                    pong_json = resp.json()
                    if "preset" in pong_json:
                        pong_info = f"preset={pong_json.get('preset')}, capabilities={pong_json.get('capabilities', [])}"
                except Exception:
                    pass
                click.echo(f"[OK] {name}: 200 | {pong_info}")
                results.append((name, "OK", pong_info))
            elif resp.status_code == 404:
                msg = resp.text[:200]
                click.echo(f"[404] {name}: endpoint inacessível | {msg}")
                results.append((name, "404", msg))
            elif resp.status_code == 410:
                msg = resp.text[:200]
                click.echo(f"[410] {name}: token_revoked | {msg}")
                results.append((name, "410", msg))
            elif resp.status_code == 400:
                msg = resp.text[:200]
                click.echo(f"[400] {name}: invalid_request | {msg}")
                results.append((name, "400", msg))
            elif resp.status_code == 429:
                msg = resp.text[:200]
                retry = rate_limit_info(resp)["retry_after"]
                click.echo(f"[429] {name}: rate_limited (Retry-After={retry if retry is not None else '?'}s) | {msg}")
                results.append((name, "429", msg))
            else:
                msg = resp.text[:200]
                click.echo(f"[{resp.status_code}] {name}: {msg}")
                results.append((name, str(resp.status_code), msg))
        except Exception as e:
            click.echo(f"[EXCEÇÃO] {name}: {str(e)[:200]}")
            results.append((name, "EXCEÇÃO", str(e)[:200]))
    if last_rl and last_rl["remaining"] is not None:
        click.echo(f"\nRate limit: {last_rl['remaining']}/{last_rl['limit']} restantes (policy {last_rl['policy']})")
    click.echo("\n=== RESUMO ===")
    for name, status, detail in results:
        click.echo(f"{name}: {status} ({detail})")

if __name__ == "__main__":
    cli()
