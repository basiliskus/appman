import os
from pathlib import Path

APPMAN_DIR = os.path.dirname(os.path.abspath(__file__))

ROOT_DIR = Path(APPMAN_DIR).parent

DATA_DIR = os.path.join(ROOT_DIR, "data")
SCHEMAS_DIR = os.path.join(ROOT_DIR, "schemas")
TESTS_DIR = os.path.join(ROOT_DIR, "tests")

FORMULAS_DIR = os.path.join(DATA_DIR, "formulas")
PM_DIR = os.path.join(DATA_DIR, "package-managers")
CONFIG_PATH = os.path.join(DATA_DIR, "config.yaml")

PACKAGES_DIR = os.path.join(TESTS_DIR, "fixtures")
