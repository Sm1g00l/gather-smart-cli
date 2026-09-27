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
