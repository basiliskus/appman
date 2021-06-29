# appman

appman is cross-platform application management aggregator

[![Build Status](https://travis-ci.com/basiliskus/appman.svg?branch=main)](https://travis-ci.com/basiliskus/appman)

<p align="center"><img src="/docs/demo.gif?raw=true"/></p>

## Requirements

- Python 3.9

## Installation

You can install appman from [PyPI](https://pypi.org/project/appman/):

```bash
> pip install appman
```

## How to use

### Set up you user package list

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
    $ appman add

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

    7zip
    ack
    apache2
    aria2
    bottom
    broot
    cookiecutter
    curl
    ...
    ```

    Directly passing parameters:
    ```console
    $ appman search -pt app
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
