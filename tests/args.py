cliargs = {
    "action": ["init", "install", "uninstall", "update-all"],
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
    "label": ["", "essentials", "dev", "utils"],
    "shell": ["", "cmd", "powershell"],
    "no-init": [True, False],
    "sudo": [True, False],
    "global": [True, False],
    "verbose": [True, False],
    "package-id": [
        "oh-my-zsh",
        "yq",
        "microsoft-visual-studio-code",
        "focusrite-control",
        "chocolatey-cli",
    ],
}

packages = [
    {"id": "oh-my-zsh", "name": "oh-my-zsh", "os": "linux", "pt": "cli"},
    {"id": "yq", "name": "yq", "os": "linux", "pt": "cli"},
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
    {
        "id": "chocolatey-cli",
        "name": "Chocolatey CLI",
        "os": "windows",
        "pt": "cli",
        "shell": "powershell",
    },
]
