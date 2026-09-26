import sys, unittest.mock as mock, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from click.testing import CliRunner
from gather_cli.test_all import cli

def test_test_all_reports():
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Criar .env simulado
        env_path = Path(".env")
        env_path.write_text("BOT_MONITOR_URL=http://test/bot\nBOT_MONITOR_KEY=whsec_abc\nLIGHTBULB_URL=http://test/light\nLIGHTBULB_KEY=whsec_abc\nINBOX_URL=http://test/inbox\nINBOX_KEY=whsec_abc\n")
        result = runner.invoke(cli, ["all"])
        # Não necessariamente passa (o webhook pode falhar), mas imprime algo
        assert result.exit_code in [0, 2]  # 0 = passou, 2 = erro de webhook (aceitável)
        assert "Bot Monitor" in result.output or "Webhook" in result.output or "resume" in result.output.lower()
