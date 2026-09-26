
import sys, unittest.mock as mock, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from click.testing import CliRunner
from gather_cli.bot import cli

def test_bot_add_timer_sdk():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with mock.patch("gather_cli.bot.requests.post") as mpost:
            mpost.return_value.raise_for_status = lambda: None
            mpost.return_value.status_code = 200
            result = runner.invoke(cli, ["add", "refatorar auth", "--status", "timer"])
        assert result.exit_code == 0
        msg_file = Path("bot_messages.json")
        assert msg_file.exists()
        data = json.loads(msg_file.read_text())
        assert len(data) == 1
        assert data[0]["msg"] == "refatorar auth"
        assert data[0]["status"] == "timer"
        # Verifica payload SDK oficial: status.set
        args = mpost.call_args.kwargs["json"]
        assert args.get("state") == "timer" or args.get("state_action") is not None
