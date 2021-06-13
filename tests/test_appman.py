import pytest

from .context import appman


test = True

test_single_package = [
    ("install", "linux", "cli", "curl", "", False, False, False),
]

test_packages = [
    ("install", "linux", "cli", "essentials", "", False, False, False),
    ("install", "windows", "cli", "essentials", "", False, False, False),
]


@pytest.fixture
def appm(packages_root):
    return appman.AppMan(packages_root)


@pytest.mark.parametrize(
    "action, os, pt, pn, shell, sudo, allusers, noinit", test_single_package
)
def test_get_single_package(appm, action, os, pt, pn, shell, sudo, allusers, noinit):
    package = appm.get_package(pt, pn)
    formula = appm.find_best_formula(os, package)
    if not formula:
        print(f"Formula not found for: {package.name}")
        return

    if not noinit:
        formula.init(test)
    package.run(formula, action, shell, sudo, allusers, test)


@pytest.mark.parametrize(
    "action, os, pt, label, shell, sudo, allusers, noinit", test_packages
)
def test_get_packages_using_filters(
    appm, action, os, pt, label, shell, sudo, allusers, noinit
):
    packages = appm.get_packages(os, pt, label)
    for package in packages:
        formula = appm.find_best_formula(os, package)
        if not formula:
            print(f"Formula not found for: {package.name}")
            return

        if not noinit:
            formula.init(test)
        package.run(formula, action, shell, sudo, allusers, test)
