import pytest
from click.testing import CliRunner

from .context import appman
from . import args


def test_entrypoint():
    runner = CliRunner()
    result = runner.invoke(appman.cli, ["--help"])
    assert result.exit_code == 0


@pytest.mark.parametrize("os", args.cliargs["os"])
@pytest.mark.parametrize("package_type", args.cliargs["package-type"])
@pytest.mark.parametrize("package_id", args.cliargs["package-id"])
@pytest.mark.parametrize("shell", args.cliargs["shell"])
# @pytest.mark.parametrize("sudo", args.cliargs["sudo"])
# @pytest.mark.parametrize("allusers", args.cliargs["global"])
@pytest.mark.parametrize("no_init", args.cliargs["no-init"])
def test_install_single_package(
    packages_root, config_file, os, package_type, package_id, shell, no_init
):
    args = ["--config", config_file]
    args += ["--packages-path", packages_root]
    args += ["run", "install"]
    args += ["--os", os]
    args += ["--package-type", package_type]
    args += ["--package-id", package_id]
    args += ["--test"]
    args += ["--verbose"]
    if shell:
        args += ["--shell", shell]
    if no_init:
        args += ["--no-init"]
    # if sudo:
    #     args += ["--sudo"]
    # if allusers:
    #     args += ["--global"]
    runner = CliRunner()
    result = runner.invoke(appman.cli, args)
    result.exception
    assert result.exit_code == 0


@pytest.mark.parametrize("os", args.cliargs["os"])
@pytest.mark.parametrize("package_type", args.cliargs["package-type"])
@pytest.mark.parametrize("label", args.cliargs["label"])
@pytest.mark.parametrize("shell", args.cliargs["shell"])
# @pytest.mark.parametrize("sudo", args.cliargs["sudo"])
# @pytest.mark.parametrize("allusers", args.cliargs["global"])
@pytest.mark.parametrize("no_init", args.cliargs["no-init"])
def test_install_multiple_packages(
    packages_root, config_file, os, package_type, label, shell, no_init
):
    args = ["--config", config_file]
    args += ["--packages-path", packages_root]
    args += ["run", "install"]
    args += ["--os", os]
    args += ["--package-type", package_type]
    args += ["--test"]
    args += ["--verbose"]
    if label:
        args += ["--label", label]
    if shell:
        args += ["--shell", shell]
    if no_init:
        args += ["--no-init"]
    # if sudo:
    #     args += ["--sudo"]
    # if allusers:
    #     args += ["--global"]
    runner = CliRunner()
    result = runner.invoke(appman.cli, args)
    assert result.exit_code == 0
