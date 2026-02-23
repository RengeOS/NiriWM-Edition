#!/bin/bash
cd /tmp/ &&
git clone https://github.com/RengeOS/Deepin-Icons &&
cd Deepin-Icons/ &&
tar -xvf Deepin2022.tar.xz &&
mv * ~/.icons &&
echo "Done! Deepin Icons 2022 has installed!" &&
cd /tmp/ && rm -rf Deepin-Icons/
