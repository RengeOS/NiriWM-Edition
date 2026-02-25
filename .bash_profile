#!/bin/bash

chmod +x ~/.config/niri/scripts/*
chmod +x ~/.config/waybar/scripts/*
matugen image ~/Pictures/Wallpapers/default-wallpaper.jpg

if [ -z "$DISPLAY" ] && [ -n "$(tty)" ]; then
    exec niri
fi
