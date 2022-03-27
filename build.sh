#!/bin/sh

pkill *python*
pkill bot

pip install -r requirements.txt
python3 bot/bot.py