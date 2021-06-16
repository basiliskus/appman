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
def test_install_single_package(
    packages_root, config_file, os, package_type, package_id
):
    args = ["--config", config_file]
    args += ["--packages-path", packages_root]
    args += ["run", "install"]
    args += ["--os", os]
    args += ["--package-type", package_type]
    args += ["--package-id", package_id]
    args += ["--test"]
    args += ["--verbose"]
    runner = CliRunner()
    result = runner.invoke(appman.cli, args)
    result.exception
    assert result.exit_code == 0


@pytest.mark.parametrize("os", args.cliargs["os"])
@pytest.mark.parametrize("package_type", args.cliargs["package-type"])
@pytest.mark.parametrize("label", args.cliargs["label"])
def test_install_multiple_packages(packages_root, config_file, os, package_type, label):
    args = ["--config", config_file]
    args += ["--packages-path", packages_root]
    args += ["run", "install"]
    args += ["--os", os]
    args += ["--package-type", package_type]
    args += ["--test"]
    args += ["--verbose"]
    if label:
        args += ["--label", label]
    runner = CliRunner()
    result = runner.invoke(appman.cli, args)
    assert result.exit_code == 0


@pytest.mark.skip(reason="need better test parameters")
@pytest.mark.parametrize("action", args.cliargs["action"])
@pytest.mark.parametrize("os", ["linux"])
@pytest.mark.parametrize("package_type", ["cli"])
def test_actions(packages_root, config_file, action, os, package_type):
    args = ["--config", config_file]
    args += ["--packages-path", packages_root]
    args += ["run", action]
    args += ["--os", os]
    args += ["--package-type", package_type]
    args += ["--test"]

    runner = CliRunner()
    result = runner.invoke(appman.cli, args)
    assert result.exit_code == 0
