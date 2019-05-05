""" views to the DataModel model
"""
import hashlib
import os
import stat

from flask import (Blueprint, get_flashed_messages, jsonify, redirect,
                   render_template, request)

from ...tasks import data as data_tasks
from ...config import TEMPLATES
from .models import DataModel, update_many


data_app = Blueprint(
    'data_app', __name__, root_path='/data', template_folder=TEMPLATES)


# @data_app.route('/create-data-object/', methods=['POST'])
# def create():
#     """Creates a data object. This endpoint is called from scrasync for every
#        scraped page.
#     """
#     # todo(): delete!
#     if not request.is_json:
#         raise RuntimeError(request)
#     content = request.get_json()
#     data_tasks.call_data_create.delay(**content)
#     return jsonify({'success': True})


@data_app.route('/create-from-file/', methods=['POST'])
def create_from_file():

    hasher = hashlib.md5()
    kwds = request.POST.dict()
    corpusid = kwds.get('corpusid')
    doc, file_id = DataModel.create_empty(
        corpusid=corpusid,
        title=kwds.get('file_name'))
    docid = str(doc.get('_id'))
    encoding = kwds.get('charset', 'utf8')

    file_path = os.path.join(kwds.get('corpus_files_path'), file_id)
    # todo(): use DataModel.data_to_corpus to create the file
    with open(file_path, '+a') as out:
        out.write('{}\n\n'.format(docid))
        for _line in request.FILES['file'].readlines():
            if isinstance(_line, bytes):
                hasher.update(_line)
            else:
                hasher.update(bytes(_line, encoding=encoding))
            out.write('{}'.format(
                _line.decode(encoding)
            ))
    os.chmod(file_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
    _hash = hasher.hexdigest()
    try:
        doc.set_hashtxt(value=_hash)
    except ValueError:
        doc.rm_doc()
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({
            'success': False,
            'data_id': docid,
            'corpusid': kwds.get('corpusid')
        })
    return jsonify({'success': True,
                    'data_id': docid,
                    'texthash': _hash,
                    'file_id': file_id,
                    'file_path': file_path,
                    'file_name': kwds.get('file_name')})


@data_app.route('/')
def index():
    """The page serving the data index that shows scrapped pages."""

    data = DataModel.get_directory(
        start=request.args.get('start', 0),
        limit=request.args.get('limit', 100)
    )
    context = dict(
        success=True,
        data=data,
        errors=[msg.message for msg in get_flashed_messages()
                if msg.level_tag == 'error']
    )
    return render_template("data.html", **context)


@data_app.route('/webpage/<objectid:docid>/')
def webpage(docid):
    """ displays the page - the doc and its structure.
    """
    document = DataModel.inst_by_id(docid)
    if not isinstance(document, DataModel):
        return jsonify(dict(success=False, msg='No doc found.'))
    return jsonify(dict(document))


@data_app.route('/data-to-corpus/')
def data_to_corpus():

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

    data = request.POST
    out = {}
    for k, v in data.items():
        _ = k.split('_')
        docid = _.pop(0)
        field = '_'.join(_)
        if docid not in out:
            out[docid] = {}
        out[docid][field] = v
    update_many(out)
    return redirect(request.META.get('HTTP_REFERER'))
