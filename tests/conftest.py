import os
import pytest
from pathlib import Path

from appman import config


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = Path(TESTS_DIR).parent
DATA_DIR = os.path.join(ROOT_DIR, "appman", "data")


@pytest.fixture
def config_path():
    return os.path.join(DATA_DIR, config.CONFIG_RES_YAML)


@pytest.fixture
def data_root():
    return DATA_DIR


@pytest.fixture
def schemas_root():
    return os.path.join(ROOT_DIR, "schemas")


@pytest.fixture
def packages_root():
    return os.path.join(DATA_DIR, "packages")


@pytest.fixture
def user_root():
    return os.path.join(DATA_DIR, "user")


@pytest.fixture
def svars():
    return ["tags"]
