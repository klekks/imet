#!/bin/sh

echo "Start build.sh"

sudo pkill python3 > pkill.log

pip3 install -r ./requirements.txt > pip.log

python3 bot.py& > python.log


echo "End build.sh !!!!!"