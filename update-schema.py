import os

import yaml

config_path = "./data/config.yaml"
schemas_path = "./schemas"
svars = ["tags"]


def replace_in_file(fpath):
    with open(config_path, encoding="utf-8") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    with open(fpath, encoding="utf-8") as file:
        fdata = file.read()

    found = False
    for svar in svars:
        value = config["defaults"][svar]
        svar = f"${svar}"
        if svar in fdata:
            fdata = fdata.replace(svar, ",".join(map(lambda x: f"'{x}'", value)))
            found = True

    if found:
        with open(fpath, "w") as file:
            file.write(fdata)


def main():
    for path, directories, files in os.walk(schemas_path):
        for name in files:
            fpath = os.path.join(path, name)
            replace_in_file(fpath)


if __name__ == "__main__":
    main()
