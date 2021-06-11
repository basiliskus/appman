import os
import tempfile

# import pytest

import util


def test_load_data_files(data_root):
    util.safe_load_yaml_files(data_root)


def test_load_package_files(packages_root):
    util.safe_load_yaml_files(packages_root)


def test_validate_config_schema(schemas_root, config_path):
    schema_path = os.path.join(schemas_root, "config.yaml")
    util.validate_schema(schema_path, config_path)


def test_validate_data_schemas(schemas_root, data_root):
    # validate formulas
    [spath, dpath] = util.get_validation_files(schemas_root, data_root, "formulas")
    util.validate_data_schema(spath, dpath)

    # validate package managers
    [_, dpath] = util.get_validation_files(schemas_root, data_root, "package-managers")
    util.validate_data_schema(spath, dpath)


def test_validate_packages_schema(schemas_root, packages_root, config_path, svars):
    simple = ["vscode", "sublime", "missing"]
    tf = tempfile.NamedTemporaryFile(delete=False)
    schema_path = os.path.join(schemas_root, "packages.yaml")
    for fpath in util.get_file_paths(packages_root):
        fname = os.path.splitext(os.path.basename(fpath))[0]
        spath = (
            schema_path.replace(".yaml", "-simple.yaml")
            if fname in simple
            else schema_path
        )
        if util.replace_in_tmp_file(config_path, spath, tf.name, svars):
            spath = tf.name
        util.validate_schema(spath, fpath)
    os.remove(tf.name)
