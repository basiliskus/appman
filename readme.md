# appman

appman is cross-platform application management aggregator

[![Build Status](https://app.travis-ci.com/basiliskus/appman.svg?branch=main)](https://app.travis-ci.com/basiliskus/appman)

<p align="center"><img src="https://raw.githubusercontent.com/basiliskus/appman/main/docs/demo.gif"/></p>

## Requirements

- Python 3.8
- Git

## Installation

You can install appman from [PyPI](https://pypi.org/project/appman/):

```bash
> pip install appman
```

## Background

While working on my [dotfiles](https://wiki.archlinux.org/title/Dotfiles) repository, I realized that I also wanted to have a way to handle not just configuration files but also my installed applications. That way I'd be able to define which applications I want to have installed on any new environment, have those under version control, and run a script to install/uninstall applications on any new personal or work computer, server, etc.

## Goals

The main goal for appman is to be flexible and extensible. In that context the goals are:

- Cross-platform: handle multiple OS and devices. Currently appman handles Ubuntu and Windows (desktop).
- Multi-profile: define different profiles with a unique list of applications for different environments (e.g., work and personal computers).
- Supported Packages: aside from desktop and command line applications, support software like: device drivers, software plugins and extensions (e.g., vscode extensions), backend libraries (e.g., python libraries), fonts, etc.
- Package Management: support any package manager (e.g., apt, brew, scoop) or custom formulas to define how to install, uninstall and upgrade packages.
- Package definitions source: the source for package definitions is a [git repository](https://github.com/basiliskus/appman-main), which allows you to fork and use your own repository.

## How to use

### Set up your user package list

- Add a package to your user packages list

  Using interactive mode:

  ```console
  $ appman add

  [?] Select the package type: (Use arrow keys)
  >app
   font
   driver
   provisioned
   backend
   extension

  [?] Select app packages to add: (<up>, <down> to move, <space> to select, <a> to toggle, <i> to invert)
   ○ curl
   ○ fzf
  >● git
   ○ jq
   ○ python
   ○ ...

  Added git package
  ```

  or directly passing parameters:

  ```console
  $ appman add -pt app -id git
  ```

- Remove a previously added package

  Using interactive mode:

  ```console
  $ appman remove

  [?] Select the package type: (Use arrow keys)
  >app
   font
   driver
   provisioned
   backend
   extension

  [?] Select app packages to remove: (<up>, <down> to move, <space> to select, <a> to toggle, <i> to invert)
   ○ 7zip
   ○ curl
  >● git
   ○ ...

  Removed git package
  ```

  Directly passing parameters:

  ```console
  $ appman remove -pt app -id git
  ```

- Show your user packages list

  Using interactive mode:

  ```console
  $ appman list

  [?] Select the package type: (Use arrow keys)
  >app

   • 7zip (cli, utils)
   • curl (cli, utils)
  ```

  Directly passing parameters:

  ```console
  $ appman list -pt app
  ```

- Search all available packages to add

  Using interactive mode:

  ```console
  $ appman search

  [?] Select the package type: (Use arrow keys)
  >app

   • 7zip
   • ack
   • apache2
   • aria2
   • bottom
   • broot
   • cookiecutter
   • curl
  ...
  ```

  Directly passing parameters:

  ```console
  $ appman search -pt app -id 7zip
  ```

### Install/Uninstall packages in your user packages list

Using interactive mode:

```console
$ appman install

[?] Select the package type: (Use arrow keys)
>app

Installing 7zip...
Installing ack...
...
```

Directly passing parameters:

```console
$ appman install -pt app -id 7zip
```

### Change the package definitions repository source

```console
$ appman repo https://github.com/basiliskus/appman-main
```

### Update the package definitions repository source

```console
$ appman update
```

### Using labels

All packages have pre-defined labels (e.g. for apps: 'cli' & 'gui'), but you can also add your own labels by passing the --labels/-l parameter to the 'add' command.

```console
$ appman add -pt app -id 7zip -l server
```

You can also filter by labels when using the 'list', 'search', 'remove', 'install' or 'uninstall' commands

```console
$ appman list -pt app -l server
```

## License

© Basilio Bogado. Distributed under the [MIT License](LICENSE).
