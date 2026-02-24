#!/bin/bash

# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Le Nguyen Hoang Gia Phu <crystalforceix@gmail.com>

# Init
mkdir -p ./skel/.config/
mkdir -p ./skel/Pictures/Wallpapers/

# Variable
HOME_DIR="./skel"
HOME_CONFIG_DIR="./skel/.config"
HOME_WALLPAPERS_DIR="./skel/Pictures/Wallpapers"

# Setup
# List of files and directories to move
HOME_FILES=(
  "./Home-Overlay/.icons"  
)

CONFIG_FILES=(
  "./Home-Overlay/fish"
  "./Home-Overlay/fuzzel"
  "./Home-Overlay/gtk-3.0"
  "./Home-Overlay/gtk-4.0"
  "./Home-Overlay/helix"
  "./Home-Overlay/kitty"
  "./Home-Overlay/matugen"
  "./Home-Overlay/niri"
  "./Home-Overlay/swaync"
  "./Home-Overlay/waybar"
  "./Home-Overlay/wlogout"
  "./Home-Overlay/defaults/starship.toml"
)

# Loop for HOME_DIR
for h in "${HOME_FILES[@]}"; do
  # Check if file or directory exists
  if [[ -e "$h" ]]; then
    # Move the file/directory to destination
    mv -- "$h" "$HOME_DIR/"
    echo "Moved: $h"
  else
    echo "Error: '$h' does not exist" >&2
  fi
done

# Loop for HOME_CONFIG_DIR
for c in "${CONFIG_FILES[@]}"; do
  # Check if file or directory exists
  if [[ -e "$c" ]]; then
    # Move the file/directory to destination
    mv -- "$c" "$HOME_CONFIG_DIR/"
    echo "Moved: $c"
  else
    echo "Error: '$c' does not exist" >&2
  fi
done

# Setup wallpaper
mv ./Home-Overlay/defaults/default-wallpaper.jpg $HOME_WALLPAPERS_DIR

# Install icons theme into ~/.icons/
mkdir -p ./temp/ && cd ./temp/
git clone https://github.com/RengeOS/Deepin-Icons &&
cd Deepin-Icons/ &&
tar -xvf Deepin2022.tar.xz &&
mv * ../../skel/.icons &&
echo "Done! Deepin Icons 2022 has installed!" &&
cd ../../ && rm -rf ./temp/
