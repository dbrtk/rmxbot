"""Module that holds queries and fiunction for data retireval. All methods
   return json objects.
"""

import json
import os
import typing
import uuid

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


def paginate(start: int = 0, limit: int = 100):
    """
    Paginates the collection that holds corpora.
    :param start:
    :param limit:
    :return:
    """
    cursor = CorpusModel.range_query(
        query={'crawl_ready': True},
        projection=dict(),
        limit=limit,
        start=start,
        direction=pymongo.DESCENDING)
    encoder = RmxEncoder()
    return [
        json.loads(encoder.encode(item)) for item in cursor
    ]


def create_from_crawl(name: str = None, endpoint: str = None,
                      crawl: bool = True):
    """Create a corpus from a crawl using scrasync."""
    url_list = [endpoint]

    docid = str(CorpusModel.inst_new_doc(name=name))
    corpus = CorpusModel.inst_by_id(docid)
    corpus.set_corpus_type(data_from_the_web=True)

    depth = DEFAULT_CRAWL_DEPTH if crawl else 0

    # todo(): pass the corpus file path to the crawler.
    crawl_async.delay(url_list, corpus_id=docid, depth=depth)
    return {'success': True}


def crawl(corpusid: str = None, endpoint: str = None, crawl: bool = True):
    """Launching the crawler (scrasync) on an existing corpus"""
    if not CorpusModel.inst_by_id(corpusid):
        abort(404)
    set_crawl_ready(corpusid, False)
    crawl_async.delay([endpoint], corpus_id=corpusid,
                      depth=DEFAULT_CRAWL_DEPTH if crawl else 0)
    return {'success': True}


def corpus_data(corpusid):
    """This returns a corpus data view. It will contain all necesary info
    about a text corpus.
    """
    obj = {}
    status, message = status_text(request.args.get('status'))
    if status:
        obj['status'] = status
        obj['status_message'] = message

    corpus = CorpusModel.inst_by_id(corpusid)
    if not corpus:
        # obj['errors'] = [
        #     ERR_MSGS.get('corpus_does_not_exist').format(corpusid)
        # ]
        raise RuntimeError(
            ERR_MSGS.get('corpus_does_not_exist').format(corpusid)
        )

    obj['available_feats'] = corpus.get_features_count()
    obj['name'] = corpus.get('name')
    obj['corpusid'] = str(corpus.get_id())
    obj['urls_length'] = len(corpus.get('urls'))
    obj['texts'] = [_ for _ in corpus.get('urls')[:10]]

    return obj


def corpus_is_ready(corpusid, feats):
    """Returns an object with information about the state of the corpus.
    This is called when features are being computed.
    """
    feats = int(feats)
    availability = request_availability(corpusid, dict(features=feats))
    availability.update(dict(features=feats))
    return availability


def corpus_crawl_ready(corpusid):
    """Checking if the crawl is ready in order to load the page. This is called
    when the crawler is running."""
    corpus = corpus_status_data(corpusid)
    if not corpus:
        abort(404)

    if corpus.get('crawl_ready') and \
            not corpus.get('integrity_check_in_progress'):
        return {
            'ready': True,
            'corpusid': corpusid
        }
    return {
        'ready': False,
        'corpusid': corpusid
    }


def file_upload_ready(corpusid):
    """Checks if hte corpus created from files is ready."""
    corpus = CorpusModel.inst_by_id(corpusid)
    if not corpus:
        abort(404)

    if corpus.get('crawl_ready'):
        return {
            'ready': True,
            'corpusid': corpusid
        }
    return {
        'ready': False,
        'corpusid': corpusid
    }


def texts(corpusid):
    """Returns an object that contains texts."""
    corpus = CorpusModel.inst_by_id(corpusid)

    outobj = {}
    if not corpus:
        outobj['errors'] = [
            ERR_MSGS.get('corpus_does_not_exist').format(corpusid)
        ]
        return outobj

    dataids = corpus.get_dataids()
    outobj['files_upload_endpoint'] = EXTRACTXT_FILES_UPLOAD_URL.strip(
        '/')
    outobj['datatype'] = 'crawl' if corpus['data_from_the_web'] else \
        'upload' if corpus['data_from_files'] else None
    outobj['corpusid'] = corpus.get('_id')
    outobj['name'] = corpus.get('name')
    outobj['data'] = DataModel.query_data_project(
        query={'_id': {'$in': dataids}},
        project=LISTURLS_PROJECT,
        direct=1)
    return outobj


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


def lemma_context(corpusid, words: typing.List[str] = None):
    """ Returns the context for lemmatised words. Lemmatised words are the
    words that make a feature - feature-words. The context are all sentences
    in the corpus that contain one or more feature-word(s).

    :param corpusid: the corpus id
    :param words: these are feature words (lemmatised by default)
    :return:
    """
    corpus = CorpusModel.inst_by_id(corpusid)
    if not isinstance(words, list) or \
            not all(isinstance(_, str) for _ in words):
        raise ValueError(words)
    lemma_to_words, lemma = corpus.get_lemma_words(words)

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
    return {
        'success': True,
        'corpusid': corpus.get_id(),
        'data': [{'fileid': k, 'sentences': v} for k, v in
                 resp.json().get('data').items()]
    }


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
