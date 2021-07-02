import click.testing
import pytest

from .context import appman
from . import args


def test_entrypoint():
    runner = click.testing.CliRunner()
    result = runner.invoke(appman.cli, ["--help"])
    assert result.exit_code == 0


def invoke_cli(
    action,
    package_type,
    package_id=None,
    labels=None,
    os=None,
    test=False,
    verbose=False,
):
    args = []
    if verbose:
        args += ["--verbose"]
    args += [action]
    args += ["--package-type", package_type]
    if package_id:
        args += ["--package-id", package_id]
    if labels:
        args += ["--labels", labels]
    if os:
        args += ["--os", os]
    if test:
        args += ["--test"]
    runner = click.testing.CliRunner()
    return runner.invoke(appman.cli, args)


@pytest.mark.parametrize("package", args.packages)
def test_install_single_package(package):
    result = invoke_cli(
        "install", package["pt"], package_id=package["id"], test=True, verbose=True
    )
    result.exception
    assert result.exit_code == 0


@pytest.mark.parametrize("package_type", args.cliargs["package-type"])
@pytest.mark.parametrize("labels", args.cliargs["labels"])
def test_install_multiple_packages(package_type, labels):
    result = invoke_cli("install", package_type, labels=labels, test=True, verbose=True)
    assert result.exit_code == 0


@pytest.mark.parametrize("action", args.cliargs["action"])
@pytest.mark.parametrize("package_type", args.cliargs["package-type"])
def test_actions(action, package_type):
    result = invoke_cli(action, package_type, test=True)
    assert result.exit_code == 0


def test_list_packages():
    result = invoke_cli("list", "app", labels="essentials")
    assert result.exit_code == 0


def test_add_package():
    result = invoke_cli("add", "app", package_id="git", labels="essentials,home")
    assert result.exit_code == 0


def test_remove_package():
    result = invoke_cli("remove", "app", package_id="git")
    assert result.exit_code == 0
