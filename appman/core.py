import os
import re
import subprocess

import yaml

from . import config


class AppMan:
    def __init__(self, path, config=config.CONFIG_PATH):
        self.path = path
        self.config = config
        self.packages = []
        self.formulas = []
        self.load_data(path)

    def load_data(self, path):
        # config
        cfdata, _ = self._load_data_file(self.config)
        self.config = Config(cfdata)

        # package managers
        for pmdata, pmpath in list(self._load_data_dir(config.PM_DIR)):
            pmname = self._get_name_from_path(pmpath)
            pm = Formula(pmname)
            pm.load(pmdata)
            self.formulas.append(pm)

        # formulas
        for fdata, fpath in self._load_data_dir(config.FORMULAS_DIR):
            fname = self._get_name_from_path(fpath)
            formula = Formula(fname, custom=True)
            formula.load(fdata)
            self.formulas.append(formula)

        # packages: cli
        for package in self._create_packages(path, "cli"):
            self.packages.append(package)

        # packages: gui
        for package in self._create_packages(path, "gui"):
            self.packages.append(package)

        # packages: group by files
        for presult in self._load_data_grouped(path):
            package = Package(presult["id"], presult["ptype"])
            package.load(presult["data"])
            self.packages.append(package)

    def get_packages(self, os, package_type, label=None):
        return [
            package
            for package in self.packages
            if (
                package.type == package_type
                and package.has_label(label)
                and package.is_compatible(os, self.config)
            )
        ]

    def get_package(self, package_type, id):
        for package in self.packages:
            if package.type == package_type and package.id == id:
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

    def _create_packages(self, path, ptype):
        ptdir = os.path.join(path, ptype)
        for pdata, ppath in self._load_data_dir(ptdir):
            pname = self._get_name_from_path(ppath)
            package = Package(pname, ptype)
            package.load(pdata)
            yield package

    def _load_data_file(self, path):
        with open(path, encoding="utf-8") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        return data, path

    def _load_data_dir(self, path):
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".yaml"):
                    fpath = os.path.join(root, file)
                    yield self._load_data_file(fpath)

    def _load_data_grouped(self, path):
        for entry in os.scandir(path):
            if entry.is_file() and entry.path.endswith(".yaml"):
                data, _ = self._load_data_file(entry.path)
                ptype = os.path.splitext(entry.name)[0]
                for d in data:
                    id = d if isinstance(d, str) else d["id"]
                    yield {
                        "id": id,
                        "data": d,
                        "ptype": ptype,
                    }

    def _get_name_from_path(self, path):
        return os.path.splitext(os.path.basename(path))[0]


class Package:
    arg_default = "pmid"

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
        sudo=False,
        allusers=False,
        test=False,
        verbose=False,
    ):
        args = self.get_args(formula.name)
        command = formula.get_command(commandtype, args, allusers)
        if command:
            return command.run(
                shell=formula.shell, sudo=sudo, test=test, verbose=verbose
            )
        raise ValueError(
            f"Command '{commandtype}' not found in formula '{formula.name}'"
        )

    def has_label(self, label):
        return not label or (self.labels and label in self.labels)

    def is_compatible(self, os, config):
        if self.format == "simple":
            return True

        for o in self.os:
            if config.is_os_compatible(o, os):
                return True

        return any(pm in config.get_compatible_pms(os, self.type) for pm in self.args)

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
    def __init__(self, name, custom=False):
        self.name = name
        self.custom = custom
        self.os = None
        self.shell = None
        self.commands = []
        self.initialized = False

    def load(self, data):
        self.os = data["os"]
        if "shell" in data:
            self.shell = data["shell"]
        for name in data["commands"]:
            command = data["commands"][name]
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

    def run(self, shell=None, sudo=False, test=False, verbose=False):
        command = self.command
        if shell == "powershell":
            command = ["powershell", "-Command", command]
        if sudo:
            command = f"sudo {command}"
        if test or verbose:
            self._print(command)
        if not test:
            return subprocess.run(command, shell=True, capture_output=True)

    def _print(self, command):
        if isinstance(command, list):
            command = " ".join(command)
        print(f"> {command}")


class Config:
    any_os = "any"

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
