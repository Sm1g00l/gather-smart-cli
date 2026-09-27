import sys, unittest.mock as mock, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from click.testing import CliRunner
from gather_cli.test_all import cli

def test_test_all_reports():
    runner = CliRunner()
    with runner.isolated_filesystem():
        env_path = Path(".env")
        env_path.write_text("BOT_MONITOR_URL=http://test/bot\nBOT_MONITOR_KEY=whsec_abc\nLIGHTBULB_URL=http://test/light\nLIGHTBULB_KEY=whsec_abc\nINBOX_URL=http://test/inbox\nINBOX_KEY=whsec_abc\n")
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            m.return_value.json.return_value = {"type": "webhook.pong"}
            m.return_value.text = '{"type":"webhook.pong"}'
            m.return_value.headers = {}
            result = runner.invoke(cli, ["all"])
        assert result.exit_code == 0
        assert "Bot Monitor" in result.output
