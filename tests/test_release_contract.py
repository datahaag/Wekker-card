"""Release and HACS integration layout checks."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "wekker_card"

def test_hacs_integration_layout() -> None:
    hacs = json.loads((ROOT / "hacs.json").read_text(encoding="utf-8"))
    manifest = json.loads((COMPONENT / "manifest.json").read_text(encoding="utf-8"))
    assert hacs == {"name": "Wekker-card", "render_readme": True}
    assert manifest["domain"] == "wekker_card"
    assert manifest["config_flow"] is True
    assert manifest["version"] == "2.0.0"
    assert manifest["requirements"] == []

def test_all_runtime_files_live_in_component() -> None:
    required = {"__init__.py", "alarm.py", "button.py", "config_flow.py", "const.py", "entity.py", "manifest.json", "number.py", "select.py", "sensor.py", "services.yaml", "switch.py", "text.py", "time.py", "frontend/wekker-card.js", "translations/en.json", "translations/nl.json"}
    actual = {path.relative_to(COMPONENT).as_posix() for path in COMPONENT.rglob("*") if path.is_file() and "__pycache__" not in path.parts}
    assert required <= actual

def test_no_terminal_installer_is_required() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "HACS" in readme
    assert "custom_components/wekker_card" in readme
    assert "install.sh --hacs" not in readme

def test_workflow_validates_integration() -> None:
    workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
    assert "category: integration" in workflow
    assert "hassfest" in workflow.lower()

if __name__ == "__main__":
    tests = [value for name, value in globals().copy().items() if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"OK: {len(tests)} release contract tests")
