import pytest

from .context import appman
from . import args


@pytest.fixture
def appm(packages_root):
    return appman.AppMan(packages_root)


@pytest.mark.parametrize(
    "action, os, pt, pmid",
    [("install", "linux", "cli", "curl")],
)
def test_get_packages_by_id(appm, action, os, pt, pmid):
    package = appm.get_package(pt, pmid)
    formula = appm.find_best_formula(os, package)
    if not formula:
        print(f"Formula not found for: {package.name}")
        return

    formula.init(test=True)
    package.run(formula, action, test=True)


@pytest.mark.parametrize(
    "action, os, pt, label",
    [
        ("install", "linux", "cli", "essentials"),
        ("install", "windows", "cli", "essentials"),
    ],
)
def test_get_packages_by_filters(appm, action, os, pt, label):
    packages = appm.get_packages(os, pt, label)
    for package in packages:
        formula = appm.find_best_formula(os, package)
        if not formula:
            print(f"Formula not found for: {package.name}")
            return

        formula.init(test=True)
        package.run(formula, action, test=True)


@pytest.mark.skip(reason="need to be more specific about the test parameters")
@pytest.mark.parametrize("os", args.cliargs["os"])
@pytest.mark.parametrize("package_type", args.cliargs["package-type"])
def test_get_packages_by_type_returns_something(appm, os, package_type):
    packages = appm.get_packages(os, package_type)
    assert packages


@pytest.mark.skip(reason="need to be more specific about the test parameters")
@pytest.mark.parametrize("os", args.cliargs["os"])
@pytest.mark.parametrize("package_type", ["cli", "gui"])
@pytest.mark.parametrize("label", args.cliargs["label"])
def test_get_packages_by_label_returns_something(appm, os, package_type, label):
    packages = appm.get_packages(os, package_type, label)
    assert packages


@pytest.mark.parametrize("packages", args.packages)
def test_get_packages_by_id_returns_something(appm, packages):
    package = appm.get_package(packages["pt"], packages["id"])
    assert package
