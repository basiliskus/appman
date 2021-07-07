import re
import copy
import subprocess

# from importlib import resources
# for now using importlib_resources instead of importlib
# for compatibility with python 3.8
import importlib_resources as resources

import yaml

from . import log
from . import util
from . import config


logger = log.AppmanLogger(__file__, "DEBUG", "DEBUG")


class AppMan:
    pts = config.PACKAGES_TYPES

    def __init__(self, bpackage):
        self.config = None
        self.packages = []
        self.user_packages = []
        self.load_bucket_data(bpackage)

    def load_bucket_data(self, bpackage):

        # config
        cfdata = self._load_data_resource(bpackage, config.CONFIG_RES_YAML)
        self.config = Config(cfdata)

        # formulas
        formulas = []
        fpackage = f"{bpackage}.{config.BUCKET_FORMULAS_PKG}"
        for ffile in self._get_data_resource_files(fpackage):
            data = self._load_data_resource(fpackage, ffile.name)
            formula = Formula(ffile.stem)
            formula.load(self._load_data_resource(fpackage, ffile.name))
            formulas.append(formula)

        # packages
        fpackage = f"{bpackage}.{config.BUCKET_PACKAGES_PKG}"
        for pt in self.pts:
            pkg = f"{fpackage}.{self.pts[pt]['pkg']}"
            for pfile in self._get_data_resource_files(pkg):
                data = self._load_data_resource(pkg, pfile.name)
                package = Package(data["id"], pt)
                package.load(data, formulas)
                self.packages.append(package)

    def load_user_data(self, upackage):
        path = resources.files(upackage)
        for path in path.glob(f"*{config.DEFS_EXT}"):
            ptype = self._get_package_type(path.stem)
            data = self._load_data_resource(upackage, path.name)
            for pd in data:
                package = UserPackage(pd["id"], ptype)
                package.load(pd)
                self.user_packages.append(package)

    def add_user_package(self, package, labels=None):
        # add default labels for package
        plabels = package.labels
        if labels:
            plabels.extend(labels)

        user_package = UserPackage(package.id, package.type, plabels)
        resource = self._get_resource_name(package.type)
        self._add_data_resource(config.USER_DATA_PKG, resource, user_package.data)

    def remove_user_package(self, user_package):
        resource = self._get_resource_name(user_package.type)
        self._remove_data_resource(config.USER_DATA_PKG, resource, user_package.data)

    def get_user_packages(self, package_type, os="any", id=None, labels=None):
        packages = []
        for user_package in self.user_packages:
            package = self.get_package(package_type, user_package.id)
            if (
                user_package.type == package_type
                and user_package.has_labels(labels)
                and (package is None or package.is_compatible(os))
                and (id is None or user_package.id == id)
            ):
                packages.append(user_package)
        return sorted(packages, key=lambda p: p.id)

    def get_user_package(self, package_type, id):
        packages = self.get_user_packages(package_type, id=id)
        return packages[0] if packages else None

    def has_user_package(self, package_type, id):
        return bool(self.get_user_package(package_type, id))

    def has_any_user_package(self, package_type, labels):
        return bool(self.get_user_packages(package_type, labels=labels))

    def get_packages(self, package_type, os="any", id=None, labels=None):
        packages = []
        for package in self.packages:
            if (
                package.type == package_type
                and package.has_labels(labels)
                and package.is_compatible(os)
                and (id is None or package.id == id)
            ):
                packages.append(package)
        return sorted(packages, key=lambda p: p.id)

    def get_package(self, package_type, id):
        packages = self.get_packages(package_type, id=id)
        return packages[0] if packages else None

    def _load_data_resource(self, package, resource):
        with resources.open_text(package, resource) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        return data

    def _add_data_resource(self, package, resource, data):
        content = self._read_data_resource(package, resource)
        if not content:
            content = []
        elif not isinstance(content, list):
            raise TypeError

        content.append(data)
        content = sorted(content, key=lambda o: o["id"])
        self._write_data_resource(package, resource, content)

    def _remove_data_resource(self, package, resource, data):
        content = self._read_data_resource(package, resource)
        content.remove(data)
        self._write_data_resource(package, resource, content)

    def _read_data_resource(self, package, resource):
        fpath = self._get_resource_file(package, resource)
        if not fpath.exists():
            return None
        with open(fpath, encoding="utf-8") as file:
            return yaml.load(file, Loader=yaml.FullLoader)

    def _write_data_resource(self, package, resource, data):
        fpath = self._get_resource_file(package, resource)
        with open(fpath, "w", encoding="utf-8") as file:
            yaml.dump(data, file)

    def _get_data_resource_files(self, package):
        path = resources.files(package)
        yield from path.glob(f"*{config.DEFS_EXT}")

    def _get_resource_file(self, package, resource):
        path = resources.files(package)
        return path.joinpath(f"{resource}{config.DEFS_EXT}")

    def _get_resource_name(self, ptype):
        return next(self.pts[pt]["pkg"] for pt in self.pts if pt == ptype)

    def _get_package_type(self, resource):
        return next(pt for pt in self.pts if self.pts[pt]["pkg"] == resource)


class CommonPackage:
    def __init__(self, id, ptype):
        self.id = id
        self.type = ptype
        self.labels = []

    def has_labels(self, labels):
        return not labels or (self.labels and set(labels).issubset(self.labels))


class UserPackage(CommonPackage):
    def __init__(self, id, ptype, labels=None):
        super().__init__(id, ptype)
        if labels:
            self.labels.extend(labels)

    def load(self, obj):
        if "labels" in obj:
            self.labels = obj["labels"]

    @property
    def data(self):
        return {"id": self.id, "labels": self.labels}


class Package(CommonPackage):
    def __init__(self, id, ptype):
        super().__init__(id, ptype)
        self.name = id
        self.description = ""
        self.formulas = []

    def load(self, obj, formulas):
        if "name" in obj:
            self.name = obj["name"]
        if "description" in obj:
            self.description = obj["description"]
        if "labels" in obj:
            self.labels = obj["labels"]
        if "custom-formulas" in obj:
            for fo in obj["custom-formulas"]:
                formula = self._create_custom_formula(fo)
                self.formulas.append(formula)
        if "formulas" in obj:
            for fo in obj["formulas"]:
                formula = next((f for f in formulas if f.name == fo), None)
                if not formula:
                    logger.error(f"Formula not found for '{fo}'")
                    continue
                formula = self._create_formula(formula, obj["formulas"][fo])
                self.formulas.append(formula)

    def run(
        self,
        formula,
        commandtype,
        sudo=False,
        allusers=False,
        test=False,
        verbose=False,
        quiet=False,
    ):
        command = formula.get_command(commandtype, allusers)
        if command:
            return command.run(
                shell=formula.shell, sudo=sudo, test=test, verbose=verbose, quiet=quiet
            )
        raise ValueError(
            f"Command '{commandtype}' not found in formula '{formula.name}'"
        )

    def find_best_formula(self, os, config):
        # priority 1: custom formula
        for formula in self.formulas:
            if formula.custom and util.is_os_compatible(formula.os, os):
                return formula

        # priority 2: compatible package management formulas
        # using order in config.pms
        for pm in config.get_compatible_pms(os, self.type):
            formula = self.get_formula(pm)
            if formula:
                return formula

    def get_formula(self, name):
        for formula in self.formulas:
            if formula.name == name:
                return formula

    def is_compatible(self, os):
        for f in self.formulas:
            if util.is_os_compatible(f.os, os):
                return True

    def is_installed(self, formula):
        result = self.run(formula, "installed", quiet=True)
        return result.returncode == 0 and result.stdout.readline()

    def _create_custom_formula(self, data):
        formula = Formula("custom", custom=True)
        formula.load(data)
        return formula

    def _create_formula(self, formula, argvalues):
        newformula = copy.deepcopy(formula)
        for command in newformula.commands:
            command.command = formula.resolve_args(command.command, argvalues)
        return newformula


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

    def get_command(self, name, allusers=False):
        name = f"{name}-global" if allusers else name
        for command in self.commands:
            if command.name == name:
                return command
        return None

    @staticmethod
    def resolve_args(command, argvalues):
        # infer args
        regex = r"\$([a-z0-9_-]+)"
        args = re.findall(regex, command, re.U | re.M)

        if isinstance(argvalues, str):
            if len(args) == 1:
                return command.replace(f"${args[0]}", argvalues)
            elif len(args) > 1:
                logger.error(f"Need to specify key for '{argvalues}'")
                return

        for arg in args:
            if arg in argvalues.keys():
                command = command.replace(f"${arg}", argvalues[arg])
        return command


class Command:
    def __init__(self, name, command):
        self.name = name
        self.command = command

    def run(self, shell=None, sudo=False, test=False, verbose=False, quiet=False):
        command = self.command
        if shell == "powershell":
            command = ["powershell", "-Command", command]
        if sudo:
            command = f"sudo {command}"
        if test or verbose:
            self._print(command)
        if test:
            return

        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=(subprocess.PIPE if quiet else subprocess.STDOUT),
            text=True,
        )

        if not quiet:
            util.log_subprocess_output(process, logger)

        process.wait()

        return process

    def _print(self, command):
        if isinstance(command, list):
            command = " ".join(command)
        logger.console(f"> {command}")


class Config:
    pt_sep = "-"

    def __init__(self, data):
        self.pms = data["package-managers"]
        self.tags = data["tags"]

    def get_pm_defaults(self, ptype):
        pts = ptype.split(self.pt_sep)
        ptconfig = self.pms
        for pt in pts:
            ptconfig = ptconfig[pt]
        return ptconfig

    def get_compatible_pms(self, os, ptype):
        return list(set(self._get_compatible_pms(os, ptype)))

    def _get_compatible_pms(self, os, ptype):
        pmc = self.get_pm_defaults(ptype)
        for pmos in pmc:
            if util.is_os_compatible(os, pmos):
                yield from pmc[pmos]
