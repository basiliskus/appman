import os
from pathlib import Path

OS_SUPPORTED = ["linux", "windows", "darwin"]

DATA_PKG = "data"
CONFIG_RES_YAML = "config.yaml"
FORMULAS_RES = "formulas"
PACKAGES_RES = "packages"
PM_RES = "package-managers"

APPMAN_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = Path(APPMAN_DIR).parent

SCHEMAS_DIR = os.path.join(ROOT_DIR, "schemas")
TESTS_DIR = os.path.join(ROOT_DIR, "tests")
DATA_DIR = os.path.join(APPMAN_DIR, DATA_PKG)

PACKAGES_DIR = os.path.join(DATA_DIR, PACKAGES_RES)
FORMULAS_DIR = os.path.join(DATA_DIR, FORMULAS_RES)
PM_DIR = os.path.join(DATA_DIR, PM_RES)
CONFIG_PATH = os.path.join(DATA_DIR, CONFIG_RES_YAML)
