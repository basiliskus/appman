import click

from . import core
from . import util


@click.group()
@click.option(
    "--packages-path",
    "-p",
    type=click.Path(exists=True, file_okay=False, writable=True),
    default="../data",
    help="Specify data path",
)
@click.option("--test", "-t", is_flag=True, help="Test run")
@click.pass_context
def cli(ctx, packages_path, test):
    am = core.AppMan(packages_path)
    ctx.obj = {
        "appman": am,
        "test": test,
    }


@cli.command()
@click.argument(
    "action",
    type=click.Choice(
        ["init", "install", "uninstall", "update-all"], case_sensitive=False
    ),
)
@click.option(
    "--os",
    "-os",
    type=click.Choice(["windows", "linux", "macos"], case_sensitive=False),
    help="OS type",
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
@click.option("--package-name", "-pn", help="Package name")
@click.option("--label", help="Package label")
@click.option(
    "--shell",
    type=click.Choice(["cmd", "powershell"], case_sensitive=False),
    help="Shell to run commands",
)
# @click.option("--sudo", is_flag=True, help="Run with sudo")
# @click.option("--global", "-g", "allusers", is_flag=True, help="Is global")
@click.option("--no-init", is_flag=True, help="Avoid running initialization scripts")
@click.pass_context
def run(
    ctx,
    action,
    os,
    package_name,
    package_type,
    label,
    shell,
    # sudo,
    # allusers,
    no_init,
):
    appman = ctx.obj["appman"]
    if package_name:
        package = appman.get_package(package_type, package_name)
        if not package:
            util.print_warning(f"Package not found: {package_name}")
            return
        package_run(
            package,
            action,
            appman,
            os,
            shell,
            # sudo,
            # allusers,
            no_init,
            ctx.obj["test"],
        )
    else:
        packages = appman.get_packages(os, package_type, label)
        if not packages:
            util.print_warning(
                f"No packages found for parameters: os={os}, package_type={package_type}, label={label}"
            )
            return
        for package in packages:
            package_run(
                package,
                action,
                appman,
                os,
                shell,
                # sudo,
                # allusers,
                no_init,
                ctx.obj["test"],
            )


def package_run(
    package,
    action,
    appman,
    os,
    shell,
    # sudo,
    # allusers,
    noinit,
    test,
):
    formula = appman.find_best_formula(os, package)
    if not formula:
        util.print_warning(f"Formula not found for: {package.name}")
        return

    if not noinit:
        formula.init(test)
    package.run(formula, action, shell=shell, test=test)


if __name__ == "__main__":
    cli()
