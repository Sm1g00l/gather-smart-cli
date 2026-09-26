import sys, unittest.mock as mock, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from click.testing import CliRunner
from gather_cli.light import cli

def test_light_on_red():
    runner = CliRunner()
    with mock.patch("gather_cli.light.requests.post") as m:
        m.return_value.status_code = 200
        result = runner.invoke(cli, ["on", "--color", "red"])
        assert result.exit_code == 0
        assert "red -> ON" in result.output
        args = m.call_args
        payload_raw = args.kwargs.get("data") or args.kwargs.get("json")
        payload_json = json.loads(payload_raw) if isinstance(payload_raw, str) else payload_raw
        # SDK oficial: tipo do evento e data
        assert payload_json.get("type") == "switch.set_state" or payload_json.get("data", {}).get("on") is True
