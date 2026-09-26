import sys, unittest.mock as mock
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
        assert args.kwargs["json"]["variation"] == "red"
        assert args.kwargs["json"]["state"] == "on"
