import os
import io


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
