import platform

import click
import PyInquirer

from . import core
from . import util
from . import config


class BaseCommand(click.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = [
            click.Option(
                ("--package-type", "-pt"),
                type=click.Choice(config.PACKAGES_TYPES),
                help="Package type",
            ),
            click.Option(("--package-id", "-id"), help="Package ID"),
            click.Option(
                ("--labels", "-l"),
                callback=self.parse_labels,
                help="Comma-separated list of labels",
            ),
        ] + self.params

    @staticmethod
    def parse_labels(ctx, param, value):
        if value:
            return value.split(",")


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


@cli.command(cls=BaseCommand)
@click.option("--test", "-t", is_flag=True, help="Print commands without running")
@click.pass_context
def install(ctx, package_id, package_type, labels, test):
    verbose = ctx.obj["verbose"]
    try:
        if not package_type:
            package_type = prompt_package_type()

        run_command(ctx, "install", package_id, package_type, labels, test, verbose)
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command(cls=BaseCommand)
@click.option("--test", "-t", is_flag=True, help="Print commands without running")
@click.pass_context
def uninstall(ctx, package_id, package_type, labels, test):
    verbose = ctx.obj["verbose"]

    try:
        if not package_type:
            package_type = prompt_package_type()

        run_command(ctx, "uninstall", package_id, package_type, labels, test, verbose)
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command(cls=BaseCommand)
@click.pass_context
def search(ctx, package_type, package_id, labels):
    os = ctx.obj["os"]
    appman = ctx.obj["appman"]
    verbose = ctx.obj["verbose"]

    try:
        if not package_type:
            package_type = prompt_package_type()

        if package_id:
            pkg = appman.get_package(package_type, package_id)
            if pkg:
                util.print_info(f"Package definition for '{package_id}' found")
            else:
                util.print_info(f"Package definition for '{package_id}' not found")
            return

        pkgs = appman.get_packages(package_type, os, labels=labels)
        if not pkgs:
            util.print_info("No packages found")
            return

        for pkg in pkgs:
            util.print_info(pkg.id)
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command(cls=BaseCommand)
@click.pass_context
def list(ctx, package_type, package_id, labels):
    verbose = ctx.obj["verbose"]
    appman = ctx.obj["appman"]

    try:
        if not package_type:
            package_type = prompt_package_type()

        if package_id:
            if appman.has_user_package(package_type, package_id):
                util.print_info(f"Package '{package_id}' found")
            else:
                util.print_info(f"Package '{package_id}' not found")
            return

        pkgs = appman.get_user_packages(package_type, labels=labels)
        if not pkgs:
            msg = f"No {package_type} packages found"
            if labels:
                msg += f" with labels: {', '.join(labels)}"
            util.print_info(msg)
            return

        for pkg in pkgs:
            msg = f"  • {pkg.id}"
            if pkg.labels:
                msg += f" ({', '.join(pkg.labels)})"
            util.print_info(msg)
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command(cls=BaseCommand)
@click.option("--interactive", "-i", is_flag=True, help="Enter interactive mode")
@click.pass_context
def add(ctx, package_type, package_id, labels, interactive):
    os = ctx.obj["os"]
    verbose = ctx.obj["verbose"]
    appman = ctx.obj["appman"]

    try:
        if interactive or not (package_type and package_id):
            if not package_type:
                package_type = prompt_package_type()

            pkgs = appman.get_packages(package_type, os)
            if not pkgs:
                util.print_warning(f"No {package_type} package definitions found")
                return
            usr_pkgs = appman.get_user_packages(package_type)
            qname = "add"
            choices = get_user_packages_choices(pkgs, usr_pkgs, qname)
            if not choices:
                util.print_warning(f"No {package_type} package definitions found")
                return
            questions = get_prompt_questions(
                "checkbox", f"Select {package_type} packages to add:", qname, choices
            )
            answers = PyInquirer.prompt(questions)
            pids = answers[qname]
            for pid in pids:
                pkg = appman.get_package(package_type, pid)
                appman.add_user_package(pkg, labels)
                util.print_success(f"Added {pid} package")
            return

        pkg = appman.get_package(package_type, package_id)
        if not pkg:
            util.print_info(f"Package definition for '{package_id}' not found")
            pkgs = appman.get_packages(package_type, os)
            if pkgs:
                util.print_info(
                    f"You can choose from this list: {', '.join([p.id for p in pkgs])}"
                )
            return

        if appman.has_user_package(package_type, package_id):
            util.print_warning(f"Package '{package_id}' already found")
            return

        appman.add_user_package(pkg, labels)
        util.print_success(f"Package '{package_id}' added")
    except Exception as e:
        e.verbose = verbose
        raise


@cli.command(cls=BaseCommand)
@click.option("--interactive", "-i", is_flag=True, help="Enter interactive mode")
@click.pass_context
def remove(ctx, package_type, package_id, labels, interactive):
    os = ctx.obj["os"]
    verbose = ctx.obj["verbose"]
    appman = ctx.obj["appman"]

    try:
        if interactive or not (package_type and package_id):
            if not package_type:
                package_type = prompt_package_type()

            usr_pkgs = appman.get_user_packages(package_type, labels=labels)
            if not usr_pkgs:
                util.print_warning(f"No {package_type} user packages found")
                return
            qname = "remove"
            pkgs = appman.get_packages(package_type, os)
            choices = get_user_packages_choices(pkgs, usr_pkgs, qname)
            if not choices:
                util.print_warning(
                    f"No matching {package_type} package definitions found"
                )
                return
            questions = get_prompt_questions(
                "checkbox", f"Select {package_type} packages to remove:", qname, choices
            )
            answers = PyInquirer.prompt(questions)
            pids = answers[qname]
            for pid in pids:
                usr_pkg = appman.get_user_package(package_type, pid)
                appman.remove_user_package(usr_pkg)
                util.print_success(f"Removed {pid} package")
            return

        usr_pkg = appman.get_user_package(package_type, package_id)
        if not usr_pkg:
            util.print_warning(f"Package '{package_id}' was not found")
            pkgs = appman.get_user_packages(package_type, labels=labels)
            if pkgs:
                util.print_info(
                    f"You can choose from this list: {', '.join([p.id for p in pkgs])}"
                )
            return
        appman.remove_user_package(usr_pkg)
        util.print_success(f"Package '{package_id}' removed")
    except Exception as e:
        e.verbose = verbose
        raise


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


def prompt_package_type(suffix="", choices=config.ptchoices()):
    choice_list = choices.keys() if isinstance(choices, dict) else choices
    questions = get_prompt_questions(
        "list", "Select the package type:", "ptype", choice_list
    )
    answers = PyInquirer.prompt(questions)
    ptype = f"{suffix}-{answers['ptype']}" if suffix else answers["ptype"]
    if isinstance(choices, dict) and choices[ptype]:
        return prompt_package_type(ptype, choices[ptype])
    return ptype


def run_command(ctx, action, package_id, package_type, labels, test, verbose):
    os = ctx.obj["os"]
    appman = ctx.obj["appman"]

    if package_id:
        if not appman.has_user_package(package_type, package_id):
            util.print_info(
                f"Package '{package_id}' not found. Make sure to add it first"
            )
            return
        package = appman.get_package(package_type, package_id)
        package_run(package, action, appman, os, test, verbose, idprovided=True)
    else:
        packages = appman.get_user_packages(package_type, labels=labels)
        if not packages:
            msg = f"No {package_type} packages found"
            if labels:
                msg += f" with labels: {', '.join(labels)}"
            msg += ". Make sure to add them first"
            util.print_info(msg)
            return

        for pkg in packages:
            package = appman.get_package(pkg.type, pkg.id)
            if package:
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
