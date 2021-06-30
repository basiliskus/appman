import re
import subprocess
from importlib import resources

import yaml

from . import config


class AppMan:
    pts = config.PACKAGES_TYPES

    def __init__(self):
        self.config = None
        self.formulas = []
        self.packages = []
        self.user_packages = []
        self.load_data()

    def load_data(self):

        # config
        cfdata = self._load_data_resource(config.BUCKET_PKG, config.CONFIG_RES_YAML)
        self.config = Config(cfdata)

        # formulas
        for ffile in self._get_data_resource_files(config.BUCKET_FORMULAS_PKG):
            data = self._load_data_resource(config.BUCKET_FORMULAS_PKG, ffile.name)
            custom = data["type"] == "custom"
            formula = Formula(ffile.stem, custom=custom)
            formula.load(
                self._load_data_resource(config.BUCKET_FORMULAS_PKG, ffile.name)
            )
            self.formulas.append(formula)

        # packages
        for pt in self.pts:
            pkg = f"{config.BUCKET_PACKAGES_PKG}.{self.pts[pt]['pkg']}"
            for pfile in self._get_data_resource_files(pkg):
                data = self._load_data_resource(pkg, pfile.name)
                package = Package(pfile.stem, pt)
                package.load(data)
                self.packages.append(package)

        # user packages
        for presult in self._get_grouped_data_resource_files(config.USER_DATA_PKG):
            package = UserPackage(presult["id"], presult["ptype"])
            package.load(presult["data"])
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

    def get_user_packages(self, package_type, id=None, labels=None):
        packages = []
        for package in self.user_packages:
            if (
                package.type == package_type
                and package.has_labels(labels)
                and (id is None or package.id == id)
            ):
                packages.append(package)
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
                and package.is_compatible(os, self.config)
                and (id is None or package.id == id)
            ):
                packages.append(package)
        return sorted(packages, key=lambda p: p.id)

    def get_package(self, package_type, id):
        packages = self.get_packages(package_type, id=id)
        return packages[0] if packages else None

    def get_formula(self, name):
        for formula in self.formulas:
            if formula.name == name:
                return formula

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

    def _create_packages(self, ptype):
        pname = f"{config.BUCKET_PACKAGES_PKG}.{ptype}"
        for pfile in self._get_data_resource_files(pname):
            package = Package(pfile.stem, ptype)
            package.load(self._load_data_resource(pname, pfile.name))
            yield package

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

    def _get_grouped_data_resource_files(self, package):
        path = resources.files(package)
        for file in path.glob(f"*{config.DEFS_EXT}"):
            ptype = self._get_package_type(file.stem)
            data = self._load_data_resource(package, file.name)
            if not data:
                continue
            for d in data:
                yield {
                    "id": d["id"],
                    "data": d,
                    "ptype": ptype,
                }

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
    arg_default = "pmid"

    def __init__(self, id, ptype, format="default"):
        super().__init__(id, ptype)
        self.name = id
        self.format = format
        self.description = ""
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
    pt_sep = "-"

    def __init__(self, data):
        self.os = data["os"]
        self.defaults = data["defaults"]

    def get_pm_defaults(self, ptype):
        pts = ptype.split(self.pt_sep)
        ptconfig = self.defaults["pm"]
        for pt in pts:
            ptconfig = ptconfig[pt]
        return ptconfig

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
