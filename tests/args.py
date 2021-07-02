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
}

packages = [
    {"id": "git", "os": "linux", "pt": "app"},
    {"id": "chocolatey-cli", "os": "windows", "pt": "app"},
    {"id": "microsoft-visual-studio-code", "os": "linux", "pt": "app"},
    {"id": "focusrite-control", "os": "windows", "pt": "driver"},
    {"id": "pylint", "os": "any", "pt": "backend-python"},
    {"id": "eslint", "os": "any", "pt": "backend-node"},
    {"id": "ms-azuretools.vscode-docker", "os": "any", "pt": "extension-vscode"},
]
