import os

import yaml

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = os.path.join(SCRIPT_PATH, "../data")
CONFIG_PATH = os.path.join(SCRIPT_PATH, "../data/config.yaml")
svars = ["tags"]


def get_data_paths(dtype):
    if dtype == "config":
        fpath = os.path.join(DATA_PATH, f"{dtype}.yaml")
        yield fpath

    dpath = os.path.join(DATA_PATH, dtype)
    for path, directories, files in os.walk(dpath):
        for name in files:
            fpath = os.path.join(path, name)
            yield fpath


def replace_in_tmp_file(DATA_PATH, tmp_path):
    # load config file
    with open(CONFIG_PATH, encoding="utf-8") as file:
        fconfig = yaml.load(file, Loader=yaml.FullLoader)

    # load data file
    with open(DATA_PATH, encoding="utf-8") as file:
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
