import sys
import os
import io

# for now using importlib_resources instead of importlib
# for compatibility with python 3.8
import importlib_resources as resources

# from importlib import resources

import yaml

from . import config


def parse_stmsg(msg):
    msg = msg.decode("UTF-8") if isinstance(msg, bytes) else msg
    msg = f"{os.linesep}".join(msg.splitlines()) if isinstance(msg, list) else msg
    if isinstance(msg, io.IOBase):
        msg = msg.read()
    return msg.rstrip()


def get_verb(action, tense):
    if "update" in action:
        action = "updat"
    elif action not in ["install", "uninstall"]:
        action = "process"

    if tense == "present":
        return f"{action}ing"
    if tense == "past":
        return f"{action}ed"

    return action


def log_subprocess_output(process, logger):
    while process.poll() is None:
        line = process.stdout.readline()
        if line:
            logger.info(line.strip())
        sys.stdout.flush()


def is_os_compatible(source, dest):
    return (
        (source == dest)
        or (source in "any" or dest in "any")
        or (dest in get_os_family_names(os=source))
    )


def get_os_family_names(data=config.OS, os=None, found=False):
    for e in data:
        if isinstance(e, dict):
            yield from get_os_family_names(e, os, found)
        else:
            include = found or not os or os == e
            if include:
                yield e
            if isinstance(data, dict):
                yield from get_os_family_names(data[e], os, include)


def load_yaml_resource(package, resource):
    fpath = get_package_resource_file(package, resource)
    if not fpath.exists():
        return None
    with resources.open_text(package, resource) as file:
        data = yaml.load(file, Loader=yaml.FullLoader)
    return data


def write_yaml_resource(package, resource, data):
    fpath = get_package_resource_file(package, resource)
    with open(fpath, "w", encoding="utf-8") as file:
        yaml.dump(data, file, sort_keys=False, default_flow_style=None)


def get_package_path(package):
    return resources.files(package)


def get_package_resource_files(package):
    path = get_package_path(package)
    yield from path.glob(f"*{config.DEFS_EXT}")


def get_package_resource_file(package, resource):
    path = get_package_path(package)
    fname = resource if config.DEFS_EXT in resource else f"{resource}{config.DEFS_EXT}"
    return path.joinpath(fname)


def add_data_resource(package, resource, data):
    content = load_yaml_resource(package, resource)
    if not content:
        content = []
    elif not isinstance(content, list):
        raise TypeError

    content.append(data)
    content = sorted(content, key=lambda o: o["id"])
    write_yaml_resource(package, resource, content)


def remove_data_resource(package, resource, data):
    content = load_yaml_resource(package, resource)
    content.remove(data)
    write_yaml_resource(package, resource, content)


def get_resource_name(ptype):
    names = ptype.split("-")
    for pt in config.PACKAGES_TYPES:
        if pt == names[0]:
            pkg = config.PACKAGES_TYPES[pt]["pkg"]
            return ".".join([pkg] + names[1:])
    raise ValueError(f"{ptype} did not match resource names")


def get_package_type(resource):
    names = resource.split(".")
    for pt in config.PACKAGES_TYPES:
        if config.PACKAGES_TYPES[pt]["pkg"] == names[0]:
            return "-".join([pt] + names[1:])
    raise ValueError(f"{resource} did not match package types")


def get_resource_names():
    return [get_resource_name(pt) for pt in get_package_types()]


def get_package_types():
    package_types = []
    for pt, v in config.PACKAGES_TYPES.items():
        if "sub" in v:
            for sub in v["sub"]:
                package_types.append(f"{pt}-{sub}")
        else:
            package_types.append(pt)
    return package_types


def get_pt_choices():
    choices = {}
    for pt in get_package_types():
        pname, *psub = pt.split("-")
        if pname not in choices:
            choices[pname] = []
        if psub:
            choices[pname].append(psub[0])
    return choices


def get_repo_path():
    return get_package_path(config.APPMAN_PKG) / config.REPO_DIR
