#!/bin/bash

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Le Nguyen Hoang Gia Phu <crystalforceix@gmail.com>

## Variable
Source_Packages_AUR="./Packages-AUR"
Name_Repo="rengeos-repo"

## Check if the directory exists.
if [[ -d "$Source_Packages_AUR" ]]; then
    echo "$Source_Packages_AUR Directory exists, continue..."
else
    echo "$Source_Packages_AUR Directory does not exist, exiting..."
    exit 0
fi

## Setup
echo "Making Packages Database In $Source_Packages_AUR"
repo-add $Source_Packages_AUR/"$Name_Repo".db.tar.gz $Source_Packages_AUR/*.pkg.tar.zst
echo "Done!"
