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


def get_verb(action, tense):
    if "update" in action:
        action = "updat"
    elif action not in ["install", "uninstall"]:
        action = "process"

    if tense == "present":
        return f"{action}ing"
    if tense == "past":
        return f"{action}ed"

    return action
