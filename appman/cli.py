import platform

import click

from . import core
from . import util
from . import config


PT_CHOICES = [
    "cli",
    "gui",
    "backend",
    "fonts",
    "drivers",
    "vscode",
    "provisioned",
]


class RunCommand(click.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = [
            click.Argument(
                ("package-type",),
                type=click.Choice(
                    PT_CHOICES,
                    case_sensitive=False,
                ),
            ),
            click.Option(("--package-id", "-id"), help="Package ID"),
            click.Option(("--label",), help="Package label"),
            click.Option(
                ("--test", "-t"), is_flag=True, help="Print commands without running"
            ),
        ] + self.params


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Print error stacktrace")
@click.version_option(message="%(prog)s %(version)s")
@click.pass_context
def cli(ctx, verbose):
    try:
        os = platform.system().lower()
        if os not in config.OS_SUPPORTED:
            util.print_error(f"{os} is not supported")
            return

        am = core.AppMan()
        ctx.obj = {"appman": am, "os": os, "verbose": verbose}
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command(cls=RunCommand)
@click.pass_context
def install(ctx, package_id, package_type, label, test):
    verbose = ctx.obj["verbose"]
    try:
        run_command(ctx, "install", package_id, package_type, label, test, verbose)
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command(cls=RunCommand)
@click.pass_context
def uninstall(ctx, package_id, package_type, label, test):
    verbose = ctx.obj["verbose"]
    try:
        run_command(ctx, "uninstall", package_id, package_type, label, test, verbose)
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command()
@click.argument("package-type", type=click.Choice(PT_CHOICES, case_sensitive=False))
@click.option("--id", help="Package id")
@click.option("--labels", help="Package labels")
@click.pass_context
def search(ctx, package_type, id, labels):
    os = ctx.obj["os"]
    appman = ctx.obj["appman"]

    if id:
        pkg = find_package(appman, package_type, id)
        if pkg:
            util.print_info(f"Package '{id}' found")
        return

    pkgs = find_packages(appman, package_type, os, label=labels)
    if not pkgs:
        return

    for pkg in pkgs:
        util.print_info(pkg.id)


@cli.command()
@click.argument("package-type", type=click.Choice(PT_CHOICES, case_sensitive=False))
@click.option("--labels", help="Package labels")
@click.pass_context
def list(ctx, package_type, labels):
    verbose = ctx.obj["verbose"]
    try:
        appman = ctx.obj["appman"]
        pkgs = appman.get_user_packages(package_type, labels)
        for pkg in pkgs:
            util.print_info(f"* {pkg.id} (labels: {','.join(pkg.labels)})")
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command()
@click.argument("package-type", type=click.Choice(PT_CHOICES, case_sensitive=False))
@click.option("--id", help="Package id")
@click.option("--labels", help="Package labels")
@click.pass_context
def add(ctx, package_type, id, labels):
    verbose = ctx.obj["verbose"]
    try:
        appman = ctx.obj["appman"]
        pkg = find_package(appman, package_type, id)
        if not pkg:
            return
        if appman.get_user_package(package_type, id):
            util.print_warning(f"Package '{id}' already found")
            return
        appman.add_user_package(pkg, labels)
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command()
@click.argument("package-type", type=click.Choice(PT_CHOICES, case_sensitive=False))
@click.option("--id", help="Package id")
@click.pass_context
def delete(ctx, package_type, id):
    verbose = ctx.obj["verbose"]
    try:
        appman = ctx.obj["appman"]
        usr_pkg = appman.get_user_package(package_type, id)
        if not usr_pkg:
            util.print_warning(f"Package '{id}' was not found")
            return
        appman.delete_user_package(usr_pkg)
        util.print_success(f"Package '{id}' removed")
    except Exception as e:
        e.verbose = verbose
        raise


def find_package(appman, package_type, id):
    pkg = appman.get_package(package_type, id)
    if pkg:
        return pkg
    util.print_info(f"Package '{id}' not found")


def find_packages(appman, package_type, os, label):
    packages = appman.get_packages(package_type, os, label)
    if packages:
        return packages
    util.print_info("No packages found")


def run_command(ctx, action, package_id, package_type, label, test, verbose):
    os = ctx.obj["os"]
    appman = ctx.obj["appman"]
    if package_id:
        package = find_package(appman, package_type, package_id)
        if package:
            package_run(package, action, appman, os, test, verbose, idprovided=True)
    else:
        packages = find_packages(appman, package_type, os, label)
        if not packages:
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
