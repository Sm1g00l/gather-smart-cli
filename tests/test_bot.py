
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
