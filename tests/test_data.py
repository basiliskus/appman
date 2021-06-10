import os

import yaml
import pytest
import yamale


# @pytest.fixture
def get_data_paths(dtype):
    root = "../data"

    if dtype == "config":
        fpath = os.path.join(root, f"{dtype}.yaml")
        yield fpath

    dpath = os.path.join(root, dtype)
    for path, directories, files in os.walk(dpath):
        for name in files:
            fpath = os.path.join(path, name)
            yield fpath


def test_validate_files():
    for fpath in get_data_paths(""):
        with open(fpath, encoding="utf-8") as file:
            yaml.safe_load(file)


def test_validate_schema():
    sfolder = "../schemas"
    simple = ["vscode", "sublime", "missing"]
    snames = ["config", "packages", "formulas", "package-managers"]
    for sname in snames:
        for fpath in get_data_paths(sname):
            fname = os.path.splitext(os.path.basename(fpath))[0]
            if sname == "package-managers":
                sfname = "formulas.yaml"
            elif fname in simple:
                sfname = f"{sname}-simple.yaml"
            else:
                sfname = f"{sname}.yaml"
            spath = os.path.join(sfolder, sfname)
            schema = yamale.make_schema(spath)
            data = yamale.make_data(fpath)
            yamale.validate(schema, data)
