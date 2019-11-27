import json
import os
import uuid
from urllib.parse import urlencode

import bson
from flask import (abort, Blueprint, jsonify, redirect, render_template,
                   request)
import pymongo

from ...config import (DEFAULT_CRAWL_DEPTH, EXTRACTXT_FILES_UPLOAD_URL,
                       RMXGREP_ENDPOINT, TEMPLATES)
from ...contrib.rmxjson import RmxEncoder
from ...core import http_request
from ..data.models import (
    DataModel, LIST_SCREENPLAYS_PROJECT, LISTURLS_PROJECT)
from .decorators import check_availability
from .models import (CorpusModel, corpus_status_data, request_availability,
                     set_crawl_ready)
from .status import status_text

from ...tasks.corpus import (crawl_async, delete_data_from_corpus, test_task)

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
    """Create a corpus from a crawl using scrasync."""

    the_name = request.form['name']
    endpoint = request.form['endpoint']
    url_list = [endpoint]
    crawl = request.form.get("crawl", True)
    crawl = True if crawl else crawl

    docid = str(CorpusModel.inst_new_doc(name=the_name))
    corpus = CorpusModel.inst_by_id(docid)
    corpus.set_corpus_type(data_from_the_web=True)

    depth = DEFAULT_CRAWL_DEPTH if crawl else 0

    # todo(): pass the corpus file path to the crawler.
    crawl_async.delay(url_list, corpus_id=docid, depth=depth)

    return redirect(
        '/corpus/{}/?{}'.format(
            str(docid), urlencode(dict(status='newly-created'))))


@corpus_app.route('/crawl/', methods=['POST'])
def crawl():
    """Launching the crawler (scrasync) on an existing corpus"""
    endpoint = request.form['endpoint']
    corpusid = request.form['corpusid']
    crawl = request.form.get("crawl", True)
    crawl = True if crawl else crawl

    if not CorpusModel.inst_by_id(corpusid):
        abort(404)

    set_crawl_ready(corpusid, False)
    crawl_async.delay([endpoint], corpus_id=corpusid,
                      depth=DEFAULT_CRAWL_DEPTH if crawl else 0)
    return redirect(
        '/corpus/{}/?{}'.format(
            str(corpusid), urlencode(dict(status='crawling'))))


@corpus_app.route('/test-task/<a>/<b>/')
def view_test_task(a, b):

    res = test_task.delay(int(a), int(b))
    return jsonify({'success': True, 'result': res.get()})


@corpus_app.route('/<objectid:corpusid>/', methods=['GET'])
def corpus_data_view(corpusid):

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
        return render_template("corpus/data.html", **context)

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
    """Checking if the crawl is ready in order to load the page."""

    corpus = corpus_status_data(corpusid)
    if not corpus:
        abort(404)

    if corpus.get('crawl_ready') and \
            not corpus.get('integrity_check_in_progress'):
        return jsonify({
            'ready': True,
            'corpusid': corpusid
        })
    # todo(): delete.
    # if corpus['data_from_the_web'] and \
    #         not corpus.get('integrity_check_in_progress'):
    #     _corpusid = str(corpusid)
    #     celery.send_task(
    #         SCRASYNC_TASKS['crawl_ready'],
    #         kwargs={'corpusid': _corpusid},
    #         link=on_crawl_ready.s(_corpusid)
    #     )
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


@corpus_app.route('/<objectid:corpusid>/data/')
def texts(corpusid):

    template_name = "corpus/data-view.html"
    corpus = CorpusModel.inst_by_id(corpusid)

    context = {}
    if not corpus:
        context['errors'] = [
            ERR_MSGS.get('corpus_does_not_exist').format(corpusid)
        ]
        return render_template(template_name, **context)

    dataids = corpus.get_dataids()
    context['files_upload_endpoint'] = EXTRACTXT_FILES_UPLOAD_URL.strip(
        '/')
    context['datatype'] = 'crawl' if corpus['data_from_the_web'] else \
        'upload' if corpus['data_from_files'] else None
    context['corpusid'] = corpus.get('_id')
    context['name'] = corpus.get('name')
    context['data'] = DataModel.query_data_project(
        query={'_id': {'$in': dataids}},
        project=LISTURLS_PROJECT,
        direct=1)

    return render_template(template_name, **context)


@corpus_app.route('/<objectid:corpusid>/data/edit/', methods=['GET'])
def edit_corpus(corpusid):

    template_name = "corpus/data-view-edit.html"
    corpus = CorpusModel.inst_by_id(corpusid)

    context = {}
    if not corpus:
        context['errors'] = [
            ERR_MSGS.get('corpus_does_not_exist').format(corpusid)
        ]
        return render_template(template_name, **context)
    dataids = corpus.get_dataids()
    context['datatype'] = 'screenplay'
    context['corpusid'] = corpus.get('_id')
    context['name'] = corpus.get('name')
    context['data'] = DataModel.query_data_project(
        query={'_id': {'$in': dataids}},
        project=LIST_SCREENPLAYS_PROJECT,
        direct=1)
    return render_template(template_name, **context)


@corpus_app.route('/<objectid:corpusid>/data/delete-texts/',
                  methods=['POST', 'GET'])
def delete_texts(corpusid):

    if request.method == 'GET':
        corpus = CorpusModel.inst_by_id(corpusid)
        dataids = corpus.get_dataids()

        context = {
            'corpusid': corpus.get('_id'),
            'name': corpus.get('name'),
            'data': DataModel.query_data_project(
                query={'_id': {'$in': dataids}},
                project=LISTURLS_PROJECT,
                direct=1),
        }
        return render_template('corpus/delete-texts.html', **context)

    elif request.method == 'POST':
        set_crawl_ready(corpusid, False)
        delete_data_from_corpus.delay(
            corpusid=str(corpusid), data_ids=request.form.getlist('docid'))
        return redirect(
            '/corpus/{}/?status=remove-files'.format(str(corpusid)))
    else:
        return abort(403)


@corpus_app.route('/<objectid:corpusid>/file/<objectid:dataid>/',
                  methods=['GET'])
def get_text_file(corpusid, dataid):

    corpus = CorpusModel.inst_by_id(corpusid)
    try:
        doc = corpus.get_url_doc(str(dataid))
    except (RuntimeError, ):
        return abort(404, 'Requested file does not exist.')
    fileid = doc.get('file_id')
    txt = []
    with open(
            os.path.join(corpus.corpus_files_path(), fileid)
    ) as _file:
        # _file.readline()
        # while True:
        #     _ = _file.readline()
        #     if not _.strip():
        #         continue
        #     else:
        #         txt += _
        #         break
        for _line in _file.readlines():
            _line = _line.strip()
            if _line:
                txt.append(_line)
    return jsonify({'text': txt, 'dataid': dataid, 'length': len(txt)})


@corpus_app.route('/<objectid:corpusid>/context/')
def lemma_context(corpusid):
    """ Returns the context for lemmatised words.

    :param corpusid:
    :return:
    """
    corpus = CorpusModel.inst_by_id(corpusid)
    lemma_to_words, lemma = corpus.get_lemma_words(request.args.get('lemma'))

    matchwords = []
    for i in lemma:
        try:
            mapping = next(_ for _ in lemma_to_words if _.get('lemma') == i)
            matchwords.extend(mapping.get('words'))
        except StopIteration:
            matchwords.append(i)

    resp = http_request.get(
        RMXGREP_ENDPOINT,
        params={
            'words': matchwords,
            'corpus_path': corpus.corpus_files_path()
        })
    data = resp.json()
    return jsonify({
        'success': True,
        'data': data.get('data')
    })


@corpus_app.route('/<objectid:corpusid>/features/')
@check_availability
def request_features(reqobj):

    corpus = reqobj.get('corpus')
    del reqobj['corpus']

    features, docs = corpus.get_features(**reqobj)
    return jsonify(dict(
        success=True,
        features=features,
        docs=docs
    ))


@corpus_app.route('/<objectid:corpusid>/features-html/')
@check_availability
def request_features_html(reqobj):

    corpus = reqobj.get('corpus')
    features, _ = corpus.get_features(**reqobj)
    features = render_template('corpus/features.html',
                               features=features,
                               corpusid=str(corpus.get('_id')))
    return jsonify({'features': features})


@corpus_app.route('/<objectid:corpusid>/force-directed-graph/')
@check_availability
def force_directed_graph(reqobj):
    """ Retrieving data (links and nodes) for a force-directed graph. This
        function maps the documents and features to links and nodes.
    """

    corpus = reqobj.get('corpus')
    del reqobj['corpus']

    features, docs = corpus.get_features(**reqobj)

    links, nodes = [], []

    for f in features:
        f['id'] = str(uuid.uuid4())
        f['group'] = f['id']
        f['type'] = 'feature'
        # cleanup the feat object
        del f['docs']
        nodes.append(f)

    def get_feat(feature):
        for item in nodes:
            if item.get('features') == feature:
                return item
        return None
    for d in docs:
        _f = get_feat(d['features'][0]['feature'])
        d['group'] = _f['id']
        d['id'] = str(uuid.uuid4())
        d['type'] = 'document'

        nodes.append(d)
        for f in d['features']:
            if _f and f['feature'] == _f:
                the_feat = _f
            else:
                the_feat = get_feat(f['feature'])
            _f = None
            if not the_feat:
                continue
            links.append(dict(
                source=d['id'],
                target=the_feat['id'],
                weight=f['weight']
            ))
        # cleanup the doc object
        del d['features']

    return jsonify(
        dict(
            links=links, nodes=nodes, corpusid=str(corpus.get('_id'))
        )
    )
