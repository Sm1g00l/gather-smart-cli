
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_repo_has_pyproject():
    assert (Path(__file__).parent.parent / "pyproject.toml").exists()

def test_cli_package_exists():
    assert (Path(__file__).parent.parent / "src" / "gather_cli" / "__init__.py").exists()

def test_readme_exists():
    assert (Path(__file__).parent.parent / "README.md").exists()
