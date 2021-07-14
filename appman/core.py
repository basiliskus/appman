import re
import copy
import shutil
import subprocess

from . import log
from . import util
from . import config


logger = log.AppmanLogger(__file__, "DEBUG", "DEBUG")


class AppMan:
    def __init__(self):
        self.config = Config(config.USER_PKG, config.CONFIG_RES_YAML)
        self.repo = Repo(self.config.repo)
        self.userrepo = UserPackageRepo()

    def update(self):
        self.repo.update()

    def get_packages(self, package_type, os="any", id=None, labels=None):
        return self.repo.get_packages(package_type, os, id, labels)

    def get_package(self, package_type, id):
        return self.repo.get_package(package_type, id)

    def get_user_packages(self, package_type, os="any", id=None, labels=None):
        user_packages = self.userrepo.get_packages(package_type, id, labels)
        return [p for p in user_packages if self.repo.get_package(p.type, p.id, os)]

    def get_user_package(self, package_type, id):
        return self.userrepo.get_package(package_type, id)

    def has_user_package(self, package_type, id):
        return self.userrepo.has_package(package_type, id)

    def add_user_package(self, package, labels=None):
        self.userrepo.add_package(package, labels)

    def remove_user_package(self, user_package):
        self.userrepo.remove_package(user_package)

    def set_repo(self, url):
        self.config.repo = url
        self.config.save()
        self.repo.switch(url)


class Repo:
    repo_path = util.get_repo_path()

    def __init__(self, url):
        self.init(url)
        self.load()

    def init(self, url):
        self.url = url
        self.packages = []
        if not self.repo_path.is_dir():
            self.clone()

    def load(self):
        formulas = []
        fpackage = config.REPO_FORMULAS_PKG
        for ffile in util.get_package_resource_files(fpackage):
            data = util.load_yaml_resource(fpackage, ffile.name)
            formula = Formula(ffile.stem)
            formula.load(util.load_yaml_resource(fpackage, ffile.name))
            formulas.append(formula)

        for rname in util.get_resource_names():
            pkg = f"{config.REPO_PACKAGES_PKG}.{rname}"
            pt = util.get_package_type(rname)
            for pfile in util.get_package_resource_files(pkg):
                data = util.load_yaml_resource(pkg, pfile.name)
                package = Package(data["id"], pt)
                package.load(data, formulas)
                self.packages.append(package)

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

    def get_package(self, package_type, id, os="any"):
        packages = self.get_packages(package_type, id=id, os=os)
        return packages[0] if packages else None

    def switch(self, url):
        shutil.rmtree(self.repo_path)
        self.init(url)
        self.load()

    def clone(self):
        logger.info(f"Initializing source repo: {self.url}")
        subprocess.run(["git", "clone", self.url, self.repo_path], check=True)

    def update(self):
        logger.info(f"Updating source repo: {self.url}")
        subprocess.run(["git", "-C", self.repo_path, "pull"], check=True)


class UserPackageRepo:
    def __init__(self):
        self.packages = []
        self.load(config.USER_DATA_PKG)

    def load(self, upackage):
        for path in util.get_package_resource_files(upackage):
            ptype = util.get_package_type(path.stem)
            data = util.load_yaml_resource(upackage, path.name)
            for pd in data:
                package = UserPackage(pd["id"], ptype)
                package.load(pd)
                self.packages.append(package)

    def add_package(self, package, labels=None):
        # add default labels for package
        plabels = package.labels
        if labels:
            plabels.extend(labels)

        user_package = UserPackage(package.id, package.type, plabels)
        # self.packages.append(user_package)

        resource = util.get_resource_name(package.type)
        util.add_data_resource(
            config.USER_DATA_PKG, f"{resource}{config.DEFS_EXT}", user_package.data
        )

    def remove_package(self, user_package):
        # self.packages.remove(user_package)
        resource = util.get_resource_name(user_package.type)
        util.remove_data_resource(
            config.USER_DATA_PKG, f"{resource}{config.DEFS_EXT}", user_package.data
        )

    def get_packages(self, package_type, id=None, labels=None):
        packages = []
        for user_package in self.packages:
            if (
                user_package.type == package_type
                and user_package.has_labels(labels)
                and (id is None or user_package.id == id)
            ):
                packages.append(user_package)
        return sorted(packages, key=lambda p: p.id)

    def get_package(self, package_type, id):
        packages = self.get_packages(package_type, id=id)
        return packages[0] if packages else None

    def has_package(self, package_type, id):
        return bool(self.get_package(package_type, id))


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
        return command.run(
            shell=formula.shell, sudo=sudo, test=test, verbose=verbose, quiet=quiet
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
        command = formula.get_command("installed")
        return command.check_output()

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

    def init(self, test=False, verbose=False, quiet=False):
        if self.initialized or not self.has_command("init"):
            return
        command = self.get_command("init")
        command.run(test=test, verbose=verbose, quiet=quiet)
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
        raise ValueError(f"Command '{name}' not found in formula '{self.name}'")

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

        try:
            outs, errs = process.communicate(timeout=180)
            if process.returncode != 0 and errs:
                logger.error(util.parse_stmsg(errs))
        except subprocess.TimeoutExpired as e:
            logger.error(e)
            process.kill()
            process.communicate()

        return process

    def check_output(self):
        process = subprocess.run(self.command, capture_output=True, shell=True)
        return process.returncode == 0 and process.stdout

    def _print(self, command):
        if isinstance(command, list):
            command = " ".join(command)
        logger.console(f"> {command}")


class Config:
    pt_sep = "-"

    def __init__(self, package, resource):
        self.pkg = package
        self.resource = resource
        self.repo = None
        self.pms = []
        self.tags = []
        self.load()

    def load(self):
        data = util.load_yaml_resource(self.pkg, self.resource)
        if "repository" in data:
            self.repo = data["repository"]
        if "package-managers" in data:
            self.pms = data["package-managers"]
        if "tags" in data:
            self.tags = data["tags"]

    def save(self):
        data = {}
        if self.repo:
            data["repository"] = self.repo
        if self.pms:
            data["package-managers"] = self.pms
        if self.tags:
            data["tags"] = self.tags
        util.write_yaml_resource(self.pkg, self.resource, data)

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
