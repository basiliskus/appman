cliargs = {
    "action": ["install", "uninstall"],
    "os": ["windows", "linux"],
    "package-type": [
        "cli",
        "gui",
        "backend",
        "fonts",
        "drivers",
        "vscode",
        "provisioned",
    ],
    "label": ["", "essentials", "dev-tools", "utils"],
    "package-id": [
        "git",
        "chocolatey-cli",
        "microsoft-visual-studio-code",
        "focusrite-control",
    ],
}

packages = [
    {"id": "git", "name": "git", "os": "linux", "pt": "cli"},
    {
        "id": "chocolatey-cli",
        "name": "Chocolatey CLI",
        "os": "windows",
        "pt": "cli",
    },
    {
        "id": "microsoft-visual-studio-code",
        "name": "microsoft-visual-studio-code",
        "os": "linux",
        "pt": "gui",
    },
    {
        "id": "focusrite-control",
        "name": "Focusrite Control",
        "os": "windows",
        "pt": "drivers",
    },
]
