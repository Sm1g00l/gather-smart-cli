import click
import os
from pathlib import Path
from dotenv import load_dotenv

@click.command()
@click.option('--bot-url', prompt=True, help='Webhook URL do Bot Monitor')
@click.option('--bot-key', prompt=True, hide_input=True, help='API Key do Bot Monitor')
@click.option('--light-url', prompt=True, help='Webhook URL da Lightbulb')
@click.option('--light-key', prompt=True, hide_input=True, help='API Key da Lightbulb')
@click.option('--inbox-url', prompt=True, help='Webhook URL do Inbox')
@click.option('--inbox-key', prompt=True, hide_input=True, help='API Key do Inbox')
def setup(bot_url, bot_key, light_url, light_key, inbox_url, inbox_key):
    env_path = Path(".env")
    lines = [
        f"BOT_MONITOR_URL={bot_url}",
        f"BOT_MONITOR_KEY={bot_key}",
        f"LIGHTBULB_URL={light_url}",
        f"LIGHTBULB_KEY={light_key}",
        f"INBOX_URL={inbox_url}",
        f"INBOX_KEY={inbox_key}",
    ]
    env_path.write_text("\n".join(lines) + "\n")
    click.echo("Setup concluído. .env criado.")

if __name__ == '__main__':
    setup()
