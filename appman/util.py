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


def parse_stmsg(msg):
    msg = msg.decode("UTF-8") if isinstance(msg, bytes) else msg
    msg = f"{os.linesep}".join(msg.splitlines()) if isinstance(msg, list) else msg
    return msg.rstrip()


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
