#!/bin/sh

echo "Start build.sh"

pip3 install -r ./requirements.txt > pip.log

chmod 755 bot.sh
./bot.sh &

echo "End build.sh !!!!!"