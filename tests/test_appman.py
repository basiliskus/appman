import os

import pytest

from appman import AppMan

test = True
os = ["windows", "linux", "macos"]
action = ["init", "install", "uninstall", "update-all"]
pt = ["cli", "gui", "backend", "fonts", "drivers", "vscode", "provisioned"]
label = ["essentials", "development", "communication", "browser"]
shell = ["cmd", "powershell"]
noinit = [True, False]
sudo = [True, False]
allusers = [True, False]

testdata = [
    ("install", "linux", "cli", "essentials", "", False, False, False),
    ("install", "windows", "cli", "essentials", "", False, False, False),
]


@pytest.fixture
def appman(data_root):
    return AppMan(data_root)


@pytest.mark.parametrize(
    "action, os, pt, label, shell, allusers, noinit, sudo", testdata
)
def test_one(appman, action, os, pt, label, shell, allusers, noinit, sudo):
    pn = "curl"
    package = appman.get_package(pt, pn)
    formula = appman.find_best_formula(os, package)
    if not formula:
        print(f"Formula not found for: {package.name}")
        return

    if not noinit:
        formula.init(test)
    package.run(formula, action, shell, sudo, allusers, test)


@pytest.mark.parametrize(
    "action, os, pt, label, shell, allusers, noinit, sudo", testdata
)
def test_two(appman, action, os, pt, label, shell, allusers, noinit, sudo):
    packages = appman.get_packages(os, pt, label)
    for package in packages:
        formula = appman.find_best_formula(os, package)
        if not formula:
            print(f"Formula not found for: {package.name}")
            return

        if not noinit:
            formula.init(test)
        package.run(formula, action, shell, sudo, allusers, test)
