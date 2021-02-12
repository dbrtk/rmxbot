""" Routes for the corpus module. """
import json
import os
import time
import uuid
from urllib.parse import urlencode

import bson
from flask import (abort, Blueprint, jsonify, redirect, render_template,
                   request)
import pymongo
import requests

from ...app import celery
from ...config import (DEFAULT_CRAWL_DEPTH, EXTRACTXT_FILES_UPLOAD_URL,
                       TEMPLATES)
from ...contrib.rmxjson import RmxEncoder
from ..data.models import (
    DataModel, LIST_SCREENPLAYS_PROJECT, LISTURLS_PROJECT)
from .decorators import check_availability
from .models import (ContainerModel, container_status, request_availability,
                     set_crawl_ready)
from .status import status_text
from ...tasks.celeryconf import (NLP_TASKS, RMXCLUSTER_TASKS, RMXBOT_TASKS,
                                 RMXGREP_TASK, SCRASYNC_TASKS)
from ...tasks.container import (crawl_async, delete_data_from_container, test_task)

ERR_MSGS = dict(
    container_does_not_exist='A container with id: "{}" does not exist.')

container_app = Blueprint(
    'container_app', __name__, root_path='/container', template_folder=TEMPLATES)


@container_app.route('/')
def container_home():
    """ Renders the home page for the corpus.
    :return:
    """
    context = {}
    cursor = ContainerModel.range_query(
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


@container_app.route('/new/')
def new_corpus():

    return render_template('corpus/new.html')


@container_app.route('/create-from-text-files/')
def create_from_txt_files():

    return render_template("corpus/create-from-text-files.html",
                           files_upload_endpoint=EXTRACTXT_FILES_UPLOAD_URL)


@container_app.route('/create/', methods=['POST'])
def create_from_crawl():
    """Create a corpus from a crawl using scrasync."""

    the_name = request.form['name']
    endpoint = request.form['endpoint']
    url_list = [endpoint]
    crawl = request.form.get("crawl", True)
    crawl = True if crawl else crawl

    docid = str(ContainerModel.inst_new_doc(name=the_name))
    corpus = ContainerModel.inst_by_id(docid)
    corpus.set_container_type(data_from_the_web=True)

    depth = DEFAULT_CRAWL_DEPTH if crawl else 0

    # todo(): pass the corpus file path to the crawler.
    celery.send_task(
        RMXBOT_TASKS['crawl_async'],
        kwargs={
            'url_list': url_list,
            'corpus_id': docid,
            'depth': depth
        }
    )

    # crawl_async.delay(url_list, corpus_id=docid, depth=depth)

    return redirect(
        '/container/{}/?{}'.format(
            str(docid), urlencode(dict(status='newly-created'))))


@container_app.route('/crawl/', methods=['POST'])
def crawl():
    """Launching the crawler (scrasync) on an existing corpus"""
    endpoint = request.form['endpoint']
    corpusid = request.form['corpusid']
    crawl = request.form.get("crawl", True)
    crawl = True if crawl else crawl

    if not ContainerModel.inst_by_id(corpusid):
        abort(404)

    set_crawl_ready(corpusid, False)

    celery.send_task(
        RMXBOT_TASKS['crawl_async'],
        kwargs={
            'url_list': [endpoint],
            'corpus_id': corpusid,
            'depth': DEFAULT_CRAWL_DEPTH if crawl else 0
        }
    )

    # crawl_async.delay([endpoint], corpus_id=corpusid,
    #                   depth=DEFAULT_CRAWL_DEPTH if crawl else 0)
    return redirect(
        '/container/{}/?{}'.format(
            str(corpusid), urlencode(dict(status='crawling'))))


@container_app.route('/test-task/<a>/<b>/')
def view_test_task(a, b):

    # res = test_task.delay(int(a), int(b))
    res = celery.send_task(
        RMXBOT_TASKS['test_task'],
        kwargs={
            'a': int(a),
            'b': int(b)
        }
    ).get()
    return jsonify({'success': True, 'result': res})


@container_app.route('/<objectid:corpusid>/', methods=['GET'])
def corpus_data_view(corpusid):

    context = {}
    status, message = status_text(request.args.get('status'))
    if status:
        context['status'] = status
        context['status_message'] = message

    corpus = ContainerModel.inst_by_id(corpusid)
    if not corpus:
        context['errors'] = [
            ERR_MSGS.get('container_does_not_exist').format(corpusid)
        ]
        return render_template("corpus/data.html", **context)

    context['available_feats'] = corpus.get_features_count()
    context['corpus_name'] = corpus.get('name')
    context['corpusid'] = str(corpus.get_id())
    context['urls_length'] = len(corpus.get('urls'))
    context['texts'] = [_ for _ in corpus.get('urls')[:10]]

    return render_template("corpus/data.html", **context)


@container_app.route('/<objectid:corpusid>/is-ready/<feats>/', methods=['GET'])
def corpus_is_ready(corpusid, feats):

    feats = int(feats)
    availability = request_availability(corpusid, dict(features=feats))
    availability.update(dict(features=feats))

    return jsonify(availability)


@container_app.route('/<objectid:corpusid>/container-crawl-ready/', methods=['GET'])
def corpus_crawl_ready(corpusid):
    """Checking if the crawl is ready in order to load the page."""

    corpus = container_status(corpusid)
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


@container_app.route('/<objectid:corpusid>/container-from-files-ready/',
                     methods=['GET'])
def corpus_from_files_ready(corpusid):

    corpus = ContainerModel.inst_by_id(corpusid)
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


@container_app.route('/<objectid:corpusid>/data/')
def texts(corpusid):

    template_name = "corpus/data-view.html"
    corpus = ContainerModel.inst_by_id(corpusid)

    context = {}
    if not corpus:
        context['errors'] = [
            ERR_MSGS.get('container_does_not_exist').format(corpusid)
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


@container_app.route('/<objectid:corpusid>/data/edit/', methods=['GET'])
def edit_corpus(corpusid):

    template_name = "corpus/data-view-edit.html"
    corpus = ContainerModel.inst_by_id(corpusid)

    context = {}
    if not corpus:
        context['errors'] = [
            ERR_MSGS.get('container_does_not_exist').format(corpusid)
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


@container_app.route('/<objectid:corpusid>/data/delete-texts/',
                     methods=['POST', 'GET'])
def delete_texts(corpusid):

    if request.method == 'GET':
        corpus = ContainerModel.inst_by_id(corpusid)
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

        celery.send_task(
            RMXBOT_TASKS['delete_data_from_container'],
            kwargs={
                'corpusid': str(corpusid),
                'data_ids': request.form.getlist('docid')
            }
        )

        # delete_data_from_container.delay(
        #     corpusid=str(corpusid), data_ids=request.form.getlist('docid'))

        return redirect(
            '/container/{}/?status=remove-files'.format(str(corpusid)))
    else:
        return abort(403)


@container_app.route('/<objectid:corpusid>/file/<objectid:dataid>/',
                     methods=['GET'])
def get_text_file(corpusid, dataid):

    corpus = ContainerModel.inst_by_id(corpusid)
    try:
        doc = corpus.get_url_doc(str(dataid))
    except (RuntimeError, ):
        return abort(404, 'Requested file does not exist.')
    fileid = doc.get('file_id')
    txt = []
    with open(
            os.path.join(corpus.texts_path(), fileid)
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


@container_app.route('/<objectid:corpusid>/context/')
def lemma_context(corpusid):
    """ Returns the context for lemmatised words.

    :param corpusid:
    :return:
    """
    corpus = ContainerModel.inst_by_id(corpusid)
    lemma_to_words, lemma = corpus.get_lemma_words(request.args.get('lemma'))

    matchwords = []
    for i in lemma:
        try:
            mapping = next(_ for _ in lemma_to_words if _.get('lemma') == i)
            matchwords.extend(mapping.get('words'))
        except StopIteration:
            matchwords.append(i)

    data = celery.send_task(
        RMXGREP_TASK['search_text'],
        kwargs={
            'highlight': True,
            'words': matchwords,
            'container_path': corpus.texts_path()
        }).get()
    return jsonify({
        'success': True,
        'data': data.get('data')
    })


@container_app.route('/<objectid:corpusid>/features/')
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


@container_app.route('/<objectid:corpusid>/features-html/')
@check_availability
def request_features_html(reqobj):

    corpus = reqobj.get('corpus')
    features, _ = corpus.get_features(**reqobj)
    features = render_template('corpus/features.html',
                               features=features,
                               corpusid=str(corpus.get('_id')))
    return jsonify({'features': features})


@container_app.route('/<objectid:corpusid>/force-directed-graph/')
@check_availability
def force_directed_graph(reqobj):
    """ Retrieving data (links and nodes) for a force-directed graph. This
        function maps the documents and features to links and nodes.
    """

    container = reqobj.get('corpus')
    del reqobj['corpus']

    features, docs = container.get_features(**reqobj)

    links, nodes = [], []

    for f in features:
        f['id'] = uuid.uuid4().hex
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
        d['id'] = uuid.uuid4().hex
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
            links=links, nodes=nodes, corpusid=str(container.get('_id'))
        )
    )


@container_app.route('/<objectid:containerid>/kmeans/<int:feats>')
def kmeans_groups(containerid: str, feats: int):

    container = ContainerModel.inst_by_id(containerid)

    params = celery.send_task(
        NLP_TASKS['kmeans_files'],
        kwargs={
            'path': container.get_folder_path(),
            'containerid': str(containerid)
        }).get()
    params['k'] = feats
    groups = celery.send_task(
        RMXCLUSTER_TASKS['kmeans_groups'],
        kwargs=params
    ).get()

    return jsonify({
        'k': feats,
        'containerid': containerid,
        'groups': groups,
        'success': True,
        'msg': 'Endpoint used for testing and development.'
    })


@container_app.route('/<objectid:containerid>/crawl-metrics')
def crawl_metrics(containerid: str):
    """
    Querying all metrics for scrasync. It is using hte task registered with
    RMXBOT_TASKS.

    the response = {
        'status': 'success',
        'data': {
            'resultType': 'vector',
            'result': [{
                'metric': {
                    '__name__': 'parse_and_save__lastcall_<containerid>',
                    'job': 'scrasync'
                },
                'value': [1613125321.823, '1613125299.354587']
            }, {
                'metric': {
                    '__name__': 'parse_and_save__succes_<containerid>',
                    'job': 'scrasync'
                }, 'value': [1613125321.823, '1613125299.3545368']
            }]
        }
    }
    """
    return celery.send_task(
        RMXBOT_TASKS['crawl_metrics'],
        kwargs={ 'containerid': str(containerid) }
    ).get()
