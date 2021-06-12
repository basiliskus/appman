import click

from . import core


@click.group()
@click.option(
    "--yaml-dir",
    "-f",
    type=click.Path(exists=True, file_okay=False, writable=True),
    default="../data",
    help="Specify data path",
)
@click.option("--test", "-t", is_flag=True, help="Test run")
@click.pass_context
def cli(ctx, yaml_dir, test):
    am = core.AppMan(yaml_dir)
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
@click.option("--packagename", "-pn", help="Package name")
@click.option(
    "--packagetype",
    "-pt",
    type=click.Choice(
        ["cli", "gui", "backend", "fonts", "drivers", "vscode", "provisioned"],
        case_sensitive=False,
    ),
    help="Package type",
)
@click.option(
    "--label",
    type=click.Choice(
        ["essentials", "development", "communication", "browser"], case_sensitive=False
    ),
    help="Package label",
)
@click.option(
    "--shell",
    type=click.Choice(["cmd", "powershell"], case_sensitive=False),
    help="Shell to run commands",
)
@click.option("--sudo", is_flag=True, help="Run with sudo")
@click.option("--global", "-g", "allusers", is_flag=True, help="Is global")
@click.option("--no-init", is_flag=True, help="Avoid running initialization scripts")
@click.pass_context
def run(
    ctx,
    action,
    os,
    packagename,
    packagetype,
    label,
    shell,
    sudo,
    allusers,
    no_init,
):
    appman = ctx.obj["appman"]
    if packagename:
        package = appman.get_package(packagetype, packagename)
        package_run(
            package,
            action,
            appman,
            os,
            shell,
            sudo,
            allusers,
            no_init,
            ctx.obj["test"],
        )
    else:
        packages = appman.get_packages(os, packagetype, label)
        for package in packages:
            package_run(
                package,
                action,
                appman,
                os,
                shell,
                sudo,
                allusers,
                no_init,
                ctx.obj["test"],
            )


def package_run(
    package,
    action,
    appman,
    os,
    shell,
    sudo,
    allusers,
    noinit,
    test,
):
    formula = appman.find_best_formula(os, package)
    if not formula:
        print(f"Formula not found for: {package.name}")
        return

    if not noinit:
        formula.init(test)
    package.run(formula, action, shell, sudo, allusers, test)


if __name__ == "__main__":
    cli()
