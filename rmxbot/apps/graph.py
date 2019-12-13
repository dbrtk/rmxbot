
import json

from flask import abort, Blueprint, jsonify, request

graph_app = Blueprint('graph_app', __name__, root_path='/graph')


@graph_app.route('/', methods=['POST'])
def graph_post():
    """ POST method for graphql calls.

    :return:
    """

    query = json.loads(request.data)
    print(query)

    return jsonify({'data': {'msg': 'whatever'}})


@graph_app.route('/', methods=['GET'])
def graph_get():
    """ GET method for graphql calls.

    When receiving a request with a GET method, graphql expects a query string.


    :return:
    """

    query = request.args.get('query')
    print(query)

    return jsonify({'data': {'data': '{"ohrly": "whatever"}'}})


