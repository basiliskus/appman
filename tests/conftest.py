import os
import pytest


ROOT_PATH = os.path.dirname(os.path.realpath(__file__))


def pytest_addoption(parser):
    parser.addoption("--datapath", action="store", default="fixtures")


@pytest.fixture
def data_root(request):
    datapath = request.config.getoption("--datapath")
    if datapath == "fixtures":
        datapath = os.path.join(ROOT_PATH, datapath)
    return datapath


@pytest.fixture
def schemas_path():
    return os.path.join(ROOT_PATH, os.pardir, "schemas")


@pytest.fixture
def config_path(data_root):
    return os.path.join(data_root, "config.yaml")


@pytest.fixture
def svars():
    return ["tags"]


# def pytest_generate_tests(metafunc):
#     option_value = metafunc.config.option.datapath
#     if "datapath" in metafunc.fixturenames and option_value is not None:
#         metafunc.parametrize("datapath", [option_value])
