import sys, unittest.mock as mock, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from click.testing import CliRunner
from gather_cli.inbox import cli

def test_inbox_add():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with mock.patch("gather_cli.inbox.requests.post") as m:
            m.return_value.status_code = 200
            result = runner.invoke(cli, ["add", "tarefa X"])
        assert result.exit_code == 0
        tasks = json.loads(Path("tasks.json").read_text())
        assert len(tasks) == 1
        assert tasks[0]["msg"] == "tarefa X"
        assert tasks[0]["level"] == 1  # nível crescente
        # SDK oficial: inbox.activity.add (id, text, url?) ou inbox.counter.set
        payload_json = m.call_args.kwargs["json"]
        assert payload_json.get("activity_action") == "activity.add" or payload_json.get("counter_action") == "counter.set"
