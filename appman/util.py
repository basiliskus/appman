import sys
import os
import io

from . import config


def parse_stmsg(msg):
    msg = msg.decode("UTF-8") if isinstance(msg, bytes) else msg
    msg = f"{os.linesep}".join(msg.splitlines()) if isinstance(msg, list) else msg
    if isinstance(msg, io.IOBase):
        msg = msg.read()
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


def log_subprocess_output(process, logger):
    while process.poll() is None:
        line = process.stdout.readline()
        if line:
            logger.info(line.strip())
        sys.stdout.flush()


def is_os_compatible(source, dest):
    return (
        (source == dest)
        or (source in "any" or dest in "any")
        or (dest in get_os_family_names(os=source))
    )


def get_os_family_names(data=config.OS, os=None, found=False):
    for e in data:
        if isinstance(e, dict):
            yield from get_os_family_names(e, os, found)
        else:
            include = found or not os or os == e
            if include:
                yield e
            if isinstance(data, dict):
                yield from get_os_family_names(data[e], os, include)
