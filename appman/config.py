import os
from pathlib import Path

OS_SUPPORTED = ["linux", "windows", "darwin"]
DEFS_EXT = ".yaml"

DATA_PKG = "appman.data"
CONFIG_RES_YAML = "config.yaml"
FORMULAS_PKG = "appman.data.formulas"
PACKAGES_PKG = "appman.data.packages"
PM_PKG = "appman.data.package-managers"
USER_PKG = "appman.data.user"

APPMAN_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = Path(APPMAN_DIR).parent

SCHEMAS_DIR = os.path.join(ROOT_DIR, "schemas")
TESTS_DIR = os.path.join(ROOT_DIR, "tests")
DATA_DIR = os.path.join(APPMAN_DIR, "data")

PACKAGES_DIR = os.path.join(DATA_DIR, "packages")
FORMULAS_DIR = os.path.join(DATA_DIR, "formulas")
PM_DIR = os.path.join(DATA_DIR, "package-managers")
CONFIG_PATH = os.path.join(DATA_DIR, CONFIG_RES_YAML)
