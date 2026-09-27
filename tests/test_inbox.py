import sys, unittest.mock as mock, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from click.testing import CliRunner
from gather_cli.inbox import cli

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
        args = m.call_args
        payload_raw = args.kwargs.get("data") or args.kwargs.get("json")
        payload_json = json.loads(payload_raw) if isinstance(payload_raw, str) else payload_raw
        assert payload_json.get("type") == "activity.add"

def test_inbox_remove():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Setup: add a task first
        Path("tasks.json").write_text(json.dumps([{"id": "task_1", "msg": "test", "level": 1}]))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            result = runner.invoke(cli, ["remove", "task_1"])
        assert result.exit_code == 0
        tasks = json.loads(Path("tasks.json").read_text())
        assert len(tasks) == 0
        args = m.call_args
        payload_raw = args.kwargs.get("data") or args.kwargs.get("json")
        payload_json = json.loads(payload_raw) if isinstance(payload_raw, str) else payload_raw
        assert payload_json.get("type") == "activity.remove"
        assert payload_json.get("data", {}).get("id") == "task_1"

def test_inbox_clear():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Setup: add tasks first
        Path("tasks.json").write_text(json.dumps([{"id": "task_1", "msg": "test", "level": 1}]))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            result = runner.invoke(cli, ["clear"])
        assert result.exit_code == 0
        tasks = json.loads(Path("tasks.json").read_text())
        assert len(tasks) == 0
        args = m.call_args
        payload_raw = args.kwargs.get("data") or args.kwargs.get("json")
        payload_json = json.loads(payload_raw) if isinstance(payload_raw, str) else payload_raw
        assert payload_json.get("type") == "activity.clear"