#!/bin/sh

echo "Start build.sh"

pip3 install -r ./requirements.txt > pip.log

pkill -9 -f ./bot.py

echo "End build.sh !!!!!"