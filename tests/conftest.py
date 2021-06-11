import os
import pytest

from appman import config


def pytest_addoption(parser):
    parser.addoption(
        "--packages-path", action="store", help="Path to packages defintion folder"
    )


@pytest.fixture
def packages_root(request):
    ppath = request.config.getoption("--packages-path")
    return os.path.join(config.ROOT_DIR, ppath)


@pytest.fixture
def data_root():
    return config.DATA_DIR


@pytest.fixture
def schemas_root():
    return config.SCHEMAS_DIR


@pytest.fixture
def config_path():
    return os.path.join(config.DATA_DIR, "config.yaml")


@pytest.fixture
def svars():
    return ["tags"]


# def pytest_generate_tests(metafunc):
#     option_value = metafunc.config.option.datapath
#     if "datapath" in metafunc.fixturenames and option_value is not None:
#         metafunc.parametrize("datapath", [option_value])
