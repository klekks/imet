#!/bin/sh

echo "Start build.sh"

pkill *python*
pkill bot

pip3 install -r ./requirements.txt
python3 ./bot.py &

echo "End build.sh !!!!!"