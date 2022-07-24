import platform

import click
import distro
from InquirerPy import prompt

from . import log
from . import core
from . import util
from . import config


logger = log.AppmanLogger(__file__, "DEBUG", "DEBUG")


class BaseCommand(click.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = [
            click.Option(
                ("--package-type", "-pt"),
                type=click.Choice(util.get_package_types()),
                help="Package type",
            ),
            click.Option(("--package-id", "-id"), help="Package ID"),
            click.Option(
                ("--labels", "-l"),
                callback=self.parse_labels,
                help="Comma-separated list of labels",
            ),
            click.Option(
                ("--os", "-os"), help="If no OS given, will use current detected OS"
            ),
            click.Option(
                ("--quiet", "-q"), is_flag=True, help="Print minimum information"
            ),
            click.Option(
                ("--verbose", "-v"), is_flag=True, help="Print debugging information"
            ),
        ] + self.params

    @staticmethod
    def parse_labels(ctx, param, value):
        if value:
            return value.split(",")


@click.group()
@click.version_option(message="%(prog)s %(version)s")
@click.pass_context
def cli(ctx):
    """Cross-platform application management aggregator"""
    try:
        os = platform.system().lower()
        if os not in config.OS_SUPPORTED:
            logger.error(f"{os} is not supported")
            return

        if os == "linux":
            os = distro.id()

        am = core.AppMan()
        ctx.obj = {"appman": am, "os": os}
    except Exception as e:
        e.verbose = True
        raise


@cli.command(cls=BaseCommand, short_help="Install packages in user list")
@click.option("--test", "-t", is_flag=True, help="Print commands without running")
@click.pass_context
def install(ctx, package_id, package_type, labels, os, verbose, quiet, test):
    """Install packages in user list"""
    try:
        if not package_type:
            package_type = prompt_package_type()

        run_command(
            ctx, "install", package_id, package_type, labels, os, test, verbose, quiet
        )
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command(cls=BaseCommand, short_help="Uninstall packages in user list")
@click.option("--test", "-t", is_flag=True, help="Print commands without running")
@click.pass_context
def uninstall(ctx, package_id, package_type, labels, os, verbose, quiet, test):
    """Uninstall packages in user list"""
    try:
        if not package_type:
            package_type = prompt_package_type()

        run_command(
            ctx, "uninstall", package_id, package_type, labels, os, test, verbose, quiet
        )
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command(cls=BaseCommand, short_help="Search for packages available in source repo")
@click.pass_context
def search(ctx, package_type, package_id, labels, os, verbose, quiet):
    """Search for packages available in source repo"""
    os = os or ctx.obj["os"]
    appman = ctx.obj["appman"]

    try:
        if not package_type:
            package_type = prompt_package_type()
        if package_id:
            pkg = appman.get_package(package_type, package_id)
            if pkg:
                logger.console(f"Package definition for {package_id} found")
            else:
                logger.console(f"Package definition for {package_id} not found")
            return

        pkgs = appman.get_packages(package_type, os, labels=labels)
        if not pkgs:
            logger.console("No packages found")
            return

        for pkg in pkgs:
            logger.console(f"  • {pkg.id}")
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command(cls=BaseCommand, short_help="List packages added by user")
@click.pass_context
def list(ctx, package_type, package_id, labels, os, verbose, quiet):
    """List packages added by user"""
    os = os or ctx.obj["os"]
    appman = ctx.obj["appman"]

    try:
        if not package_type:
            package_type = prompt_package_type()

        if package_id:
            if appman.has_user_package(package_type, package_id):
                logger.console(f"Package {package_id} found")
            else:
                logger.console(f"Package {package_id} not found")
            return

        pkgs = appman.get_user_packages(package_type, os=os, labels=labels)
        if not pkgs:
            msg = f"No {package_type} packages found"
            if labels:
                msg += f" with labels: {', '.join(labels)}"
            logger.console(msg)
            return

        for pkg in pkgs:
            msg = f"  • {pkg.id}"
            if pkg.labels:
                msg += f" ({', '.join(pkg.labels)})"
            logger.console(msg)
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command(cls=BaseCommand, short_help="Add package to user list")
@click.option("--interactive", "-i", is_flag=True, help="Enter interactive mode")
@click.pass_context
def add(ctx, package_type, package_id, labels, os, verbose, quiet, interactive):
    """Add package to user list"""
    os = os or ctx.obj["os"]
    appman = ctx.obj["appman"]

    try:
        if interactive or not (package_type and package_id):
            if not package_type:
                package_type = prompt_package_type()

            pkgs = appman.get_packages(package_type, os)
            if not pkgs:
                logger.warning(f"No {package_type} package definitions found")
                return
            usr_pkgs = appman.get_user_packages(package_type)
            qname = "add"
            choices = get_user_packages_choices(pkgs, usr_pkgs, qname)
            if not choices:
                logger.warning(f"No {package_type} package definitions found")
                return
            questions = get_prompt_questions(
                "checkbox", f"Select {package_type} packages to add:", qname, choices
            )
            answers = prompt(questions)
            pids = answers[qname]
            for pid in pids:
                pkg = appman.get_package(package_type, pid)
                appman.add_user_package(pkg, labels)
                logger.success(f"Added {pid} package")
            return

        pkg = appman.get_package(package_type, package_id)
        if not pkg:
            logger.warning(f"Package definition for '{package_id}' not found")
            pkgs = appman.get_packages(package_type, os)
            if pkgs:
                logger.console(
                    f"You can choose from this list: {', '.join([p.id for p in pkgs])}"
                )
            return

        if appman.has_user_package(package_type, package_id):
            logger.warning(f"Package '{package_id}' already found")
            return

        appman.add_user_package(pkg, labels)
        logger.success(f"Added {package_id} package")
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command(cls=BaseCommand, short_help="Remove package from user list")
@click.option("--interactive", "-i", is_flag=True, help="Enter interactive mode")
@click.pass_context
def remove(ctx, package_type, package_id, labels, os, verbose, quiet, interactive):
    """Remove package from user list"""
    os = os or ctx.obj["os"]
    appman = ctx.obj["appman"]

    try:
        if interactive or not (package_type and package_id):
            if not package_type:
                package_type = prompt_package_type()

            usr_pkgs = appman.get_user_packages(package_type, labels=labels)
            if not usr_pkgs:
                logger.warning(f"No {package_type} user packages found")
                return
            qname = "remove"
            pkgs = appman.get_packages(package_type, os)
            choices = get_user_packages_choices(pkgs, usr_pkgs, qname)
            if not choices:
                logger.warning(f"No matching {package_type} package definitions found")
                return
            questions = get_prompt_questions(
                "checkbox", f"Select {package_type} packages to remove:", qname, choices
            )
            answers = prompt(questions)
            pids = answers[qname]
            for pid in pids:
                usr_pkg = appman.get_user_package(package_type, pid)
                appman.remove_user_package(usr_pkg)
                logger.success(f"Removed {pid} package")
            return

        usr_pkg = appman.get_user_package(package_type, package_id)
        if not usr_pkg:
            logger.warning(f"Package '{package_id}' was not found")
            pkgs = appman.get_user_packages(package_type, labels=labels)
            if pkgs:
                logger.console(
                    f"You can choose from this list: {', '.join([p.id for p in pkgs])}"
                )
            return
        appman.remove_user_package(usr_pkg)
        logger.success(f"Removed {package_id} package")
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command(short_help="Update package definitions repository source")
@click.pass_context
def update(ctx):
    appman = ctx.obj["appman"]
    appman.update()


@cli.command(short_help="Set package definitions repository source")
@click.argument("url")
@click.pass_context
def repo(ctx, url):
    appman = ctx.obj["appman"]
    appman.set_repo(url)


def get_prompt_questions(type, message, name, choices):
    return [
        {
            "type": type,
            "message": message,
            "name": name,
            "choices": choices,
        }
    ]


def get_user_packages_choices(packages, user_packages, action):
    result = []
    for p in packages:
        found = any(up for up in user_packages if up.id == p.id)
        choice = {"name": p.name, "value": p.id, "checked": found}
        if action == "remove" and found:
            choice["checked"] = False
            result.append(choice)
        elif (action == "add" and not found) or (action == "update"):
            result.append(choice)
    return result


def prompt_package_type(suffix="", choices=util.get_pt_choices()):
    choice_list = choices.keys() if isinstance(choices, dict) else choices
    questions = get_prompt_questions(
        "list", "Select the package type:", "ptype", choice_list
    )
    answers = prompt(questions)
    ptype = f"{suffix}-{answers['ptype']}" if suffix else answers["ptype"]
    if isinstance(choices, dict) and choices[ptype]:
        return prompt_package_type(ptype, choices[ptype])
    return ptype


def run_command(
    ctx, action, package_id, package_type, labels, os, test, verbose, quiet
):
    os = os or ctx.obj["os"]
    appman = ctx.obj["appman"]

    if package_id:
        if not appman.has_user_package(package_type, package_id):
            logger.info(f"Package '{package_id}' not found. Make sure to add it first")
            return
        package = appman.get_package(package_type, package_id)
        package_run(package, action, appman, os, test, verbose, quiet, idprovided=True)
    else:
        packages = appman.get_user_packages(package_type, os=os, labels=labels)
        if not packages:
            msg = f"No {package_type} packages found"
            if labels:
                msg += f" with labels: {', '.join(labels)}"
            msg += ". Make sure to add them first"
            logger.info(msg)
            return

        for pkg in packages:
            package = appman.get_package(pkg.type, pkg.id)
            if package:
                package_run(package, action, appman, os, test, verbose, quiet)


def package_run(package, action, appman, os, test, verbose, quiet, idprovided=False):
    formula = package.find_best_formula(os, appman.config)

    if not formula:
        logger.warning(f"Formula not found for {package.name}")
        return

    if not test:
        logger.info(f"{util.get_verb(action, 'present').capitalize()} {package.name}")

        verifiable = formula.has_command("installed")
        if verifiable:
            if action == "install" and package.is_installed(formula):
                logger.warning(f"{package.name} is already installed")
                return
            if action == "uninstall" and not package.is_installed(formula):
                logger.warning(f"{package.name} is not installed")
                return
        elif verbose:
            logger.warning(f"Not able to verify if {package.name} is installed")

        if not idprovided:
            formula.init(test, verbose, quiet)

    result = package.run(formula, action, test=test, verbose=verbose, quiet=quiet)

    if test:
        return

    if result.returncode != 0:
        logger.error(f"{package.name} was not {util.get_verb(action, 'past')}")
        return

    if not verifiable:
        logger.warning(f"Not able to verify if {package.name} was installed")
        return

    if (action == "install" and package.is_installed(formula)) or (
        action == "uninstall" and not package.is_installed(formula)
    ):
        logger.success(f"{package.name} {util.get_verb(action, 'past')} successfully")
    else:
        logger.warning(
            f"{package.name} was not {util.get_verb(action, 'past')} successfully"
        )


def main():
    try:
        cli()
    except Exception as e:
        if "verbose" in dir(e) and e.verbose:
            raise
        logger.error(e)
