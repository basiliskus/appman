OS = ["windows", {"unix-like": [{"linux": ["ubuntu"]}, "darwin"]}]
OS_SUPPORTED = ["linux", "windows", "darwin"]
DEFS_EXT = ".yaml"

USER_PKG = "appman.user"
USER_DATA_PKG = f"{USER_PKG}.data"
REPO_PKG = "appman.repo"
REPO_FORMULAS_PKG = f"{REPO_PKG}.formulas"
REPO_PACKAGES_PKG = f"{REPO_PKG}.packages"
LOGS_PKG = "appman.logs"
CONFIG_RES_YAML = "config.yaml"

PACKAGES_TYPES = {
    "app": {"pkg": "apps"},
    "font": {"pkg": "fonts"},
    "driver": {"pkg": "drivers"},
    "provisioned": {"pkg": "provisioned"},
    "backend": {"pkg": "backend"},
    "extension": {"pkg": "extensions"},
}
