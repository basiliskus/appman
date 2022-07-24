OS = ["windows", {"unix-like": [{"linux": ["ubuntu", "arch", "fedora"]}, "darwin"]}]
OS_SUPPORTED = ["linux", "windows", "darwin"]
DEFS_EXT = ".yaml"

REPO_DIR = "repo"
APPMAN_PKG = "appman"
USER_PKG = f"{APPMAN_PKG}.user"
USER_DATA_PKG = f"{USER_PKG}.data"
REPO_PKG = f"{APPMAN_PKG}.{REPO_DIR}"
REPO_FORMULAS_PKG = f"{REPO_PKG}.formulas"
REPO_PACKAGES_PKG = f"{REPO_PKG}.packages"
LOGS_PKG = f"{APPMAN_PKG}.logs"
CONFIG_RES_YAML = "config.yaml"

PACKAGES_TYPES = {
    "app": {"pkg": "apps"},
    "font": {"pkg": "fonts"},
    "driver": {"pkg": "drivers"},
    "provisioned": {"pkg": "provisioned"},
    "backend": {"pkg": "backend", "sub": ["python", "node"]},
    "extension": {"pkg": "extensions", "sub": ["vscode"]},
}
