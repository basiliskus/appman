#!/usr/bin/env bash

SCRIPT="../appman/cli.py"
DATA="../data"

# linux
python $SCRIPT -f $DATA -t run install -os linux -pt cli
python $SCRIPT -f $DATA -t run install -os linux -pt cli --label essentials
python $SCRIPT -f $DATA -t run install -os linux -pt gui --label essentials
python $SCRIPT -f $DATA -t run install -os linux -pt backend
python $SCRIPT -f $DATA -t run install -os linux -pt drivers
python $SCRIPT -f $DATA -t run install -os linux -pt fonts
python $SCRIPT -f $DATA -t run install -os linux -pt vscode
python $SCRIPT -f $DATA -t run install -os linux -pt cli -pn 'oh-my-zsh'
python $SCRIPT -f $DATA -t run install -os linux -pt cli -pn 'yq'
python $SCRIPT -f $DATA -t run install -os linux -pt gui -pn 'Microsoft Visual Studio Code'

# windows
python $SCRIPT -f $DATA -t run uninstall -os windows -pt provisioned --shell powershell
python $SCRIPT -f $DATA -t run install -os windows -pt cli --label essentials
python $SCRIPT -f $DATA -t run install -os windows -pt gui --label essentials
python $SCRIPT -f $DATA -t run install -os windows -pt backend
python $SCRIPT -f $DATA -t run install -os windows -pt fonts
python $SCRIPT -f $DATA -t run install -os windows -pt vscode
python $SCRIPT -f $DATA -t run install -os windows -pt drivers -pn 'Focusrite Control'
python $SCRIPT -f $DATA -t run install -os windows -pt cli -pn 'Chocolatey CLI' --shell powershell
