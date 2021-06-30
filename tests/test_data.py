import os
import tempfile

from . import util


def test_load_data_files(bucket_root):
    util.safe_load_yaml_files(bucket_root)


def test_validate_config_schema(schemas_root, config_path):
    schema_path = os.path.join(schemas_root, "config.yaml")
    util.validate_schema(schema_path, config_path)


def test_validate_formulas_schemas(schemas_root, bucket_root):
    [spath, dpath] = util.get_validation_files(schemas_root, bucket_root, "formulas")
    util.validate_data_schema(spath, dpath)


def test_validate_user_schemas(schemas_root, user_data_root):
    schema_path = os.path.join(schemas_root, "user-packages.yaml")
    util.validate_data_schema(schema_path, user_data_root)


def test_validate_packages_schema(schemas_root, packages_root, config_path, svars):
    schema_path = os.path.join(schemas_root, "packages.yaml")
    tf = tempfile.NamedTemporaryFile(delete=False)
    for fpath in util.get_file_paths(packages_root):
        if util.replace_in_tmp_file(config_path, schema_path, tf.name, svars):
            spath = tf.name
        util.validate_schema(spath, fpath)
    os.remove(tf.name)
