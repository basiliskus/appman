import os
import tempfile

# import pytest

from . import util
from . import args


def test_load_data_files(data_root):
    util.safe_load_yaml_files(data_root)


def test_validate_config_schema(schemas_root, config_path):
    schema_path = os.path.join(schemas_root, "config.yaml")
    util.validate_schema(schema_path, config_path)


def test_validate_formulas_schemas(schemas_root, data_root):
    [spath, dpath] = util.get_validation_files(schemas_root, data_root, "formulas")
    util.validate_data_schema(spath, dpath)


def test_validate_user_schemas(schemas_root, user_root):
    schema_path = os.path.join(schemas_root, "user-packages.yaml")
    util.validate_data_schema(schema_path, user_root)


def test_validate_packages_schema(schemas_root, packages_root, config_path, svars):
    schema_path = os.path.join(schemas_root, "packages.yaml")
    tf = tempfile.NamedTemporaryFile(delete=False)
    for fpath in util.get_file_paths(packages_root):
        if util.replace_in_tmp_file(config_path, schema_path, tf.name, svars):
            spath = tf.name
        util.validate_schema(spath, fpath)
    os.remove(tf.name)


def test_validate_simple_packages_schema(schemas_root, packages_root):
    schema_path = os.path.join(schemas_root, "packages-simple.yaml")
    for fpath in util.get_file_paths(
        packages_root, filter=(lambda x: x in args.simplefiles)
    ):
        util.validate_schema(schema_path, fpath)
