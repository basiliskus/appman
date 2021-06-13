import pytest
from click.testing import CliRunner

from .context import appman


cliargs = {
    "action": ["init", "install", "uninstall", "update-all"],
    "os": ["windows", "linux"],
    "package-type": [
        "cli",
        "gui",
        "backend",
        "fonts",
        "drivers",
        "vscode",
        "provisioned",
    ],
    "label": ["", "essentials", "dev", "utils"],
    "shell": ["", "cmd", "powershell"],
    "no-init": [True, False],
    "sudo": [True, False],
    "global": [True, False],
    "package-name": [
        "oh-my-zsh",
        "yq",
        "microsoft-visual-studio-code",
        "focusrite-control",
        "chocolatey-cli",
    ],
}

packages = {
    "oh-my-zsh": {"name": "oh-my-zsh", "os": "linux", "pt": "cli"},
    "yq": {"name": "yq", "os": "linux", "pt": "cli"},
    "microsoft-visual-studio-code": {
        "name": "microsoft-visual-studio-code",
        "os": "linux",
        "pt": "gui",
    },
    "focusrite-control": {
        "name": "Focusrite Control",
        "os": "windows",
        "pt": "drivers",
    },
    "chocolatey-cli": {
        "name": "Chocolatey CLI",
        "os": "windows",
        "pt": "drivers",
        "shell": "powershell",
    },
}


def test_entrypoint():
    runner = CliRunner()
    result = runner.invoke(appman.cli, ["--help"])
    assert result.exit_code == 0


@pytest.mark.parametrize("os", cliargs["os"])
@pytest.mark.parametrize("package_type", cliargs["package-type"])
@pytest.mark.parametrize("package_name", cliargs["package-name"])
@pytest.mark.parametrize("shell", cliargs["shell"])
@pytest.mark.parametrize("sudo", cliargs["sudo"])
@pytest.mark.parametrize("allusers", cliargs["global"])
@pytest.mark.parametrize("no_init", cliargs["no-init"])
def test_install_single_package(
    packages_root, os, package_type, package_name, shell, sudo, allusers, no_init
):
    args = ["--packages-path", packages_root]
    args += ["--test"]
    args += ["run", "install"]
    args += ["--os", os]
    args += ["--package-type", package_type]
    args += ["--package-name", package_name]
    if shell:
        args += ["--shell", shell]
    if no_init:
        args += ["--no-init"]
    if sudo:
        args += ["--sudo"]
    # if allusers:
    #     args += ["--global"]
    runner = CliRunner()
    result = runner.invoke(appman.cli, args)
    result.exception
    assert result.exit_code == 0


@pytest.mark.parametrize("os", cliargs["os"])
@pytest.mark.parametrize("package_type", cliargs["package-type"])
@pytest.mark.parametrize("label", cliargs["label"])
@pytest.mark.parametrize("shell", cliargs["shell"])
@pytest.mark.parametrize("sudo", cliargs["sudo"])
@pytest.mark.parametrize("allusers", cliargs["global"])
@pytest.mark.parametrize("no_init", cliargs["no-init"])
def test_install_multiple_packages(
    packages_root, os, package_type, label, shell, sudo, allusers, no_init
):
    args = ["--packages-path", packages_root]
    args += ["--test"]
    args += ["run", "install"]
    args += ["--os", os]
    args += ["--package-type", package_type]
    if label:
        args += ["--label", label]
    if shell:
        args += ["--shell", shell]
    if no_init:
        args += ["--no-init"]
    if sudo:
        args += ["--sudo"]
    # if allusers:
    #     args += ["--global"]
    runner = CliRunner()
    result = runner.invoke(appman.cli, args)
    assert result.exit_code == 0
