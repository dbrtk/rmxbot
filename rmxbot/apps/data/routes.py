""" views to the DataModel model
"""

from flask import Blueprint, jsonify, redirect, request

from ...config import TEMPLATES
from . import data
from .models import update_many


data_app = Blueprint(
    'data_app', __name__, root_path='/data', template_folder=TEMPLATES)


@data_app.route('/webpage/<objectid:docid>/')
def webpage(docid):
    """
    Returns the webpage for flask.
    :param docid:
    :return:
    """
    return jsonify(data.webpage(docid=docid))


@data_app.route('/edit-many/', methods=['POST'])
def edit_many():

    out = {}
    for k, v in request.form.items():
        _ = k.split('_')
        docid = _.pop(0)
        field = '_'.join(_)
        if docid not in out:
            out[docid] = {}
        out[docid][field] = v
    update_many(out)
    return redirect(request.referrer)
