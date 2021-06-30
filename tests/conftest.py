import os
import pytest
from pathlib import Path

from appman import config


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = Path(TESTS_DIR).parent
APPMAN_DIR = os.path.join(ROOT_DIR, "appman")
BUCKET_DIR = os.path.join(APPMAN_DIR, "buckets/main")


@pytest.fixture
def config_path():
    return os.path.join(BUCKET_DIR, config.CONFIG_RES_YAML)


@pytest.fixture
def bucket_root():
    return BUCKET_DIR


@pytest.fixture
def schemas_root():
    return os.path.join(ROOT_DIR, "schemas")


@pytest.fixture
def packages_root():
    return os.path.join(BUCKET_DIR, "packages")


@pytest.fixture
def user_data_root():
    return os.path.join(APPMAN_DIR, "user/data")


@pytest.fixture
def svars():
    return ["tags"]
