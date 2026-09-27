import json
import os
import stat
from pathlib import Path

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "gather-cli"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "inboxes.json"

class InboxConfig:
    def __init__(self, path: Path = None):
        self.path = path or DEFAULT_CONFIG_FILE
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}")
            self._chmod_600()
        self._data = json.loads(self.path.read_text())

    def _chmod_600(self):
        os.chmod(self.path, 0o600)

    def _save(self):
        self.path.write_text(json.dumps(self._data, indent=2))
        self._chmod_600()

    def _validate_key(self, key: str):
        if not key.startswith("whsec_"):
            raise ValueError("Key must start with 'whsec_'")

    def add(self, name: str, url: str, key: str, owner: str = ""):
        self._validate_key(key)
        inboxes = self._data.setdefault("inboxes", {})
        inboxes[name] = {"url": url, "key": key, "owner": owner}
        if "default" not in self._data:
            self._data["default"] = name
        self._save()

    def get(self, name: str):
        return self._data.get("inboxes", {}).get(name)

    def list(self):
        result = {}
        for name, inbox in self._data.get("inboxes", {}).items():
            masked = inbox.copy()
            if masked.get("key", "").startswith("whsec_"):
                masked["key"] = "whsec_***"
            result[name] = masked
        return result

    def remove(self, name: str):
        inboxes = self._data.get("inboxes", {})
        if name in inboxes:
            del inboxes[name]
        if self._data.get("default") == name:
            self._data["default"] = next(iter(inboxes)) if inboxes else None
        self._save()

    def set_default(self, name: str):
        if name not in self._data.get("inboxes", {}):
            raise ValueError(f"Inbox '{name}' not found")
        self._data["default"] = name
        self._save()

    def get_default(self):
        return self._data.get("default")

def get_config(path: Path = None) -> InboxConfig:
    """Factory function to get InboxConfig instance."""
    return InboxConfig(path)