"""Testes de ponta a ponta contra os Smart Objects reais do Gather (sem mocks).

Desligados por padrão. Para rodar:  GATHER_E2E=1 pytest -m e2e -v
Usam as credenciais do .env do repo e, no fim, restauram o estado que os
objetos tinham antes (atividades, estado, cor, lâmpada, contador).
"""
import os
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from click.testing import CliRunner
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from gather_cli import bot, inbox, light
from gather_cli.webhook import get_secret_bytes, rate_limit_info, sign_and_post

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(os.getenv("GATHER_E2E") != "1", reason="e2e desligado (use GATHER_E2E=1)"),
]

OBJECTS = {
    "bot": ("BOT_MONITOR_URL", "BOT_MONITOR_KEY"),
    "light": ("LIGHTBULB_URL", "LIGHTBULB_KEY"),
    "inbox": ("INBOX_URL", "INBOX_KEY"),
}


def post(obj, payload):
    """Envia direto ao webhook (sign_and_post já segura a execução em 429 via Retry-After)."""
    url_env, key_env = OBJECTS[obj]
    return sign_and_post(os.getenv(url_env, ""), get_secret_bytes(key_env), payload)


def send(obj, payload):
    resp = post(obj, payload)
    assert resp.status_code == 200, f"{payload['type']} {obj}: {resp.status_code} {resp.text[:200]}"


def state(obj):
    resp = post(obj, {"type": "webhook.ping"})
    assert resp.status_code == 200, f"ping {obj}: {resp.status_code} {resp.text[:200]}"
    return resp.json()["capabilities"]


def wait_for(obj, check, timeout=5.0):
    """O webhook responde 'dispatched'; espera o estado refletir a mudança."""
    deadline = time.time() + timeout
    while True:
        caps = state(obj)
        if check(caps) or time.time() > deadline:
            return caps
        time.sleep(0.5)


def entries(caps):
    return caps.get("activity", {}).get("entries", [])


def restore_activity(obj, saved):
    send(obj, {"type": "activity.clear", "data": {}})
    for e in saved:
        send(obj, {"type": "activity.add", "data": {"id": e["id"], "text": e["text"]}})


@pytest.fixture(scope="module", autouse=True)
def snapshot_and_restore():
    for url_env, key_env in OBJECTS.values():
        if not os.getenv(url_env) or not os.getenv(key_env):
            pytest.skip(f"{url_env}/{key_env} ausentes no .env")
    # Cota do space: se não sobra o suficiente para a suíte (~62 req; o que passar da cota a CLI espera via Retry-After), espera a janela virar
    probe = post("bot", {"type": "webhook.ping"})
    rl = rate_limit_info(probe)
    if rl["remaining"] is not None and rl["remaining"] < 55:
        window = int((rl["policy"] or "60;w=60").split("w=")[-1])
        time.sleep(window)
    before = {obj: state(obj) for obj in OBJECTS}
    yield before
    b, l, i = before["bot"], before["light"], before["inbox"]
    restore_activity("bot", entries(b))
    send("bot", {"type": "status.set", "data": {"state": b["status"]["state"]}})
    send("bot", {"type": "variant.set", "data": {"color": b["variant"]["color"]}})
    send("light", {"type": "variant.set", "data": {"color": l["variant"]["color"]}})
    send("light", {"type": "switch.set_state", "data": {"on": l["switch"]["on"]}})
    restore_activity("inbox", entries(i))
    send("inbox", {"type": "counter.set", "data": {"count": i["counter"]["count"]}})

    # Confere a restauração (o "at" das atividades muda; o resto tem que bater)
    def comparable(caps):
        c = dict(caps)
        if "activity" in c:
            c["activity"] = [(e["id"], e["text"]) for e in entries(c)]
        return c

    for obj, caps in before.items():
        after = wait_for(obj, lambda c: comparable(c) == comparable(caps))
        assert comparable(after) == comparable(caps), f"{obj} não voltou ao estado original"


@pytest.fixture
def runner(tmp_path):
    # Isola os arquivos locais (bot_messages.json/tasks.json) e o config multi-inbox
    inbox.set_config_override(tmp_path / "inboxes.json")
    r = CliRunner()
    with r.isolated_filesystem(temp_dir=tmp_path):
        yield r
    inbox.clear_config_override()


def run(runner, cli, args):
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.output
    return result.output


# --- Bot Monitor -----------------------------------------------------------

def test_gather_rejects_raw_timer_state():
    # Contrato do Gather que motivou o alias timer -> working na CLI
    resp = post("bot", {"type": "status.set", "data": {"state": "timer"}})
    assert resp.status_code == 400


def test_bot_add_timer_alias_reaches_gather(runner):
    out = run(runner, bot.cli, ["add", "e2e timer alias", "--status", "timer"])
    assert "400" not in out
    caps = wait_for("bot", lambda c: c["status"]["state"] == "working"
                    and any(e["text"] == "e2e timer alias" for e in entries(c)))
    assert caps["status"]["state"] == "working"
    assert any(e["text"] == "e2e timer alias" for e in entries(caps))


@pytest.mark.parametrize("status", ["on", "question", "alert", "off", "working"])
def test_bot_every_state_is_accepted(runner, status):
    out = run(runner, bot.cli, ["add", "--status", status])
    assert f"estado = {status}" in out
    caps = wait_for("bot", lambda c: c["status"]["state"] == status)
    assert caps["status"]["state"] == status


def test_bot_add_with_id_edits_the_same_entry(runner):
    run(runner, bot.cli, ["add", "🔄 e2e tarefa", "--status", "working", "--id", "e2e-task"])
    run(runner, bot.cli, ["add", "✅ e2e tarefa", "--status", "on", "--id", "e2e-task"])
    caps = wait_for("bot", lambda c: any(e["text"] == "✅ e2e tarefa" for e in entries(c)))
    mine = [e["text"] for e in entries(caps) if e["id"] == "e2e-task"]
    assert mine == ["✅ e2e tarefa"]
    assert caps["status"]["state"] == "on"
    out = run(runner, bot.cli, ["show"])
    assert "e2e-task | ✅ e2e tarefa" in out


def test_bot_clear(runner):
    run(runner, bot.cli, ["clear"])
    caps = wait_for("bot", lambda c: not entries(c))
    assert entries(caps) == []


# --- Lightbulb -------------------------------------------------------------

def test_light_on_sets_color(runner):
    run(runner, light.cli, ["on", "--color", "red"])
    caps = wait_for("light", lambda c: c["switch"]["on"] and c["variant"]["color"] == "red")
    assert caps["switch"]["on"] is True
    assert caps["variant"]["color"] == "red"


def test_light_off_yellow_alias_becomes_orange(runner):
    # O Gather aceita variant.set yellow com 200, mas não muda a cor da lâmpada
    run(runner, light.cli, ["off", "--color", "yellow"])
    caps = wait_for("light", lambda c: not c["switch"]["on"] and c["variant"]["color"] == "orange")
    assert caps["switch"]["on"] is False
    assert caps["variant"]["color"] == "orange"


# --- Inbox -----------------------------------------------------------------

def test_inbox_add_same_length_texts_get_distinct_ids(runner):
    run(runner, inbox.cli, ["clear"])
    run(runner, inbox.cli, ["add", "e2e aaa"])
    run(runner, inbox.cli, ["add", "e2e bbb"])
    caps = wait_for("inbox", lambda c: len(entries(c)) == 2)
    ids = [e["id"] for e in entries(caps)]
    assert sorted(e["text"] for e in entries(caps)) == ["e2e aaa", "e2e bbb"]
    assert len(set(ids)) == 2


def test_inbox_remove_and_counter(runner):
    run(runner, inbox.cli, ["clear"])
    run(runner, inbox.cli, ["add", "e2e remover"])
    caps = wait_for("inbox", lambda c: len(entries(c)) == 1)
    task_id = entries(caps)[0]["id"]
    run(runner, inbox.cli, ["remove", task_id])
    run(runner, inbox.cli, ["set", "--level", "2"])
    caps = wait_for("inbox", lambda c: not entries(c) and c["counter"]["count"] == 2)
    assert entries(caps) == []
    assert caps["counter"]["count"] == 2


def test_inbox_add_with_id_edits_the_same_entry(runner):
    run(runner, inbox.cli, ["clear"])
    run(runner, inbox.cli, ["add", "e2e pendência", "--id", "e2e-pend"])
    run(runner, inbox.cli, ["add", "e2e pendência (editada)", "--id", "e2e-pend"])
    caps = wait_for("inbox", lambda c: any(e["text"] == "e2e pendência (editada)" for e in entries(c)))
    assert [(e["id"], e["text"]) for e in entries(caps)] == [("e2e-pend", "e2e pendência (editada)")]
