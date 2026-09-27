import sys, unittest.mock as mock, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from click.testing import CliRunner
from gather_cli.light import cli

def test_light_on_red():
    runner = CliRunner()
    with mock.patch("gather_cli.webhook.requests.post") as m:
        m.return_value.status_code = 200
        result = runner.invoke(cli, ["on", "--color", "red"])
        assert result.exit_code == 0
        assert "red -> ON" in result.output
        args = m.call_args
        payload_raw = args.kwargs.get("data") or args.kwargs.get("json")
        payload_json = json.loads(payload_raw) if isinstance(payload_raw, str) else payload_raw
        assert payload_json.get("type") == "switch.set_state" or payload_json.get("data", {}).get("on") is True

def test_light_on_green():
    runner = CliRunner()
    with mock.patch("gather_cli.webhook.requests.post") as m:
        m.return_value.status_code = 200
        result = runner.invoke(cli, ["on", "--color", "green"])
    assert result.exit_code == 0
    assert "green -> ON" in result.output

def test_light_on_yellow():
    runner = CliRunner()
    with mock.patch("gather_cli.webhook.requests.post") as m:
        m.return_value.status_code = 200
        result = runner.invoke(cli, ["on", "--color", "yellow"])
    assert result.exit_code == 0
    assert "yellow -> ON" in result.output

def test_light_off_green():
    runner = CliRunner()
    with mock.patch("gather_cli.webhook.requests.post") as m:
        m.return_value.status_code = 200
        result = runner.invoke(cli, ["off", "--color", "green"])
    assert result.exit_code == 0
    assert "green -> OFF" in result.output

def test_light_on_webhook_404():
    runner = CliRunner()
    with mock.patch("gather_cli.webhook.requests.post") as m:
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = '{"error":"not_found"}'
        m.return_value = mock_resp
        result = runner.invoke(cli, ["on", "--color", "green"])
    assert result.exit_code == 0
    assert "404" in result.output

def test_light_on_webhook_error():
    runner = CliRunner()
    with mock.patch("gather_cli.webhook.requests.post") as m:
        m.side_effect = Exception("Network error")
        result = runner.invoke(cli, ["on", "--color", "green"])
    assert result.exit_code == 0
    assert "Erro webhook" in result.output

def test_light_off_webhook_404():
    runner = CliRunner()
    with mock.patch("gather_cli.webhook.requests.post") as m:
        mock_resp = mock.MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = '{"error":"not_found"}'
        m.return_value = mock_resp
        result = runner.invoke(cli, ["off", "--color", "red"])
    assert result.exit_code == 0
    assert "404" in result.output

def test_light_all_colors():
    runner = CliRunner()
    for color in ["green", "red", "yellow"]:
        runner = CliRunner()
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            result = runner.invoke(cli, ["on", "--color", color])
        assert result.exit_code == 0
        assert f"{color} -> ON" in result.output
        
        runner = CliRunner()
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value.status_code = 200
            result = runner.invoke(cli, ["off", "--color", color])
        assert result.exit_code == 0
        assert f"{color} -> OFF" in result.output

def test_light_on_sets_variant_color():
    from click.testing import CliRunner
    from gather_cli.light import cli
    with mock.patch("gather_cli.webhook.requests.post") as m:
        m.return_value.status_code = 200
        result = CliRunner().invoke(cli, ["on", "--color", "red"])
    assert result.exit_code == 0
    first = json.loads(m.call_args_list[0].kwargs["data"])
    assert first["type"] == "variant.set" and first["data"]["color"] == "red"
