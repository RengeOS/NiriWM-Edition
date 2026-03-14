#!/bin/bash

chmod +x ~/.config/niri/scripts/*
chmod +x ~/.config/waybar/scripts/*
matugen image ~/Pictures/Wallpapers/default-wallpaper.jpg -m dark --source-color-index 0

if [ -z "$DISPLAY" ] && [ -n "$(tty)" ]; then
    exec niri
fi
