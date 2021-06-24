import os
from pathlib import Path

OS_SUPPORTED = ["linux", "windows", "darwin"]
DEFS_EXT = ".yaml"

DATA_PKG = "appman.data"
CONFIG_RES_YAML = "config.yaml"
FORMULAS_PKG = "appman.data.formulas"
PACKAGES_PKG = "appman.data.packages"
USER_PKG = "appman.data.user"

PACKAGES_TYPES = [
    {"id": "app", "pkg": "apps"},
    {"id": "backend", "pkg": "backend"},
    {"id": "driver", "pkg": "drivers"},
    {"id": "extension", "pkg": "extensions"},
    {"id": "font", "pkg": "fonts"},
    {"id": "provisioned", "pkg": "provisioned"},
]

APPMAN_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = Path(APPMAN_DIR).parent

SCHEMAS_DIR = os.path.join(ROOT_DIR, "schemas")
TESTS_DIR = os.path.join(ROOT_DIR, "tests")
DATA_DIR = os.path.join(APPMAN_DIR, "data")

PACKAGES_DIR = os.path.join(DATA_DIR, "packages")
USER_DIR = os.path.join(DATA_DIR, "user")
FORMULAS_DIR = os.path.join(DATA_DIR, "formulas")
CONFIG_PATH = os.path.join(DATA_DIR, CONFIG_RES_YAML)
