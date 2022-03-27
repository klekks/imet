from flask import Flask
from flask import request, Response

from models.models import Button

import json

app = Flask(__name__)


@app.route("/all_buttons")
def all_buttons():
    buttons = Button.select(Button)[:]
    print(buttons)
    result = []
    for button in buttons:
        result.append(button.to_dict())

    return Response(
            json.dumps(result, sort_keys=True, indent=4),
            mimetype='application/json'
    )


@app.route("/add_button")
def add_button():
    args = dict(request.args)
    if not args.get('page', False):
        return Response("FAIL", 404)
    if not args.get('name', False):
        return Response("FAIL", 404)
    if not args.get('next_page', False) and not args.get('action', False):
        return Response("FAIL", 404)
    if not args.get('next_page', False):
        args['next_page'] = '0'
    button = Button.create_button(args['page'], args['name'], args['next_page'])
    if args.get('action', False):
        button.action = args['action']
        button.save()
    return "OK"


@app.route("/", methods=["POST",])
def default_post_handler():
    return str(request.get_json())


@app.route("/", methods=["GET",])
def default_get_handler():
    return str(dict(request.args))
