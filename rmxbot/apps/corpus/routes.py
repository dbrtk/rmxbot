import json
import uuid
from urllib.parse import parse_qs, urlencode, urlparse

import bson
from flask import abort, Blueprint, jsonify, redirect, render_template, request
import pymongo
import requests

from ...config import (DEFAULT_CRAWL_DEPTH, EXTRACTXT_FILES_UPLOAD_URL,
                       MONGODB_OBJECTID_REGEX, SCRASYNC_CRAWL_READY, TEMPLATES)
from ...contrib.db.models.fields.urlfield import validate_url_list
from ...contrib.rmxjson import RmxEncoder
from ..data.models import (
    DataModel, LIST_SCREENPLAYS_PROJECT, LISTURLS_PROJECT)
from .decorators import check_availability
from .models import CorpusModel, request_availability, set_crawl_ready
from .status import CORPUS_STATUS, status_text

from ...tasks.corpus import (crawl_async, delete_data_from_corpus,
                             file_extract_callback, nlp_callback_success,
                             test_task)
from . import scripts

RE_ID = MONGODB_OBJECTID_REGEX

ERR_MSGS = dict(corpus_does_not_exist='A corpus with id: "{}" does not exist.')

corpus_app = Blueprint(
    'corpus_app', __name__, root_path='/corpus', template_folder=TEMPLATES)


@corpus_app.route('/')
def corpus_home():
    """
    :return:
    """
    context = {}
    cursor = CorpusModel.range_query(
        query={'crawl_ready': True},
        projection=dict(),
        direction=pymongo.DESCENDING)
    encoder = RmxEncoder()
    out = []
    for item in cursor:
        item = json.loads(encoder.encode(item))
        if item.get('screenplay', False):
            item['data'] = DataModel.query_data_project(
                query={'_id': {
                    '$in': [bson.ObjectId(_.get('data_id'))
                            for _ in item.get('urls')][:10]
                }},
                project=LIST_SCREENPLAYS_PROJECT
            )
        item['corpusid'] = item['_id']
        del item['_id']
        out.append(item)

    context['data'] = out
    return render_template("corpus/index.html", **context)


@corpus_app.route('/new/')
def new_corpus():

    return render_template('corpus/new.html')


@corpus_app.route('/create-from-text-files/')
def create_from_txt_files():

    return render_template("corpus/create-from-text-files.html",
                           files_upload_endpoint=EXTRACTXT_FILES_UPLOAD_URL)


@corpus_app.route('/create/', methods=['POST'])
def create_from_crawl():

    the_name = request.form['name']
    endpoint = request.form['endpoint']
    url_list = [endpoint]

    crawl = request.form.get("crawl", True)
    crawl = True if crawl else crawl

    docid = str(CorpusModel.inst_new_doc(name=the_name))
    corpus = CorpusModel.inst_by_id(docid)
    corpus.set_corpus_type(data_from_the_web=True)

    corpus_file_path = corpus.corpus_files_path()

    depth = DEFAULT_CRAWL_DEPTH if crawl else 0

    # todo(): pass the corpus file path to the crawler.
    crawl_async.delay(url_list, corpus_id=docid, crawl=crawl, depth=depth,
                      corpus_file_path=corpus_file_path)

    return redirect(
        '/corpus/{}/?{}'.format(
            str(docid), urlencode(dict(status='newly-created'))))


@corpus_app.route('/test-task/<a>/<b>/')
def view_test_task(a, b):

    res = test_task.delay(a, b)
    return jsonify({'success': True, 'result': res.get()})


@corpus_app.route('/<objectid:corpusid>/'.format(RE_ID), methods=['GET'])
def corpus_data(corpusid):

    context = {}
    status, message = status_text(request.args.get('status'))
    if status:
        context['status'] = status
        context['status_message'] = message

    corpus = CorpusModel.inst_by_id(corpusid)
    if not corpus:
        context['errors'] = [
            ERR_MSGS.get('corpus_does_not_exist').format(corpusid)
        ]
        return context

    context['available_feats'] = corpus.get_features_count()
    context['corpus_name'] = corpus.get('name')
    context['corpusid'] = str(corpus.get_id())
    context['urls_length'] = len(corpus.get('urls'))
    context['texts'] = [_ for _ in corpus.get('urls')[:10]]

    return render_template("corpus/data.html", **context)


@corpus_app.route('/<objectid:corpusid>/is-ready/<feats>/', methods=['GET'])
def corpus_is_ready(corpusid, feats):

    feats = int(feats)
    availability = request_availability(corpusid, dict(features=feats))
    availability.update(dict(features=feats))

    return jsonify(availability)


@corpus_app.route('/<objectid:corpusid>/corpus-crawl-ready/', methods=['GET'])
def corpus_crawl_ready(corpusid):

    corpus = CorpusModel.inst_by_id(corpusid)
    if not corpus:
        abort(404)

    if corpus.get('crawl_ready'):
        return jsonify({
            'ready': True,
            'corpusid': corpusid
        })
    if corpus['data_from_the_web']:
        endpoint = '{}/'.format(
            '/'.join(s.strip('/') for s in [SCRASYNC_CRAWL_READY, corpusid]))

        resp = requests.get(endpoint).json()

        if resp.get('ready'):
            set_crawl_ready(corpusid, True)
    return jsonify({
        'ready': False,
        'corpusid': corpusid
    })


@corpus_app.route('/<objectid:corpusid>/corpus-from-files-ready/',
                  methods=['GET'])
def corpus_from_files_ready(corpusid):

    corpus = CorpusModel.inst_by_id(corpusid)
    if not corpus:
        abort(404)

    if corpus.get('crawl_ready'):
        return jsonify({
            'ready': True,
            'corpusid': corpusid
        })
    return jsonify({
        'ready': False,
        'corpusid': corpusid
    })

