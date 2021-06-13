import click


def print_success(msg):
    click.secho(msg, fg="green")


def print_warning(msg):
    click.secho(msg, fg="yellow")


def print_error(msg):
    click.secho(msg, fg="red")
