import os

import yaml
import yamale

EXT = ".yaml"


def safe_load_yaml_files(path):
    for fpath in get_file_paths(path):
        with open(fpath, encoding="utf-8") as file:
            yaml.safe_load(file)


def get_file_paths(data_root, filter=None):
    for path, directories, files in os.walk(data_root):
        files = [
            fi for fi in files if fi.endswith(EXT) and (filter is None or filter(fi))
        ]
        for name in files:
            yield os.path.join(path, name)


def get_validation_files(schemas_root, data_root, name):
    schema_path = os.path.join(schemas_root, f"{name}{EXT}")
    data_path = os.path.join(data_root, name)
    return schema_path, data_path


def validate_schema(schema_path, data_path):
    schema = yamale.make_schema(schema_path)
    data = yamale.make_data(data_path)
    yamale.validate(schema, data)


def validate_data_schema(schema_path, root_path):
    for fpath in get_file_paths(root_path):
        validate_schema(schema_path, fpath)


def replace_in_tmp_file(config_path, data_path, tmp_path, svars):
    # load config file
    with open(config_path, encoding="utf-8") as file:
        fconfig = yaml.load(file, Loader=yaml.FullLoader)

    # load data file
    with open(data_path, encoding="utf-8") as file:
        fdata = file.read()

    # replace variables if found in data file
    found = False
    for svar in svars:
        value = fconfig["defaults"][svar]
        svar = f"${svar}"
        if svar in fdata:
            fdata = fdata.replace(svar, ",".join(map(lambda x: f"'{x}'", value)))
            found = True

    if found:
        with open(tmp_path, "w") as file:
            file.write(fdata)

    return found
