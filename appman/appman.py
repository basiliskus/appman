import os
import re
import yaml
import subprocess


class AppMan:
    def __init__(self, path):
        self.path = path
        self.config = None
        self.packages = []
        self.formulas = []
        self.load(path)

    def load(self, path):
        self._load_data_recursively(path)

    def get_packages(self, os, package_type, label=None):
        for package in self.packages:
            if (
                package.type == package_type
                and package.has_label(label)
                and package.is_compatible(os, self.config)
            ):
                yield package

    def get_package(self, package_type, name):
        for package in self.packages:
            if package.type == package_type and package.name == name:
                return package
        return None

    def get_formula(self, name):
        for formula in self.formulas:
            if formula.name == name:
                return formula
        return None

    def find_formulas(self, custom=None, command_name=None):
        for formula in self.formulas:
            if (
                (custom is None or formula.custom == custom)
                # and formula.is_compatible(os, self.config, package_type)
                and (not command_name or formula.has_command(command_name))
            ):
                yield formula

    def find_best_formula(self, os, package):
        # if package has simple format
        # there is only one way to get the formula
        if package.format == "simple":
            pm = self.config.get_compatible_pms(os, package.type)[0]
            return self.get_formula(pm)

        fnames = list(package.args.keys())

        # priority 1: custom formula
        for formula in self.find_formulas(custom=True):
            if formula.name in fnames and self.config.is_os_compatible(os, formula.os):
                return formula

        # priority 2: compatible package management formulas
        # using order in config.defaults
        for pm in self.config.get_compatible_pms(os, package.type):
            if pm in fnames:
                return self.get_formula(pm)

        return None

    def _load_data_recursively(self, path, groups=[], level=0):
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file() and entry.name.endswith(".yaml"):
                    name = os.path.splitext(entry.name)[0]
                    with open(entry.path, encoding="utf-8") as f:
                        data = yaml.load(f, Loader=yaml.FullLoader)
                        self._load_type(name, data, groups)
                elif entry.is_dir():
                    self._load_data_recursively(
                        os.path.join(path, entry.name),
                        groups + [entry.name],
                        level + 1,
                    )

    def _load_type(self, name, data, groups):
        if not groups and name == "config":
            self.config = Config(data)
        elif groups[0] == "packages":
            if len(groups) > 1:
                package = Package(name, groups[1])
                package.load(data)
                self.packages.append(package)
            else:
                for d in data:
                    if isinstance(d, str):
                        pname = d
                        format = "simple"
                    else:
                        pname = d["name"]
                        format = "default"
                    package = Package(pname, name, format)
                    package.load(d)
                    self.packages.append(package)
        elif groups[0] == "formulas":
            formula = Formula(name, groups[1], custom=True)
            formula.load(data)
            self.formulas.append(formula)
        elif groups[0] == "package-managers":
            pm = Formula(name)
            pm.load(data)
            self.formulas.append(pm)


class Package:
    arg_default = "pid"

    def __init__(self, id, type, format="default"):
        self.id = id
        self.name = id
        self.type = type
        self.format = format
        self.description = ""
        self.labels = []
        self.args = {}
        self.os = []

    def load(self, obj):
        if isinstance(obj, str):
            self.format = "simple"
            return

        if "name" in obj:
            self.name = obj["name"]
        if "description" in obj:
            self.description = obj["description"]
        if "labels" in obj:
            self.labels = obj["labels"]
        if "formulas" in obj:
            self._load_formula_args(obj["formulas"])
        if self.arg_default in obj:
            self._load_pm_args(obj[self.arg_default])

    def run(
        self,
        formula,
        commandtype,
        shell=None,
        sudo=False,
        allusers=False,
        test=False,
    ):
        args = self.get_args(formula.name)
        command = formula.get_command(commandtype, args, allusers)
        command.run(shell, sudo, test)

    def has_label(self, label):
        return not label or (self.labels and label in self.labels)

    def is_compatible(self, os, config):
        if self.format == "simple":
            return True

        for o in self.os:
            if config.is_os_compatible(o, os):
                return True

        for pm in self.args:
            if pm in config.get_compatible_pms(os, self.type):
                return True
        return False

    def get_args(self, name=None):
        if self.format == "simple":
            return {self.arg_default: self.name}
        if name and self.args:
            return self.args[name]
        return self.args

    def _load_formula_args(self, data):
        for f in data:
            self.args[f["name"]] = f["args"] if "args" in f else None
            self.os.append(f["os"])

    def _load_pm_args(self, data):
        for f in data:
            self.args[f] = {self.arg_default: data[f]}


class Formula:
    def __init__(self, name, os=None, custom=False):
        self.name = name
        self.os = os
        self.custom = custom
        self.commands = []
        self.initialized = False

    def load(self, data):
        for c in data:
            name = c
            command = data[c]
            self.add_command(name, command)

    def init(self, test=False):
        if self.initialized or not self.has_command("init"):
            return
        command = self.get_command("init")
        command.run(test=test)
        self.initialized = True

    def add_command(self, name, command):
        self.commands.append(Command(name, command))

    def has_command(self, name, allusers=False):
        name = f"{name}-global" if allusers else name
        return any(c for c in self.commands if c.name == name)

    def get_command(self, name, args=None, allusers=False):
        name = f"{name}-global" if allusers else name
        for command in self.commands:
            if command.name == name:
                if args:
                    return Command(
                        command.name, self._resolve_args(command.command, args)
                    )
                else:
                    return command
        return None

    def _resolve_args(self, command, values):
        args = self._infer_args(command)
        for arg in args:
            if arg in values.keys():
                command = command.replace(f"${arg}", values[arg])
        return command

    def _infer_args(self, command):
        regex = r"\$([a-z0-9_-]+)"
        return re.findall(regex, command, re.U | re.M)


class Command:
    def __init__(self, name, command):
        self.name = name
        self.command = command

    def run(self, shell=None, sudo=False, test=False):
        command = self.command
        if shell == "powershell":
            command = ["powershell", "-Command", command]
        if sudo:
            command = f"sudo {command}"
        self._print(command)
        if not test:
            subprocess.run(command, shell=True)

    def _print(self, command):
        if isinstance(command, list):
            command = " ".join(command)
        print(f"> {command}")


class Config:
    any_os = ["any", "all"]

    def __init__(self, data):
        self.os = data["os"]
        self.defaults = data["defaults"]

    def get_pm_defaults(self, ptype):
        return self.defaults["pm"][ptype]

    def get_compatible_pms(self, os, ptype):
        return list(set(self._get_compatible_pms(os, ptype)))

    def get_os_family_names(self, os):
        return self._get_os_family_names(self.os, os)

    def is_os_compatible(self, source, dest):
        return (
            (source == dest)
            or (source in self.any_os or dest in self.any_os)
            or (dest in self.get_os_family_names(source))
        )

    def _get_os_family_names(self, data, os=None, found=False):
        for e in data:
            if isinstance(e, dict):
                yield from self._get_os_family_names(e, os, found)
            else:
                include = found or not os or os == e
                if include:
                    yield e
                if isinstance(data, dict):
                    yield from self._get_os_family_names(data[e], os, include)

    def _get_compatible_pms(self, os, ptype):
        pmc = self.get_pm_defaults(ptype)
        for pmos in pmc:
            if self.is_os_compatible(os, pmos):
                yield from pmc[pmos]