import sys, unittest.mock as mock, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from click.testing import CliRunner
from gather_cli.test_all import cli

def _make_env(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("BOT_MONITOR_URL=http://test/bot\nBOT_MONITOR_KEY=whsec_abc\nLIGHTBULB_URL=http://test/light\nLIGHTBULB_KEY=whsec_abc\nINBOX_URL=http://test/inbox\nINBOX_KEY=whsec_abc\n")
    return env_path

def _mock_response(status_code, json_data=None, text="", headers=None):
    resp = mock.MagicMock()
    resp.status_code = status_code
    if json_data:
        resp.json.return_value = json_data
    resp.text = text or json.dumps(json_data) if json_data else ""
    resp.headers = headers or {}
    return resp

def test_test_all_success():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        _make_env(Path(tmp))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value = _mock_response(200, {"type": "webhook.pong", "preset": "status", "capabilities": {}})
            result = runner.invoke(cli, ["all"])
        assert result.exit_code == 0
        assert "OK" in result.output
        assert "Bot Monitor" in result.output
        assert "Lightbulb" in result.output
        assert "Inbox" in result.output

def test_test_all_404():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        _make_env(Path(tmp))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value = _mock_response(404, {"error": "not_found"})
            result = runner.invoke(cli, ["all"])
        assert result.exit_code == 0
        assert "404" in result.output

def test_test_all_400():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        _make_env(Path(tmp))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value = _mock_response(400, {"error": "invalid_request"})
            result = runner.invoke(cli, ["all"])
        assert result.exit_code == 0
        assert "400" in result.output

def test_test_all_410():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        _make_env(Path(tmp))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value = _mock_response(410, {"error": "token_revoked"})
            result = runner.invoke(cli, ["all"])
        assert result.exit_code == 0
        assert "410" in result.output

def test_test_all_415():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        _make_env(Path(tmp))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value = _mock_response(415)
            result = runner.invoke(cli, ["all"])
        assert result.exit_code == 0
        assert "415" in result.output

def test_test_all_429_with_retry_after():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        _make_env(Path(tmp))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value = _mock_response(429, {"error": "rate_limited"}, headers={"RateLimit-Reset": "60"})
            result = runner.invoke(cli, ["all"])
        assert result.exit_code == 0
        assert "429" in result.output
        assert "60" in result.output

def test_test_all_503():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        _make_env(Path(tmp))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value = _mock_response(503, {"error": "service_unavailable"})
            result = runner.invoke(cli, ["all"])
        assert result.exit_code == 0
        assert "503" in result.output

def test_test_all_missing_env():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # No .env file - use empty env
        result = runner.invoke(cli, ["all"], env={"BOT_MONITOR_URL": "", "BOT_MONITOR_KEY": "", "LIGHTBULB_URL": "", "LIGHTBULB_KEY": "", "INBOX_URL": "", "INBOX_KEY": ""})
    assert result.exit_code == 0
    assert "SKIP" in result.output or "faltando" in result.output.lower()

def test_test_all_invalid_key_format():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        env_path = Path(tmp) / ".env"
        env_path.write_text("BOT_MONITOR_URL=http://test/bot\nBOT_MONITOR_KEY=invalid_key\n")
        with mock.patch.dict("os.environ", {"BOT_MONITOR_URL": "http://test/bot", "BOT_MONITOR_KEY": "invalid_key", "LIGHTBULB_URL": "", "LIGHTBULB_KEY": "", "INBOX_URL": "", "INBOX_KEY": ""}):
            with mock.patch("gather_cli.webhook.requests.post") as m:
                m.return_value = _mock_response(200, {"type": "webhook.pong"})
                result = runner.invoke(cli, ["all"])
    assert result.exit_code == 0
    # The invalid key will cause a decode error which will be caught and reported
    assert "ERRO" in result.output or "inválido" in result.output.lower() or "decode" in result.output.lower()

def test_test_all_network_error():
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        _make_env(Path(tmp))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.side_effect = Exception("Connection refused")
            result = runner.invoke(cli, ["all"])
        assert result.exit_code == 0
        assert "EXCEÇÃO" in result.output or "Erro" in result.output

def test_test_all_429_uses_gather_retry_after_header():
    # Headers reais de um 429 do Gather (sem RateLimit-Reset)
    from requests.structures import CaseInsensitiveDict
    headers = CaseInsensitiveDict({"ratelimit-policy": "60;w=60", "ratelimit-limit": "60",
                                   "ratelimit-remaining": "0", "retry-after": "60"})
    runner = CliRunner()
    with runner.isolated_filesystem() as tmp:
        _make_env(Path(tmp))
        with mock.patch("gather_cli.webhook.requests.post") as m:
            m.return_value = _mock_response(429, {"error": "rate_limited"}, headers=headers)
            result = runner.invoke(cli, ["all"])
        assert "Retry-After=60s" in result.output
        assert "Rate limit: 0/60 restantes" in result.output


def test_rate_limit_info():
    from requests.structures import CaseInsensitiveDict
    from gather_cli.webhook import rate_limit_info
    resp = mock.MagicMock()
    resp.headers = CaseInsensitiveDict({"ratelimit-policy": "60;w=60", "ratelimit-limit": "60", "ratelimit-remaining": "57"})
    assert rate_limit_info(resp) == {"limit": 60, "remaining": 57, "policy": "60;w=60", "retry_after": None}
    resp.headers = CaseInsensitiveDict({"ratelimit-remaining": "0", "retry-after": "60"})
    assert rate_limit_info(resp)["retry_after"] == 60
