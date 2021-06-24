import os
import yaml

dpath = "/home/basiliskus/projects/appman/appman/data/packages/provisioned"
fpath = os.path.join(dpath, "provisioned.yaml")
with open(fpath, encoding="utf-8") as file:
    data = yaml.load(file, Loader=yaml.FullLoader)

for d in data:
    d["labels"] = []
    fpath = os.path.join(dpath, f"{d['id']}.yaml")
    with open(fpath, "w", encoding="utf-8") as file:
        yaml.dump(d, file, sort_keys=False)
