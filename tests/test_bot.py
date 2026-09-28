import sys, unittest.mock as mock, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from click.testing import CliRunner
from gather_cli.bot import cli

def test_bot_add_timer_sdk():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with mock.patch("gather_cli.webhook.requests.post") as mpost:
            mpost.return_value.raise_for_status = lambda: None
            mpost.return_value.status_code = 200
            result = runner.invoke(cli, ["add", "refatorar auth", "--status", "working"])
        assert result.exit_code == 0
        msg_file = Path("bot_messages.json")
        assert msg_file.exists()
        data = json.loads(msg_file.read_text())
        assert len(data) == 1
        assert data[0]["msg"] == "refatorar auth"
        assert data[0]["status"] == "working"
        args = mpost.call_args
        payload_raw = args.kwargs.get("data") or args.kwargs.get("json")
        payload_json = json.loads(payload_raw) if isinstance(payload_raw, str) else payload_raw
        assert payload_json.get("type") == "status.set"
        assert payload_json.get("data", {}).get("state") == "working"

def test_bot_ping_success():
    runner = CliRunner()
    with mock.patch("gather_cli.webhook.requests.post") as m:
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"status":"pong","preset":"status"}'
        m.return_value = mock_resp
        result = runner.invoke(cli, ["ping"])
    assert result.exit_code == 0
    assert "200" in result.output

def test_bot_ping_404():
    runner = CliRunner()
    with mock.patch("gather_cli.webhook.requests.post") as m:
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = '{"error":"not_found"}'
        m.return_value = mock_resp
        result = runner.invoke(cli, ["ping"])
    assert result.exit_code == 0
    assert "404" in result.output

def test_bot_ping_network_error():
    runner = CliRunner()
    with mock.patch("gather_cli.webhook.requests.post") as m:
        m.side_effect = Exception("Connection refused")
        result = runner.invoke(cli, ["ping"])
    assert result.exit_code == 0
    assert "Erro no ping" in result.output

def test_bot_add_webhook_404():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with mock.patch("gather_cli.webhook.requests.post") as m:
            mock_resp = mock.MagicMock()
            mock_resp.status_code = 404
            mock_resp.text = '{"error":"not_found"}'
            m.return_value = mock_resp
            result = runner.invoke(cli, ["add", "tarefa X", "--status", "timer"])
        assert result.exit_code == 0
        assert "404" in result.output
        # Should still update local file
        data = json.loads(Path("bot_messages.json").read_text())
        assert len(data) == 1

def test_bot_add_webhook_error():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.side_effect = Exception("Network error")
            result = runner.invoke(cli, ["add", "tarefa X", "--status", "timer"])
        assert result.exit_code == 0
        assert "Erro webhook" in result.output
        # Should still update local file
        data = json.loads(Path("bot_messages.json").read_text())
        assert len(data) == 1

def test_bot_list_empty():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "Nenhuma mensagem" in result.output

def test_bot_list_with_messages():
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("bot_messages.json").write_text(json.dumps([
            {"id": 1, "msg": "tarefa 1", "status": "timer"},
            {"id": 2, "msg": "tarefa 2", "status": "on"}
        ]))
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "tarefa 1" in result.output
        assert "tarefa 2" in result.output

def test_bot_add_all_statuses():
    runner = CliRunner()
    for status in ["timer", "on", "alert", "question", "working", "off"]:
        runner = CliRunner()
        with runner.isolated_filesystem():
            with mock.patch("gather_cli.webhook.requests.post") as m:
                m.return_value.status_code = 200
                result = runner.invoke(cli, ["add", f"tarefa {status}", "--status", status])
            assert result.exit_code == 0
            data = json.loads(Path("bot_messages.json").read_text())
            assert data[0]["status"] == ("working" if status == "timer" else status)

def test_bot_add_sends_message_as_activity():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            result = runner.invoke(cli, ["add", "task: X", "--status", "on"])
        assert result.exit_code == 0
        types = [json.loads(c.kwargs["data"])["type"] for c in m.call_args_list]
        assert types == ["activity.add", "status.set"]
        assert json.loads(m.call_args_list[0].kwargs["data"])["data"]["text"] == "task: X"

def test_bot_clear():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            result = runner.invoke(cli, ["clear"])
        assert result.exit_code == 0
        assert json.loads(m.call_args.kwargs["data"])["type"] == "activity.clear"


def test_bot_add_with_id_edits_instead_of_adding():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            result = runner.invoke(cli, ["add", "✅ tarefa X", "--status", "on", "--id", "t-x"])
        assert result.exit_code == 0
        sent = [json.loads(c.kwargs["data"]) for c in m.call_args_list]
        assert [p["type"] for p in sent] == ["activity.remove", "activity.add", "status.set"]
        assert sent[0]["data"]["id"] == sent[1]["data"]["id"] == "t-x"
        assert sent[1]["data"]["text"] == "✅ tarefa X"


def test_bot_show_prints_live_entries():
    runner = CliRunner()
    with mock.patch("gather_cli.webhook.requests.post") as m:
        m.return_value.status_code = 200
        m.return_value.headers = {}
        m.return_value.json.return_value = {"capabilities": {
            "status": {"state": "working"},
            "activity": {"entries": [{"id": "t-x", "text": "🔄 tarefa X", "at": 1}]}}}
        result = runner.invoke(cli, ["show"])
    assert result.exit_code == 0, result.output
    assert "Estado: working" in result.output
    assert "t-x | 🔄 tarefa X" in result.output
    assert "(1/20 atividades)" in result.output


def test_bot_remove():
    runner = CliRunner()
    with mock.patch("gather_cli.webhook.requests.post") as m:
        m.return_value.status_code = 200
        result = runner.invoke(cli, ["remove", "t-x"])
    assert result.exit_code == 0
    assert json.loads(m.call_args.kwargs["data"]) ["data"] == {"id": "t-x"}
