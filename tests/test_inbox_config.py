import sys, json, os, stat
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from gather_cli.inbox_config import InboxConfig

def test_inbox_config_add_and_get():
    with Path("test_inboxes.json").open("w") as f:
        f.write("{}")
    config = InboxConfig(Path("test_inboxes.json"))
    config.add("meu", "https://url1", "whsec_key1", "Lucas")
    inbox = config.get("meu")
    assert inbox["url"] == "https://url1"
    assert inbox["key"] == "whsec_key1"
    assert inbox["owner"] == "Lucas"

def test_inbox_config_list_masks_keys():
    with Path("test_inboxes.json").open("w") as f:
        f.write("{}")
    config = InboxConfig(Path("test_inboxes.json"))
    config.add("meu", "https://url1", "whsec_abcdef123456", "Lucas")
    config.add("joao", "https://url2", "whsec_xyz789", "João")
    listed = config.list()
    assert "meu" in listed
    assert "joao" in listed
    assert listed["meu"]["key"] == "whsec_***"
    assert listed["joao"]["key"] == "whsec_***"
    assert listed["meu"]["url"] == "https://url1"

def test_inbox_config_remove():
    with Path("test_inboxes.json").open("w") as f:
        f.write("{}")
    config = InboxConfig(Path("test_inboxes.json"))
    config.add("meu", "https://url1", "whsec_key1", "Lucas")
    config.remove("meu")
    assert config.get("meu") is None

def test_inbox_config_default():
    with Path("test_inboxes.json").open("w") as f:
        f.write("{}")
    config = InboxConfig(Path("test_inboxes.json"))
    config.add("meu", "https://url1", "whsec_key1", "Lucas")
    config.add("joao", "https://url2", "whsec_key2", "João")
    config.set_default("joao")
    assert config.get_default() == "joao"
    assert config.get("joao") is not None

def test_inbox_config_get_default_returns_none_when_empty():
    with Path("test_inboxes.json").open("w") as f:
        f.write("{}")
    config = InboxConfig(Path("test_inboxes.json"))
    assert config.get_default() is None

def test_inbox_config_validates_whsec_prefix():
    with Path("test_inboxes.json").open("w") as f:
        f.write("{}")
    config = InboxConfig(Path("test_inboxes.json"))
    try:
        config.add("bad", "https://url", "invalid_key", "Test")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "whsec_" in str(e)

def test_inbox_config_file_permissions_600():
    with Path("test_inboxes.json").open("w") as f:
        f.write("{}")
    config = InboxConfig(Path("test_inboxes.json"))
    config.add("meu", "https://url1", "whsec_key1", "Lucas")
    mode = os.stat("test_inboxes.json").st_mode
    assert stat.S_IMODE(mode) == 0o600

def test_inbox_config_persists_across_instances():
    with Path("test_inboxes.json").open("w") as f:
        f.write("{}")
    config1 = InboxConfig(Path("test_inboxes.json"))
    config1.add("meu", "https://url1", "whsec_key1", "Lucas")
    config1.set_default("meu")
    config2 = InboxConfig(Path("test_inboxes.json"))
    assert config2.get("meu") is not None
    assert config2.get_default() == "meu"