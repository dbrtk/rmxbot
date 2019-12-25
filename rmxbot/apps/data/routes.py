""" views to the DataModel model
"""

from flask import (Blueprint, get_flashed_messages, jsonify, redirect,
                   render_template, request)

from ...config import TEMPLATES
from . import data
from .models import DataModel, update_many


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


@data_app.route('/data-to-corpus/')
def data_to_corpus():
    """
    This method is used internally when scraped webpages are sent from scrasync
    to rnmxbot.
    """
    # todo(): delete this!!!!!!!!!!!!!!!!!!
    # todo(): review this method. Delete this.
    # obj = QueryDict(request.body).dict()
    # docid = obj.get('docid')
    # path = obj.get('path')

    docid = request.args.get('docid')
    path = request.args.get('path')

    doc = DataModel.inst_by_id(docid)
    doc.data_to_corpus(path, id_as_head=True)
    _id = doc.purge_data()

    return jsonify(dict(success=True, docid=str(_id)))


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
