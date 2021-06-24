import pytest

from appman import config


@pytest.fixture
def config_path():
    return config.CONFIG_PATH


@pytest.fixture
def data_root():
    return config.DATA_DIR


@pytest.fixture
def schemas_root():
    return config.SCHEMAS_DIR


@pytest.fixture
def packages_root():
    return config.PACKAGES_DIR


@pytest.fixture
def apps_root():
    return config.APPS_DIR


@pytest.fixture
def svars():
    return ["tags"]
