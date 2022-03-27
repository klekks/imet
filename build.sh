#!/bin/sh

echo "Start build.sh"

pkill python3
pkill flask
pip3 install -r ./requirements.txt&
python3 ./bot.py&

export FLASK_APP=./backend.py
export FLASK_ENV=development
flask run&

echo "End build.sh !!!!!"