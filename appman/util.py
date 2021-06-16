import os

import click


def print_info(msg):
    click.echo(msg)


def print_success(msg):
    click.secho(msg, fg="green")


def print_warning(msg):
    click.secho(msg, fg="yellow")


def print_error(msg):
    click.secho(msg, fg="red")


def parse_stmsg(stmsg):
    msg = stmsg.decode("UTF-8") if isinstance(stmsg, bytes) else stmsg
    return f"{os.linesep}".join(msg.splitlines())
