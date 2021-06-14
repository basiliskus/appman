import os

import pytest

from appman import config


def pytest_addoption(parser):
    parser.addoption(
        "--packages-path", action="store", help="Path to packages definition folder"
    )
    parser.addoption(
        "--config",
        action="store",
        default="config.yaml",
        help="Name for the config file",
    )


@pytest.fixture
def packages_root(request):
    ppath = request.config.getoption("--packages-path")
    return os.path.join(config.ROOT_DIR, ppath)


@pytest.fixture
def config_file(request):
    cpath = request.config.getoption("--config")
    return os.path.join(config.ROOT_DIR, cpath)


@pytest.fixture
def data_root():
    return config.DATA_DIR


@pytest.fixture
def schemas_root():
    return config.SCHEMAS_DIR


@pytest.fixture
def config_path(config_file):
    return os.path.join(config.DATA_DIR, config_file)


@pytest.fixture
def svars():
    return ["tags"]


# def pytest_generate_tests(metafunc):
#     option_value = metafunc.config.option.datapath
#     if "datapath" in metafunc.fixturenames and option_value is not None:
#         metafunc.parametrize("datapath", [option_value])
