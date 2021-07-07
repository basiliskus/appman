import os
import io

from . import config


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


def log_subprocess_output(process, logger):
    buffer = io.BytesIO()
    while True:
        char = process.stdout.read(1)
        buffer.write(char)
        if char in (b"\r", b"\n"):
            line = buffer.getvalue().decode("UTF-8").strip("\x00")
            logger.info(line)
            buffer.truncate(0)

        if process.returncode is not None or process.poll() is not None:
            break


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
