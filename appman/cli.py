import platform

import click

from . import core
from . import util


@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, dir_okay=False),
    default="data/config.yaml",
    help="Specify config file path",
)
@click.option(
    "--packages-path",
    "-p",
    type=click.Path(exists=True, file_okay=False, writable=True),
    default="data/packages",
    help="Specify data path",
)
@click.pass_context
def cli(ctx, packages_path, config):
    am = core.AppMan(packages_path, config)
    ctx.obj = {"appman": am}


@cli.command()
@click.argument(
    "action",
    type=click.Choice(["install", "uninstall", "update-all"], case_sensitive=False),
)
@click.option(
    "--package-type",
    "-pt",
    type=click.Choice(
        ["cli", "gui", "backend", "fonts", "drivers", "vscode", "provisioned"],
        case_sensitive=False,
    ),
    help="Package type",
)
@click.option("--package-id", "-id", help="Package ID")
@click.option("--label", help="Package label")
@click.option("--test", "-t", is_flag=True, help="Print commands without running")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def run(ctx, action, package_id, package_type, label, test, verbose):
    try:
        os_supported = ["linux", "windows", "darwin"]
        os = platform.system().lower()
        if os not in os_supported:
            util.print_error(f"{os} is not supported")
            return

        appman = ctx.obj["appman"]
        if package_id:
            package = appman.get_package(package_type, package_id)
            if not package:
                util.print_warning(f"Package not found: {package_id}")
                return
            package_run(package, action, appman, os, test, verbose, idprovided=True)
        else:
            packages = appman.get_packages(os, package_type, label)
            if not packages:
                util.print_warning("No packages found")
                return
            for package in packages:
                package_run(package, action, appman, os, test, verbose)
    except Exception as e:
        e.verbose = verbose
        raise


def package_run(package, action, appman, os, test, verbose, idprovided=False):
    formula = appman.find_best_formula(os, package)

    if not formula:
        util.print_warning(f"Formula not found for {package.name}")
        return

    if not test:
        util.print_info(
            f"{util.get_verb(action, 'present').capitalize()} {package.name}"
        )

    formula.init(test)
    result = package.run(formula, action, test=test, verbose=verbose)

    if test:
        return

    if result.returncode == 0:
        if idprovided:
            util.print_success(
                f"{package.name} {util.get_verb(action, 'past')} successfully"
            )
    else:
        util.print_error(f"{package.name} was not {util.get_verb(action, 'past')}")
        if result.stderr:
            util.print_error(util.parse_stmsg(result.stderr))
        if verbose and result.stdout:
            util.print_info(util.parse_stmsg(result.stdout))


def main():
    try:
        cli()
    except Exception as e:
        if "verbose" in dir(e) and e.verbose:
            raise
        util.print_error(e)
