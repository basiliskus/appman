import platform

import click

from . import core
from . import util
from . import config


# class RunCommand(click.Command):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.params.append = [
#             click.Option(
#                 "--package-type",
#                 "-pt",
#                 type=click.Choice(
#                     [
#                         "cli",
#                         "gui",
#                         "backend",
#                         "fonts",
#                         "drivers",
#                         "vscode",
#                         "provisioned",
#                     ],
#                     case_sensitive=False,
#                 ),
#                 help="Package type",
#             ),
#             click.Option("--package-id", "-id", help="Package ID"),
#             click.Option("--label", help="Package label"),
#             click.Option(
#                 "--test", "-t", is_flag=True, help="Print commands without running"
#             ),
#         ] + self.params


@click.group()
# @click.option(
#     "--data-path",
#     "-d",
#     type=click.Path(exists=True, file_okay=False, writable=True),
#     default="data",
#     help="Specify data path",
# )
@click.version_option(message="%(prog)s %(version)s")
@click.pass_context
def cli(ctx):
    am = core.AppMan()
    ctx.obj = {"appman": am}


# @cli.command(cls=RunCommand)
@cli.command()
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
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--test", "-t", is_flag=True, help="Print commands without running")
@click.pass_context
def install(ctx, package_id, package_type, label, verbose, test):
    try:
        run_command(ctx, "install", package_id, package_type, label, test, verbose)
    except Exception as e:
        e.verbose = verbose
        raise


def run_command(ctx, action, package_id, package_type, label, test, verbose):
    os = platform.system().lower()
    if os not in config.OS_SUPPORTED:
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
