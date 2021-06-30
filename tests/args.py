cliargs = {
    "action": ["install", "uninstall"],
    "os": ["windows", "linux"],
    "package-type": [
        "app",
        "font",
        "driver",
        "provisioned",
        "backend-python",
        "backend-node",
        "extension-vscode",
    ],
    "labels": ["", "dev-tools", "utils"],
    "package-id": [
        "git",
        "chocolatey-cli",
        "microsoft-visual-studio-code",
        "focusrite-control",
    ],
}

packages = [
    {"id": "git", "name": "git", "os": "linux", "pt": "app"},
    {
        "id": "chocolatey-cli",
        "name": "Chocolatey CLI",
        "os": "windows",
        "pt": "app",
    },
    {
        "id": "microsoft-visual-studio-code",
        "name": "microsoft-visual-studio-code",
        "os": "linux",
        "pt": "app",
    },
    {
        "id": "focusrite-control",
        "name": "Focusrite Control",
        "os": "windows",
        "pt": "driver",
    },
]

userlabels = ["essentials", "home"]
