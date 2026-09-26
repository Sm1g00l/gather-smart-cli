import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from unittest.mock import patch
from click.testing import CliRunner
from gather_cli.setup import setup

def test_setup_creates_env():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(setup, [
            '--bot-url', 'http://bot', '--bot-key', 'key1',
            '--light-url', 'http://light', '--light-key', 'key2',
            '--inbox-url', 'http://inbox', '--inbox-key', 'key3',
        ])
        assert result.exit_code == 0
        env_file = Path(".env")
        assert env_file.exists()
        content = env_file.read_text()
        assert "BOT_MONITOR_URL=http://bot" in content
        assert "LIGHTBULB_KEY=key2" in content
