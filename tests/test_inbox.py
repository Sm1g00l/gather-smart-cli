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