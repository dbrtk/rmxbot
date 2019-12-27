
from functools import wraps

from flask import jsonify, request

from .models import ContainerModel, request_availability
from ...tasks.corpus import generate_matrices_remote


def check_availability(func):

    @wraps(func)
    def wrapped_view(corpusid):

        if not request.method == 'GET':
            raise RuntimeError("The request method should be GET, got %s "
                               "instead." % request.method)

        reqobj = request.args
        _words = int(reqobj.get('words', 10))
        _features = int(reqobj.get('features', 10))
        _docsperfeat = int(reqobj.get('docsperfeat', 5))
        _featsperdoc = int(reqobj.get('featsperdoc', 3))
        _html = reqobj.get('html', False)

        corpus = ContainerModel.inst_by_id(corpusid)

        availability = request_availability(corpusid, {
            'features': _features,
        }, corpus=corpus)

        if availability.get('busy'):
            return jsonify(dict(busy=True, success=False))

        if availability.get('available'):

            return func(dict(
                words=_words,
                feats=_features,
                docs_per_feat=_docsperfeat,
                feats_per_doc=_featsperdoc,
                html=_html,
                corpus=corpus
            ))
        generate_matrices_remote.delay(
            corpusid=str(corpus.get_id()),
            feats=_features,
            vectors_path=corpus.get_vectors_path(),
            words=_words,
            docs_per_feat=_docsperfeat,
            feats_per_doc=_featsperdoc
        )
        out = dict(success=False, retry=True, watch=True)
        out.update(availability)
        return jsonify(out)

    # todo(): review
    # return wraps(func, assigned=available_attrs(func))(wrapped_view)
    return wrapped_view


def neo_availability(func):
    """Decorator that checks if requested features have been computed. If it's
       not the case, they are generated. This decorator is used by the graphql
       api.
    """
    @wraps(func)
    def wrapped_view(corpusid: str = None, words: int = 10, features: int = 10,
                     docsperfeat: int = 5, featsperdoc: int = 3):

        corpus = ContainerModel.inst_by_id(corpusid)

        availability = request_availability(corpusid, {
            'features': features,
        }, corpus=corpus)

        if availability.get('busy'):
            return {
                'busy': True,
                'watch': True,
                'success': False,
                'corpusid': corpus.get_id()
            }

        if availability.get('available'):

            return func(dict(
                words=words,
                feats=features,
                docs_per_feat=docsperfeat,
                feats_per_doc=featsperdoc,
                corpus=corpus
            ))
        generate_matrices_remote.delay(
            corpusid=str(corpus.get_id()),
            feats=features,
            vectors_path=corpus.get_vectors_path(),
            words=words,
            docs_per_feat=docsperfeat,
            feats_per_doc=featsperdoc
        )
        out = {
            'success': False,
            'retry': True,
            'watch': True,
            'busy': True,
            'corpusid': corpus.get_id()
        }
        out.update(availability)
        return out

    # todo(): review
    # return wraps(func, assigned=available_attrs(func))(wrapped_view)
    return wrapped_view


def graph_availability(func):
    """
    Decorator checking the availability of a graph.
    :param func:
    :return:
    """
    @wraps(func)
    def wrapped_view(reqobj):

        corpusid = reqobj.get('corpusid')
        features = reqobj.get('feats')
        words = reqobj.get('words')
        docs_per_feat = reqobj.get('docs_per_feat')
        feats_per_doc = reqobj.get('feats_per_doc')

        corpus = ContainerModel.inst_by_id(corpusid)

        availability = request_availability(corpusid, {
            'features': features,
        }, corpus=corpus)

        if availability.get('busy'):
            return jsonify(dict(busy=True, success=False))

        if availability.get('available'):

            return func(dict(
                words=words,
                feats=features,
                docs_per_feat=docs_per_feat,
                feats_per_doc=feats_per_doc,
                corpus=corpus
            ))
        generate_matrices_remote.delay(
            corpusid=str(corpus.get_id()),
            feats=features,
            vectors_path=corpus.get_vectors_path(),
            words=words,
            docs_per_feat=docs_per_feat,
            feats_per_doc=feats_per_doc
        )
        out = dict(success=False, retry=True, watch=True)
        out.update(availability)
        return jsonify(out)

    # todo(): review
    # return wraps(func, assigned=available_attrs(func))(wrapped_view)
    return wrapped_view
