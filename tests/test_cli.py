import pytest
from click.testing import CliRunner

from .context import appman
from . import args


def test_entrypoint():
    runner = CliRunner()
    result = runner.invoke(appman.cli, ["--help"])
    assert result.exit_code == 0


@pytest.mark.parametrize("package_type", args.cliargs["package-type"])
@pytest.mark.parametrize("package_id", args.cliargs["package-id"])
def test_install_single_package(package_type, package_id):
    args = ["--verbose"]
    args += ["install"]
    args += [package_type]
    args += ["--package-id", package_id]
    args += ["--test"]
    runner = CliRunner()
    result = runner.invoke(appman.cli, args)
    result.exception
    assert result.exit_code == 0


@pytest.mark.parametrize("package_type", args.cliargs["package-type"])
@pytest.mark.parametrize("labels", args.cliargs["labels"])
def test_install_multiple_packages(package_type, labels):
    args = ["--verbose"]
    args += ["install"]
    args += [package_type]
    if labels:
        args += ["--labels", labels]
    args += ["--test"]
    runner = CliRunner()
    result = runner.invoke(appman.cli, args)
    assert result.exit_code == 0


@pytest.mark.skip(reason="need better test parameters")
@pytest.mark.parametrize("action", args.cliargs["action"])
@pytest.mark.parametrize("package_type", ["cli"])
def test_actions(action, package_type):
    args = [action]
    args += [package_type]
    args += ["--test"]

    runner = CliRunner()
    result = runner.invoke(appman.cli, args)
    assert result.exit_code == 0


# @pytest.mark.parametrize("package_type", args.cliargs["package-type"])
# @pytest.mark.parametrize("labels", args.userlabels)
def test_list_packages():
    package_type = "app"
    labels = "essentials"
    args = ["list"]
    args += [package_type]
    args += ["--labels", labels]
    runner = CliRunner()
    result = runner.invoke(appman.cli, args)
    assert result.exit_code == 0


def test_add_package():
    package_type = "app"
    package_id = "git"
    labels = "essentials,home"
    args = ["add"]
    args += [package_type]
    args += [package_id]
    args += ["--labels", labels]
    runner = CliRunner()
    result = runner.invoke(appman.cli, args)
    assert result.exit_code == 0


def test_delete_package():
    package_type = "app"
    package_id = "git"
    args = ["delete"]
    args += [package_type]
    args += [package_id]
    runner = CliRunner()
    result = runner.invoke(appman.cli, args)
    assert result.exit_code == 0
