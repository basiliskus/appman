import os
import pytest
from pathlib import Path

from appman import config


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = Path(TESTS_DIR).parent
APPMAN_DIR = os.path.join(ROOT_DIR, "appman")
REPO_DIR = os.path.join(APPMAN_DIR, "repo")


@pytest.fixture
def config_path():
    return os.path.join(REPO_DIR, config.CONFIG_RES_YAML)


@pytest.fixture
def repo_root():
    return REPO_DIR


@pytest.fixture
def repo_package():
    return config.REPO_PKG


@pytest.fixture
def schemas_root():
    return os.path.join(ROOT_DIR, "schemas")


@pytest.fixture
def packages_root():
    return os.path.join(REPO_DIR, "packages")


@pytest.fixture
def user_data_root():
    return os.path.join(APPMAN_DIR, "user/data")


@pytest.fixture
def user_data_package():
    return config.USER_DATA_PKG


@pytest.fixture
def svars():
    return ["tags"]


@pytest.fixture
def apps_multi_os():
    return {
        "apps": [
            {"id": "7zip", "labels": []},
            {"id": "winmerge", "labels": []},
            {"id": "zsh", "labels": []},
        ],
        "os_compatible": {
            "windows": ["7zip", "winmerge"],
            "ubuntu": ["7zip", "zsh"],
        },
    }
