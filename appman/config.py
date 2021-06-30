OS_SUPPORTED = ["linux", "windows", "darwin"]
DEFS_EXT = ".yaml"

USER_DATA_PKG = "appman.user.data"
BUCKET_PKG = "appman.buckets.main"
BUCKET_FORMULAS_PKG = f"{BUCKET_PKG}.formulas"
BUCKET_PACKAGES_PKG = f"{BUCKET_PKG}.packages"
CONFIG_RES_YAML = "config.yaml"

PACKAGES_TYPES = {
    "app": {"pkg": "apps"},
    "font": {"pkg": "fonts"},
    "driver": {"pkg": "drivers"},
    "provisioned": {"pkg": "provisioned"},
    "backend-node": {"pkg": "backend.node"},
    "backend-python": {"pkg": "backend.python"},
    "extension-vscode": {"pkg": "extensions.vscode"},
}


def ptchoices():
    choices = {}
    for pt in PACKAGES_TYPES.keys():
        v = None
        if "-" in pt:
            pt, v = pt.split("-")
        if not choices or pt not in choices:
            choices[pt] = []
        if v:
            choices[pt].append(v)
    return choices
