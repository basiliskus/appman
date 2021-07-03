import os
import logging
import pathlib

# from importlib import resources
# for now using importlib_resources instead of importlib
# for compatibility with python 3.8
import importlib_resources as resources
import click

from . import config

DATEFMT = "%Y/%m/%d %H:%M:%S"


# https://stackoverflow.com/a/56944256/13333330
class CustomFormatter(logging.Formatter):
    grey = "\x1b[38m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;21m"
    reset = "\x1b[0m"
    format = "%(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, DATEFMT)
        return formatter.format(record)


class AppmanLogger:
    datefmt = "%Y/%m/%d %H:%M:%S"

    def __init__(self, script_path, file_log_level=None, console_log_level="DEBUG"):
        name = pathlib.Path(script_path).stem
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        if console_log_level is not None:
            ch = logging.StreamHandler()
            chlevel = getattr(logging, console_log_level.upper())
            ch.setLevel(chlevel)
            ch.setFormatter(CustomFormatter())
            logger.addHandler(ch)

        if file_log_level is not None:
            fhformat = "%(asctime)s - %(levelname)s - %(message)s"
            path = resources.files(config.LOGS_PKG)
            log_path = os.path.join(path, f"{name}.log")
            fh = logging.FileHandler(log_path)
            fhlevel = getattr(logging, file_log_level.upper())
            fh.setLevel(fhlevel)
            fh.setFormatter(logging.Formatter(fhformat, DATEFMT))
            logger.addHandler(fh)

        self.logger = logger

    def console(self, msg):
        click.echo(msg)

    def info(self, msg):
        self.logger.info(msg)

    def success(self, msg):
        click.secho(msg, fg="green")

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)
