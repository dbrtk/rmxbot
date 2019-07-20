
import json

from flask import abort, Blueprint, jsonify, request

graph_app = Blueprint('graph_app', __name__, root_path='/graph')


@graph_app.route('/', methods=['POST'])
def graph_post():

    query = json.loads(request.data)
    print(query)

    return jsonify({'data': {'msg': 'whatever'}})


@graph_app.route('/', methods=['GET'])
def graph_get():


    query = request.args.get('query')
    print(query)

    return jsonify({'data': {'data': '{"ohrly": "whatever"}'}})


