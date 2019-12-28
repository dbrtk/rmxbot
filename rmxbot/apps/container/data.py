"""Module that holds queries and fiunction for data retireval. All methods
   return json objects.
"""

import json
import os
import typing
import uuid

from flask import abort, request
import pymongo

from ...config import (DEFAULT_CRAWL_DEPTH, EXTRACTXT_FILES_UPLOAD_URL,
                       RMXGREP_ENDPOINT)
from ...contrib.rmxjson import RmxEncoder
from ...core import http_request
from ..data.models import DataModel, LISTURLS_PROJECT
from .decorators import neo_availability
from .models import (ContainerModel, container_status, request_availability,
                     set_crawl_ready)
from .status import status_text

from ...tasks.container import crawl_async, delete_data_from_corpus

ERR_MSGS = dict(container_does_not_exist='A container with id: "{}" does not exist.')


def paginate(start: int = 0, limit: int = 100):
    """
    Paginates the collection that holds corpora.
    :param start:
    :param limit:
    :return:
    """
    cursor = ContainerModel.range_query(
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
    """Create a container from a crawl using scrasync."""
    url_list = [endpoint]

    docid = str(ContainerModel.inst_new_doc(name=name))
    corpus = ContainerModel.inst_by_id(docid)
    corpus.set_container_type(data_from_the_web=True)

    depth = DEFAULT_CRAWL_DEPTH if crawl else 0

    # todo(): pass the corpus file path to the crawler.
    crawl_async.delay(url_list, corpus_id=docid, depth=depth)
    return {'success': True, 'corpusid': corpus.get_id()}


def crawl(corpusid: str = None, endpoint: str = None, crawl: bool = True):
    """Launching the crawler (scrasync) on an existing corpus"""
    corpus = ContainerModel.inst_by_id(corpusid)
    if not corpus:
        abort(404)
    set_crawl_ready(corpusid, False)
    crawl_async.delay([endpoint], corpus_id=corpusid,
                      depth=DEFAULT_CRAWL_DEPTH if crawl else 0)
    return {'success': True, 'corpusid': corpus.get_id()}


def container_data(containerid):
    """This returns a container data view. It will contain all necesary info
    about a text container.
    """
    obj = {}
    status, message = status_text(request.args.get('status'))
    if status:
        obj['status'] = status
        obj['status_message'] = message

    corpus = ContainerModel.inst_by_id(containerid)
    if not corpus:
        # obj['errors'] = [
        #     ERR_MSGS.get('container_does_not_exist').format(corpusid)
        # ]
        raise RuntimeError(
            ERR_MSGS.get('container_does_not_exist').format(containerid)
        )

    obj['available_feats'] = corpus.get_features_count()
    obj['name'] = corpus.get('name')
    obj['corpusid'] = str(corpus.get_id())
    obj['urls_length'] = len(corpus.get('urls'))
    obj['texts'] = [_ for _ in corpus.get('urls')[:10]]

    return obj


def container_is_ready(containerid, feats):
    """Returns an object with information about the state of the container.
    This is called when features are being computed.
    """
    feats = int(feats)
    availability = request_availability(containerid, dict(features=feats))
    availability.update(dict(features=feats))
    return availability


def crawl_is_ready(containerid):
    """Checking if the crawl is ready in order to load the page. This is called
    when the crawler is running."""
    container = container_status(containerid)
    if not container:
        abort(404)

    if container.get('crawl_ready') and \
            not container.get('integrity_check_in_progress'):
        return {
            'ready': True,
            'corpusid': containerid
        }
    return {
        'ready': False,
        'corpusid': containerid
    }


def file_upload_ready(containerid):
    """Checks if hte container created from files is ready."""
    corpus = ContainerModel.inst_by_id(containerid)
    if not corpus:
        abort(404)

    if corpus.get('crawl_ready'):
        return {
            'ready': True,
            'corpusid': containerid
        }
    return {
        'ready': False,
        'corpusid': containerid
    }


def texts(containerid):
    """Returns an object that contains texts."""
    container = ContainerModel.inst_by_id(containerid)

    outobj = {}
    if not container:
        outobj['errors'] = [
            ERR_MSGS.get('container_does_not_exist').format(containerid)
        ]
        return outobj

    dataids = container.get_dataids()
    outobj['files_upload_endpoint'] = EXTRACTXT_FILES_UPLOAD_URL.strip(
        '/')
    outobj['datatype'] = 'crawl' if container['data_from_the_web'] else \
        'upload' if container['data_from_files'] else None
    outobj['corpusid'] = container.get('_id')
    outobj['name'] = container.get('name')
    outobj['data'] = DataModel.query_data_project(
        query={'_id': {'$in': dataids}},
        project=LISTURLS_PROJECT,
        direct=1)
    return outobj


def delete_texts(containerid: str = None, dataids: typing.List[str] = None):
    """
    Deleting texts from the data set.

    :param containerid:
    :param dataids:
    :return:
    """
    if not all(isinstance(str, _) for _ in dataids):
        raise ValueError(dataids)
    set_crawl_ready(containerid, False)
    delete_data_from_corpus.delay(corpusid=containerid, data_ids=dataids)
    return {'success': True}


def get_text_file(containerid, dataid):
    """
    Returns the content of a text file in the data-set.
    :param containerid:
    :param dataid:
    :return:
    """
    container = ContainerModel.inst_by_id(containerid)
    try:
        doc = container.get_url_doc(str(dataid))
    except (RuntimeError, ):
        return abort(404, 'Requested file does not exist.')
    fileid = doc.get('file_id')
    txt = []
    with open(
            os.path.join(container.texts_path(), fileid)
    ) as _file:
        for _line in _file.readlines():
            _line = _line.strip()
            if _line:
                txt.append(_line)
    return {
        'text': txt,
        'dataid': dataid,
        'length': len(txt),
        'corpusid': container.get_id()
    }


def lemma_context(containerid, words: typing.List[str] = None):
    """
    Returns the context for lemmatised words. Lemmatised words are the words
    that make a feature - feature-words. The context are all sentences in the
    container that contain one or more feature-word(s).

    :param containerid: the container id
    :param words: these are feature words (lemmatised by default)
    :return:
    """
    container = ContainerModel.inst_by_id(containerid)
    if not isinstance(words, list) or \
            not all(isinstance(_, str) for _ in words):
        raise ValueError(words)
    lemma_to_words, lemma = container.get_lemma_words(words)

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
            'corpus_path': container.texts_path()
        })
    return {
        'success': True,
        'corpusid': container.get_id(),
        'data': [{'fileid': k, 'sentences': v} for k, v in
                 resp.json().get('data').items()]
    }


@neo_availability
def request_features(reqobj):
    """Checks for features availability and returns these.
    :param reqobj:
    :return:
    """
    corpus = reqobj.get('container')
    del reqobj['corpus']

    features, docs = corpus.get_features(**reqobj)
    return dict(
        success=True,
        features=features,
        docs=docs
    )


@neo_availability
def graph(reqobj):
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

    return {
        'success': True,
        'edge': links,
        'node': nodes,
        'corpusid': str(container.get_id())
    }
