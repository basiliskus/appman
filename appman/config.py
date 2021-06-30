OS_SUPPORTED = ["linux", "windows", "darwin"]
DEFS_EXT = ".yaml"

DATA_PKG = "appman.data"
CONFIG_RES_YAML = "config.yaml"
FORMULAS_PKG = "appman.data.formulas"
PACKAGES_PKG = "appman.data.packages"
USER_PKG = "appman.data.user"

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
