"""Release-, pad-, HACS- en installatiemigratiecontroles voor Wekker-card."""

from __future__ import annotations

import os
import json
from pathlib import Path
import re
import shutil
import shlex
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = (ROOT / "install.sh").read_text(encoding="utf-8")
CARD = ROOT / "custom_cards" / "wekker-card" / "wekker-card.js"
PACKAGE = ROOT / "packages" / "wekker_card.yaml"
CANONICAL_FILE = "/config/www/community/wekker-card/wekker-card.js"
CANONICAL_URL = "/local/community/wekker-card/wekker-card.js?v=1.10.0"
HACS_URL = "/hacsfiles/wekker-card/wekker-card.js"


def test_canonical_source_paths_are_lowercase() -> None:
    assert CARD.is_file()
    assert PACKAGE.is_file()
    tracked_paths = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts
    ]
    assert "custom_cards/wekker-card/wekker-card.js" in tracked_paths
    assert "dashboard/wekker-card.yaml" in tracked_paths
    assert "custom_cards/Wekker-card/wekker-card.js" not in tracked_paths
    assert "dashboard/sonos-smart-alarm.yaml" not in tracked_paths
    assert "packages/wekker-card.yaml" not in tracked_paths
    assert "packages/sonos_smart_alarm.yaml" not in tracked_paths
    assert re.fullmatch(r"[a-z0-9_]+", PACKAGE.stem)


def test_active_installer_paths_are_identical() -> None:
    assert 'CARD_SOURCE="$SCRIPT_DIR/custom_cards/wekker-card/wekker-card.js"' in INSTALLER
    assert 'CARD_TARGET="$CONFIG_DIR/www/community/wekker-card/wekker-card.js"' in INSTALLER
    assert INSTALLER.count(CANONICAL_URL) == 5
    assert 'PACKAGE_SOURCE="$SCRIPT_DIR/packages/wekker_card.yaml"' in INSTALLER
    assert 'PACKAGE_TARGET="$CONFIG_DIR/packages/wekker_card.yaml"' in INSTALLER
    assert 'INVALID_PACKAGE_TARGET="$CONFIG_DIR/packages/wekker-card.yaml"' in INSTALLER
    assert 'DASHBOARD_SOURCE="$SCRIPT_DIR/dashboard/wekker-card.yaml"' in INSTALLER
    assert 'DASHBOARD_TARGET="$CONFIG_DIR/dashboards/wekker-card.yaml"' in INSTALLER


def test_current_documentation_uses_only_canonical_paths() -> None:
    current_docs = [
        ROOT / "README.md",
        ROOT / "docs" / "architecture.md",
        ROOT / "docs" / "automatic-installation.md",
        ROOT / "docs" / "custom-card.md",
        ROOT / "docs" / "dashboard.md",
        ROOT / "docs" / "installation.md",
        ROOT / "docs" / "troubleshooting.md",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in current_docs)
    assert "/config/www/community/Wekker-card" not in combined
    assert "/local/community/Wekker-card" not in combined
    assert "custom_cards/Wekker-card" not in combined
    assert "v=1.7.0" not in combined
    assert "?v=1.8.1" not in combined
    assert CANONICAL_FILE in combined
    assert CANONICAL_URL in combined


def test_card_registration_and_picker_metadata() -> None:
    source = CARD.read_text(encoding="utf-8")
    assert 'const CARD_VERSION = "1.10.0";' in source
    assert f'const HACS_RESOURCE_PATH = "{HACS_URL}";' in source
    assert 'type: "lovelace/resources/create"' in source
    assert 'type: "lovelace/resources/update"' in source
    assert 'type: "lovelace/resources/delete"' in source
    assert 'type: "lovelace/info"' in source
    assert 'info?.resource_mode !== "storage"' in source
    assert "connectedCallback()" in source
    assert "disconnectedCallback()" in source
    assert source.count('customElements.define("wekker-card"') == 1
    assert 'customElements.define("sonos-smart-alarm-card"' not in source
    assert 'type: "wekker-card"' in source
    assert 'name: "Wekker-card (Sonos retro)"' in source


def test_hacs_repository_layout() -> None:
    manifest = json.loads((ROOT / "hacs.json").read_text(encoding="utf-8"))
    dist_card = ROOT / "dist" / "wekker-card.js"
    workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
    assert manifest["name"] == "Wekker-card"
    assert manifest["filename"] == "wekker-card.js"
    assert dist_card.is_file()
    assert dist_card.read_bytes() == CARD.read_bytes()
    assert "uses: hacs/action@main" in workflow
    assert "category: plugin" in workflow
    assert HACS_URL in (ROOT / "docs" / "github-hacs.md").read_text(encoding="utf-8")


def _shell_path(path: Path) -> str:
    value = path.resolve().as_posix()
    if os.name == "nt" and len(value) > 2 and value[1] == ":":
        return f"/{value[0].lower()}{value[2:]}"
    return value


def test_installer_migrates_and_is_idempotent() -> None:
    shell = os.environ.get("TEST_SH") or shutil.which("bash") or shutil.which("sh")
    if not shell:
        raise RuntimeError("Stel TEST_SH in op een bash/sh-runtime om de installatietest uit te voeren.")

    with tempfile.TemporaryDirectory(prefix=".wekker-card-test-", dir=ROOT) as temp:
        config = Path(temp) / "config"
        (config / "packages").mkdir(parents=True)
        (config / "www").mkdir()
        (config / "dashboards").mkdir()
        mock_bin = config / "mock-bin"
        mock_bin.mkdir()
        mock_ha = mock_bin / "ha"
        mock_ha.write_text(
            "#!/bin/sh\n"
            "[ \"$1 $2\" = \"core check\" ] || exit 2\n"
            "printf 'MOCK HA CORE CHECK: OK\\n'\n",
            encoding="utf-8",
        )
        mock_ha.chmod(0o755)
        (config / "packages" / "sonos_smart_alarm.yaml").write_text("legacy: true\n", encoding="utf-8")
        (config / "packages" / "wekker-card.yaml").write_text("invalid_slug: true\n", encoding="utf-8")
        (config / "packages" / "wekker_card.yaml.disabled").write_text("disabled_old: true\n", encoding="utf-8")
        (config / "dashboards" / "sonos-smart-alarm.yaml").write_text("legacy: true\n", encoding="utf-8")
        (config / "www" / "sonos-smart-alarm-card.js").write_text("legacy\n", encoding="utf-8")
        configuration = config / "configuration.yaml"
        configuration.write_text(
            "homeassistant:\n"
            "  name: Test\n"
            "frontend:\n"
            "  extra_module_url:\n"
            "    - /local/community/Wekker-card/wekker-card.js?v=1.7.0\n"
            "    - /local/community/wekker-card/wekker-card.js?v=1.8.1\n"
            "lovelace:\n"
            "  resources:\n"
            "    - url: /local/community/wekker-card/wekker-card.js?v=1.9.0\n"
            "      type: module\n"
            "  dashboards:\n"
            "    sonos-smart-alarm:\n"
            "      mode: yaml\n"
            "      filename: dashboards/sonos-smart-alarm.yaml\n"
            "      title: Sonos-wekker\n"
            "      icon: mdi:alarm\n"
            "      show_in_sidebar: true\n",
            encoding="utf-8",
        )

        shell_bin = _shell_path(Path(shell).resolve().parent)
        mock_bin_argument = mock_bin.relative_to(ROOT).as_posix()
        config_argument = config.relative_to(ROOT).as_posix()
        invocation = (
            f"PATH={shlex.quote(mock_bin_argument)}:{shlex.quote(shell_bin)}:$PATH; "
            f"sh install.sh --config {shlex.quote(config_argument)}"
        )
        command = [shell, "-c", invocation]
        first = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        assert first.returncode == 0, f"installatie mislukt:\n{first.stdout}\n{first.stderr}"
        second = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        assert second.returncode == 0, f"herinstallatie mislukt:\n{second.stdout}\n{second.stderr}"
        result = configuration.read_text(encoding="utf-8")

        assert (config / "packages" / "wekker_card.yaml").is_file()
        assert not (config / "packages" / "wekker-card.yaml").exists()
        assert not (config / "packages" / "wekker_card.yaml.disabled").exists()
        assert not (config / "packages" / "sonos_smart_alarm.yaml").exists()
        assert (config / "dashboards" / "wekker-card.yaml").is_file()
        assert not (config / "dashboards" / "sonos-smart-alarm.yaml").exists()
        assert (config / "www" / "community" / "wekker-card" / "wekker-card.js").is_file()
        assert not (config / "www" / "sonos-smart-alarm-card.js").exists()
        assert result.count(CANONICAL_URL) == 1
        assert result.count("type: module") == 0
        assert "  resources:" not in result
        assert "/local/community/Wekker-card" not in result
        assert result.count("wekker-card:") == 1
        assert "sonos-smart-alarm:" not in result
        assert "Bestanden naar" in first.stdout
        assert "Bestanden naar" in second.stdout
        assert "MOCK HA CORE CHECK: OK" in first.stdout
        assert "Configuratiecontrole geslaagd" in first.stdout


def test_installer_registers_explicit_yaml_resource_mode() -> None:
    shell = os.environ.get("TEST_SH") or shutil.which("bash") or shutil.which("sh")
    if not shell:
        raise RuntimeError("Stel TEST_SH in op een bash/sh-runtime om de installatietest uit te voeren.")

    with tempfile.TemporaryDirectory(prefix=".wekker-card-yaml-test-", dir=ROOT) as temp:
        config = Path(temp) / "config"
        (config / "packages").mkdir(parents=True)
        (config / "www").mkdir()
        (config / "dashboards").mkdir()
        mock_bin = config / "mock-bin"
        mock_bin.mkdir()
        mock_ha = mock_bin / "ha"
        mock_ha.write_text(
            "#!/bin/sh\n"
            "[ \"$1 $2\" = \"core check\" ] || exit 2\n"
            "printf 'MOCK HA CORE CHECK: OK\\n'\n",
            encoding="utf-8",
        )
        mock_ha.chmod(0o755)
        configuration = config / "configuration.yaml"
        configuration.write_text(
            "homeassistant:\n"
            "  packages: !include_dir_named packages\n"
            "frontend:\n"
            "  extra_module_url:\n"
            "    - /local/community/wekker-card/wekker-card.js?v=1.9.0\n"
            "lovelace:\n"
            "  resource_mode: yaml\n"
            "  resources:\n"
            "    - url: /local/community/wekker-card/wekker-card.js?v=1.9.0\n"
            "      type: module\n"
            "    - url: /local/other-card.js\n"
            "      type: module\n"
            "  dashboards:\n"
            "    wekker-card:\n"
            "      mode: yaml\n"
            "      filename: dashboards/wekker-card.yaml\n"
            "      title: Sonos-wekker\n"
            "      icon: mdi:alarm\n"
            "      show_in_sidebar: true\n",
            encoding="utf-8",
        )

        shell_bin = _shell_path(Path(shell).resolve().parent)
        invocation = (
            f"PATH={shlex.quote(mock_bin.relative_to(ROOT).as_posix())}:"
            f"{shlex.quote(shell_bin)}:$PATH; "
            f"sh install.sh --config {shlex.quote(config.relative_to(ROOT).as_posix())}"
        )
        result = subprocess.run([shell, "-c", invocation], cwd=ROOT, text=True, capture_output=True)
        assert result.returncode == 0, f"YAML-mode-installatie mislukt:\n{result.stdout}\n{result.stderr}"
        installed = configuration.read_text(encoding="utf-8")
        assert installed.count(CANONICAL_URL) == 2
        assert "/local/community/wekker-card/wekker-card.js?v=1.9.0" not in installed
        assert "/local/other-card.js" in installed
        assert "  resource_mode: yaml" in installed
        assert installed.count("type: module") == 2
        assert "Wekker-card als YAML-resource geregistreerd" in result.stdout


def test_hacs_mode_preserves_hacs_card_and_removes_local_module_config() -> None:
    shell = os.environ.get("TEST_SH") or shutil.which("bash") or shutil.which("sh")
    if not shell:
        raise RuntimeError("Stel TEST_SH in op een bash/sh-runtime om de installatietest uit te voeren.")

    with tempfile.TemporaryDirectory(prefix=".wekker-card-hacs-test-", dir=ROOT) as temp:
        config = Path(temp) / "config"
        card_target = config / "www" / "community" / "wekker-card" / "wekker-card.js"
        card_target.parent.mkdir(parents=True)
        (config / "packages").mkdir()
        (config / "dashboards").mkdir()
        hacs_contents = "// HACS MANAGED CARD\n"
        card_target.write_text(hacs_contents, encoding="utf-8")
        configuration = config / "configuration.yaml"
        configuration.write_text(
            "homeassistant:\n"
            "  packages: !include_dir_named packages\n"
            "frontend:\n"
            "  extra_module_url:\n"
            "    - /local/community/wekker-card/wekker-card.js?v=1.9.2\n"
            "lovelace:\n"
            "  dashboards:\n"
            "    wekker-card:\n"
            "      mode: yaml\n"
            "      filename: dashboards/wekker-card.yaml\n"
            "      title: Sonos-wekker\n",
            encoding="utf-8",
        )
        mock_bin = config / "mock-bin"
        mock_bin.mkdir()
        mock_ha = mock_bin / "ha"
        mock_ha.write_text(
            "#!/bin/sh\n"
            "[ \"$1 $2\" = \"core check\" ] || exit 2\n"
            "printf 'MOCK HA CORE CHECK: OK\\n'\n",
            encoding="utf-8",
        )
        mock_ha.chmod(0o755)

        shell_bin = _shell_path(Path(shell).resolve().parent)
        invocation = (
            f"PATH={shlex.quote(mock_bin.relative_to(ROOT).as_posix())}:"
            f"{shlex.quote(shell_bin)}:$PATH; "
            f"sh install.sh --hacs --config {shlex.quote(config.relative_to(ROOT).as_posix())}"
        )
        result = subprocess.run([shell, "-c", invocation], cwd=ROOT, text=True, capture_output=True)
        assert result.returncode == 0, f"HACS-modus mislukt:\n{result.stdout}\n{result.stderr}"
        installed = configuration.read_text(encoding="utf-8")
        assert card_target.read_text(encoding="utf-8") == hacs_contents
        assert "/local/community/wekker-card" not in installed
        assert "extra_module_url" not in installed
        assert (config / "packages" / "wekker_card.yaml").is_file()
        assert "HACS-modus" in result.stdout


def test_successful_canonical_install_removes_zip_and_temporary_tree() -> None:
    shell = os.environ.get("TEST_SH") or shutil.which("bash") or shutil.which("sh")
    if not shell:
        raise RuntimeError("Stel TEST_SH in op een bash/sh-runtime om de installatietest uit te voeren.")

    with tempfile.TemporaryDirectory(prefix=".wekker-card-cleanup-test-", dir=ROOT) as temp:
        config = Path(temp) / "config"
        source = config / "wekker-card"
        (source / "packages").mkdir(parents=True)
        (source / "dashboard").mkdir()
        (source / "custom_cards" / "wekker-card").mkdir(parents=True)
        shutil.copy2(ROOT / "install.sh", source / "install.sh")
        shutil.copy2(PACKAGE, source / "packages" / "wekker_card.yaml")
        shutil.copy2(ROOT / "dashboard" / "wekker-card.yaml", source / "dashboard" / "wekker-card.yaml")
        shutil.copy2(CARD, source / "custom_cards" / "wekker-card" / "wekker-card.js")
        archive = config / "wekker-card-v1.10.0.zip"
        archive.write_bytes(b"test archive")
        (config / "configuration.yaml").write_text(
            "homeassistant:\n  name: Cleanup test\n", encoding="utf-8"
        )
        mock_bin = config / "mock-bin"
        mock_bin.mkdir()
        mock_ha = mock_bin / "ha"
        mock_ha.write_text(
            "#!/bin/sh\n"
            "[ \"$1 $2\" = \"core check\" ] || exit 2\n"
            "printf 'MOCK HA CORE CHECK: OK\\n'\n",
            encoding="utf-8",
        )
        mock_ha.chmod(0o755)

        shell_bin = _shell_path(Path(shell).resolve().parent)
        source_argument = source.relative_to(ROOT).as_posix()
        config_argument = config.relative_to(ROOT).as_posix()
        invocation = (
            f"PATH={shlex.quote(mock_bin.relative_to(ROOT).as_posix())}:"
            f"{shlex.quote(shell_bin)}:$PATH; "
            f"sh {shlex.quote(source_argument)}/install.sh --config {shlex.quote(config_argument)}"
        )
        result = subprocess.run([shell, "-c", invocation], cwd=ROOT, text=True, capture_output=True)
        assert result.returncode == 0, f"cleanup-installatie mislukt:\n{result.stdout}\n{result.stderr}"
        assert not archive.exists()
        assert not source.exists()
        assert (config / "packages" / "wekker_card.yaml").is_file()
        assert (config / "www" / "community" / "wekker-card" / "wekker-card.js").is_file()
        assert list((config / "backups").glob("wekker-card-*"))
        assert "Installatie-ZIP en tijdelijke map" in result.stdout


if __name__ == "__main__":
    tests = [value for name, value in globals().copy().items() if name.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS: {test.__name__}")
    print(f"OK: {len(tests)} release contract tests")
