import pytest

from .context import appman
from . import args


@pytest.fixture
def appm(bucket_package):
    return appman.AppMan(bucket_package)


@pytest.mark.parametrize(
    "action, os, pt, pmid",
    [("install", "linux", "app", "curl")],
)
def test_get_packages_by_id(appm, user_data_package, action, os, pt, pmid):
    appm.load_user_data(user_data_package)
    package = appm.get_package(pt, pmid)
    formula = appm.find_best_formula(os, package)
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
def test_get_packages_by_filters(appm, user_data_package, action, os, pt, labels):
    appm.load_user_data(user_data_package)
    packages = appm.get_packages(pt, os, labels=labels)
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
def test_get_packages_by_type_returns_something(
    appm, user_data_package, os, package_type
):
    appm.load_user_data(user_data_package)
    packages = appm.get_packages(package_type, os)
    assert packages


@pytest.mark.skip(reason="need to be more specific about the test parameters")
@pytest.mark.parametrize("os", args.cliargs["os"])
@pytest.mark.parametrize("package_type", ["app"])
@pytest.mark.parametrize("labels", args.cliargs["labels"])
def test_get_packages_by_label_returns_something(
    appm, user_data_package, os, package_type, labels
):
    appm.load_user_data(user_data_package)
    packages = appm.get_packages(package_type, os, labels=labels)
    assert packages


@pytest.mark.parametrize("packages", args.packages)
def test_get_packages_by_id_returns_something(appm, user_data_package, packages):
    appm.load_user_data(user_data_package)
    package = appm.get_package(packages["pt"], packages["id"])
    assert package


def test_list_apps_returns_only_os_compatible(appm, apps_multi_os):
    for app in apps_multi_os["apps"]:
        appm.user_packages.append(appman.UserPackage(app["id"], "app"))

    for os in apps_multi_os["os_compatible"]:
        found_apps = [pkg.id for pkg in appm.get_user_packages("app", os=os)]
        assert found_apps == apps_multi_os["os_compatible"][os]
