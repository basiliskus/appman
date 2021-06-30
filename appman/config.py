import os
from pathlib import Path

OS_SUPPORTED = ["linux", "windows", "darwin"]
DEFS_EXT = ".yaml"

DATA_PKG = "appman.data"
CONFIG_RES_YAML = "config.yaml"
FORMULAS_PKG = "appman.data.formulas"
PACKAGES_PKG = "appman.data.packages"
USER_PKG = "appman.data.user"


APPMAN_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = Path(APPMAN_DIR).parent

SCHEMAS_DIR = os.path.join(ROOT_DIR, "schemas")
TESTS_DIR = os.path.join(ROOT_DIR, "tests")
DATA_DIR = os.path.join(APPMAN_DIR, "data")

PACKAGES_DIR = os.path.join(DATA_DIR, "packages")
USER_DIR = os.path.join(DATA_DIR, "user")
FORMULAS_DIR = os.path.join(DATA_DIR, "formulas")
CONFIG_PATH = os.path.join(DATA_DIR, CONFIG_RES_YAML)


PACKAGES_TYPES = {
    "app": {"pkg": "apps"},
    "font": {"pkg": "fonts"},
    "driver": {"pkg": "drivers"},
    "provisioned": {"pkg": "provisioned"},
    "backend-node": {"pkg": "backend.node"},
    "backend-python": {"pkg": "backend.python"},
    "extension-vscode": {"pkg": "extensions.vscode"},
}


def ptchoices():
    choices = {}
    for pt in PACKAGES_TYPES.keys():
        v = None
        if "-" in pt:
            pt, v = pt.split("-")
        if not choices or pt not in choices:
            choices[pt] = []
        if v:
            choices[pt].append(v)
    return choices
