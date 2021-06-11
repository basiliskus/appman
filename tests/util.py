import os

import yaml

# SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
# DATA_PATH = os.path.join(SCRIPT_PATH, os.pardir, "data")
# CONFIG_PATH = os.path.join(SCRIPT_PATH, os.pardir, "data/config.yaml")
# svars = ["tags"]


def get_data_paths(data_root, data_type):
    if data_type == "config":
        fpath = os.path.join(data_root, f"{data_type}.yaml")
        yield fpath

    dpath = os.path.join(data_root, data_type)
    for path, directories, files in os.walk(dpath):
        for name in files:
            fpath = os.path.join(path, name)
            yield fpath


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
