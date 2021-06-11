import os
import tempfile

import yaml
import pytest
import yamale

from . import util


def test_validate_files(data_root):
    for fpath in util.get_data_paths(data_root, ""):
        with open(fpath, encoding="utf-8") as file:
            yaml.safe_load(file)


def test_validate_schema(data_root, config_path, schemas_path, svars):
    simple = ["vscode", "sublime", "missing"]
    snames = ["config", "packages", "formulas", "package-managers"]
    tf = tempfile.NamedTemporaryFile(delete=False)
    for sname in snames:
        for fpath in util.get_data_paths(data_root, sname):
            fname = os.path.splitext(os.path.basename(fpath))[0]
            if sname == "package-managers":
                sfname = "formulas.yaml"
            elif fname in simple:
                sfname = f"{sname}-simple.yaml"
            else:
                sfname = f"{sname}.yaml"
            spath = os.path.join(schemas_path, sfname)
            if util.replace_in_tmp_file(config_path, spath, tf.name, svars):
                spath = tf.name
            schema = yamale.make_schema(spath)
            data = yamale.make_data(fpath)
            yamale.validate(schema, data)
    os.remove(tf.name)
