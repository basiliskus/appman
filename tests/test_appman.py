import pytest

from .context import appman
from . import args


@pytest.fixture
def appm():
    return appman.AppMan()


@pytest.mark.parametrize(
    "action, os, pt, pmid",
    [("install", "linux", "app", "curl")],
)
def test_get_packages_by_id(appm, action, os, pt, pmid):
    package = appm.get_package(pt, pmid)
    formula = package.find_best_formula(os, appm.config)
    if not formula:
        print(f"Formula not found for: {package.name}")
        return

    formula.init(test=True)
    package.run(formula, action, test=True)


@pytest.mark.parametrize(
    "action, os, pt, labels",
    [
        ("install", "linux", "app", "essentials"),
        ("install", "windows", "app", "essentials"),
    ],
)
def test_get_packages_by_filters(appm, action, os, pt, labels):
    packages = appm.get_packages(pt, os, labels=labels)
    for package in packages:
        formula = appm.find_best_formula(os, package)
        if not formula:
            print(f"Formula not found for: {package.name}")
            return

        formula.init(test=True)
        package.run(formula, action, test=True)


def test_get_packages_by_type_returns_something(appm):
    os = "linux"
    package_type = "app"
    packages = appm.get_packages(package_type, os)
    assert packages


def test_get_packages_by_label_returns_something(appm):
    os = "linux"
    package_type = "app"
    labels = ["cli"]
    packages = appm.get_packages(package_type, os, labels=labels)
    assert packages


@pytest.mark.parametrize("package", args.packages)
def test_get_packages_by_id_returns_something(appm, package):
    package = appm.get_package(package["pt"], package["id"])
    assert package


@pytest.mark.parametrize("package", args.packages)
def test_get_user_packages_returns_something(appm, package):
    appm.userrepo.packages.append(appman.UserPackage(package["id"], package["pt"]))
    user_packages = appm.get_user_packages(package["pt"])
    assert user_packages


def test_get_user_packages_by_label_returns_something(appm):
    appm.userrepo.packages = []

    package_type = "app"
    cli_labels = ["cli"]
    cli_package = appman.UserPackage("git", package_type, cli_labels)
    appm.userrepo.packages.append(cli_package)

    gui_labels = ["gui"]
    gui_package = appman.UserPackage(
        "microsoft-visual-studio-code", package_type, gui_labels
    )
    appm.userrepo.packages.append(gui_package)

    cli_user_packages = appm.get_user_packages(package_type, labels=cli_labels)
    assert cli_user_packages
    assert len(cli_user_packages) == 1

    gui_user_packages = appm.get_user_packages(package_type, labels=gui_labels)
    assert gui_user_packages
    assert len(gui_user_packages) == 1


def test_get_user_packages_returns_only_os_compatible(appm, apps_multi_os):
    appm.userrepo.packages = []

    for app in apps_multi_os["apps"]:
        appm.userrepo.packages.append(appman.UserPackage(app["id"], "app"))

    for os in apps_multi_os["os_compatible"]:
        found_apps = [pkg.id for pkg in appm.get_user_packages("app", os=os)]
        assert found_apps == apps_multi_os["os_compatible"][os]
