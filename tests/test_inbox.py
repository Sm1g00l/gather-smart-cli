import sys, unittest.mock as mock, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from click.testing import CliRunner
from gather_cli.inbox import cli
from gather_cli.inbox_config import get_config

def _make_config(tmp_path, data):
    config_dir = tmp_path / ".config" / "gather-cli"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "inboxes.json"
    config_file.write_text(json.dumps(data))
    return config_file

def test_inbox_add():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            result = runner.invoke(cli, ["add", "tarefa X"])
        assert result.exit_code == 0
        tasks = json.loads(Path("tasks.json").read_text())
        assert len(tasks) == 1
        assert tasks[0]["msg"] == "tarefa X"
        assert tasks[0]["level"] == 1

def test_inbox_remove():
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("tasks.json").write_text(json.dumps([{"id": "task_1", "msg": "test", "level": 1}]))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            result = runner.invoke(cli, ["remove", "task_1"])
        assert result.exit_code == 0
        tasks = json.loads(Path("tasks.json").read_text())
        assert len(tasks) == 0

def test_inbox_clear():
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("tasks.json").write_text(json.dumps([{"id": "task_1", "msg": "test", "level": 1}]))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            result = runner.invoke(cli, ["clear"])
        assert result.exit_code == 0
        tasks = json.loads(Path("tasks.json").read_text())
        assert len(tasks) == 0

def test_inbox_add_with_to_flag():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        tmp_path = Path(tmp)
        config_file = _make_config(tmp_path, {
            "default": "meu",
            "inboxes": {
                "meu": {"url": "https://my.url", "key": "whsec_mykey", "owner": "Me"},
                "joao": {"url": "https://joao.url", "key": "whsec_joaokey", "owner": "João"}
            }
        })
        import gather_cli.inbox as inbox_module
        inbox_module.set_config_override(config_file)
        
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            result = runner.invoke(cli, ["add", "tarefa para João", "--to", "joao"])
        
        inbox_module.clear_config_override()
        
        assert result.exit_code == 0, f"Exit code: {result.exit_code}, output: {result.output}"
        args = m.call_args
        assert args is not None, "Mock not called"
        assert "joao.url" in str(args) or "https://joao.url" in str(args)

def test_inbox_add_with_to_nonexistent():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        tmp_path = Path(tmp)
        config_file = _make_config(tmp_path, {"default": "meu", "inboxes": {}})
        
        import gather_cli.inbox as inbox_module
        inbox_module.set_config_override(config_file)
        
        result = runner.invoke(cli, ["add", "tarefa", "--to", "inexistente"])
        
        inbox_module.clear_config_override()
        
        assert result.exit_code != 0
        assert "não encontrado" in result.output.lower() or "not found" in result.output.lower()

def test_inbox_add_without_to_uses_default():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        tmp_path = Path(tmp)
        config_file = _make_config(tmp_path, {
            "default": "meu",
            "inboxes": {
                "meu": {"url": "https://my.url", "key": "whsec_mykey", "owner": "Me"}
            }
        })
        
        import gather_cli.inbox as inbox_module
        inbox_module.set_config_override(config_file)
        
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            result = runner.invoke(cli, ["add", "minha tarefa"])
        
        inbox_module.clear_config_override()
        
        assert result.exit_code == 0, f"Exit code: {result.exit_code}, output: {result.output}"
        args = m.call_args
        assert args is not None, "Mock not called"
        assert "my.url" in str(args)

# Config commands tests
def test_inbox_config_add():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        tmp_path = Path(tmp)
        config_file = _make_config(tmp_path, {"default": "meu", "inboxes": {}})
        import gather_cli.inbox as inbox_module
        inbox_module.set_config_override(config_file)
        
        result = runner.invoke(cli, ["config", "add", "novo", "--url", "https://new.url", "--key", "whsec_newkey", "--owner", "Novo"])
        
        inbox_module.clear_config_override()
        
        assert result.exit_code == 0
        assert "adicionado" in result.output.lower()

def test_inbox_config_list():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        tmp_path = Path(tmp)
        config_file = _make_config(tmp_path, {
            "default": "meu",
            "inboxes": {
                "meu": {"url": "https://my.url", "key": "whsec_mykey", "owner": "Me"}
            }
        })
        import gather_cli.inbox as inbox_module
        inbox_module.set_config_override(config_file)
        
        result = runner.invoke(cli, ["config", "list"])
        
        inbox_module.clear_config_override()
        
        assert result.exit_code == 0
        assert "meu" in result.output
        assert "whsec_***" in result.output

def test_inbox_config_remove():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        tmp_path = Path(tmp)
        config_file = _make_config(tmp_path, {
            "default": "meu",
            "inboxes": {
                "meu": {"url": "https://my.url", "key": "whsec_mykey", "owner": "Me"},
                "outro": {"url": "https://outro.url", "key": "whsec_outrokey", "owner": "Outro"}
            }
        })
        import gather_cli.inbox as inbox_module
        inbox_module.set_config_override(config_file)
        
        result = runner.invoke(cli, ["config", "remove", "outro"])
        
        inbox_module.clear_config_override()
        
        assert result.exit_code == 0
        assert "removido" in result.output.lower()

def test_inbox_config_default():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        tmp_path = Path(tmp)
        config_file = _make_config(tmp_path, {
            "default": "meu",
            "inboxes": {
                "meu": {"url": "https://my.url", "key": "whsec_mykey", "owner": "Me"},
                "joao": {"url": "https://joao.url", "key": "whsec_joaokey", "owner": "João"}
            }
        })
        import gather_cli.inbox as inbox_module
        inbox_module.set_config_override(config_file)
        
        result = runner.invoke(cli, ["config", "default", "joao"])
        
        inbox_module.clear_config_override()
        
        assert result.exit_code == 0
        assert "default" in result.output.lower()

def test_inbox_config_default_invalid():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        tmp_path = Path(tmp)
        config_file = _make_config(tmp_path, {
            "default": "meu",
            "inboxes": {"meu": {"url": "https://my.url", "key": "whsec_mykey", "owner": "Me"}}
        })
        import gather_cli.inbox as inbox_module
        inbox_module.set_config_override(config_file)
        
        result = runner.invoke(cli, ["config", "default", "inexistente"])
        
        inbox_module.clear_config_override()
        
        assert result.exit_code != 0
        assert "não encontrado" in result.output.lower() or "not found" in result.output.lower()

# Error handling tests
def test_inbox_add_webhook_404():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with mock.patch("gather_cli.webhook.requests.post") as m:
            mock_resp = mock.MagicMock()
            mock_resp.status_code = 404
            m.return_value = mock_resp
            result = runner.invoke(cli, ["add", "tarefa X"])
        assert result.exit_code == 0
        assert "404" in result.output

def test_inbox_add_webhook_error():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.side_effect = Exception("Connection error")
            result = runner.invoke(cli, ["add", "tarefa X"])
        assert result.exit_code == 0
        assert "Erro webhook" in result.output

def test_inbox_remove_webhook_404():
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("tasks.json").write_text(json.dumps([{"id": "task_1", "msg": "test", "level": 1}]))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            mock_resp = mock.MagicMock()
            mock_resp.status_code = 404
            m.return_value = mock_resp
            result = runner.invoke(cli, ["remove", "task_1"])
        assert result.exit_code == 0
        assert "404" in result.output

def test_inbox_clear_webhook_404():
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("tasks.json").write_text(json.dumps([{"id": "task_1", "msg": "test", "level": 1}]))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            mock_resp = mock.MagicMock()
            mock_resp.status_code = 404
            m.return_value = mock_resp
            result = runner.invoke(cli, ["clear"])
        assert result.exit_code == 0
        assert "404" in result.output

def test_inbox_list_empty():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "Nenhuma tarefa" in result.output

def test_inbox_list_with_tasks():
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("tasks.json").write_text(json.dumps([{"id": "task_1", "msg": "test", "level": 1}]))
        result = runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "task_1" in result.output

def test_inbox_set_level():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            result = runner.invoke(cli, ["set", "--level", "5"])
        assert result.exit_code == 0
        assert "nível definido: 5" in result.output.lower()

def test_inbox_add_with_id_edits_instead_of_adding():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            runner.invoke(cli, ["add", "revisar PR #42", "--id", "pr-42"])
            result = runner.invoke(cli, ["add", "revisar PR #42 (2 comentários)", "--id", "pr-42"])
        assert result.exit_code == 0
        sent = [json.loads(c.kwargs["data"]) for c in m.call_args_list]
        assert [p["type"] for p in sent] == ["activity.remove", "activity.add"] * 2
        assert {p["data"]["id"] for p in sent} == {"pr-42"}
        tasks = json.loads(Path("tasks.json").read_text())
        assert [(t["id"], t["msg"]) for t in tasks] == [("pr-42", "revisar PR #42 (2 comentários)")]


def test_inbox_show_prints_live_entries():
    runner = CliRunner()
    with mock.patch("gather_cli.webhook.requests.post") as m:
        m.return_value.status_code = 200
        m.return_value.headers = {}
        m.return_value.json.return_value = {"capabilities": {
            "counter": {"count": 1},
            "activity": {"entries": [{"id": "pr-42", "text": "revisar PR #42", "at": 1}]}}}
        result = runner.invoke(cli, ["show"])
    assert result.exit_code == 0, result.output
    assert "Contador: 1" in result.output
    assert "pr-42 | revisar PR #42" in result.output
