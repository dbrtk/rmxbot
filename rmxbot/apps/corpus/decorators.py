
# from functools import wraps

from django.http import JsonResponse

from .models import CorpusModel, request_availability
from .tasks import generate_matrices_remote


def check_availability(func):

    def wrapped_view(request, docid):

        if not request.method == 'GET':
            raise RuntimeError("The request method should be GET, got %s "
                               "instead." % request.method)

        reqobj = request.GET
        _words = int(reqobj.get('words', 10))
        _features = int(reqobj.get('features', 10))
        _docsperfeat = int(reqobj.get('docsperfeat', 5))
        _featsperdoc = int(reqobj.get('featsperdoc', 3))
        _html = reqobj.get('html', False)

        corpus = CorpusModel.inst_by_id(docid)

        availability = request_availability(docid, {
            'features': _features,
        }, corpus=corpus)

        if availability.get('busy'):
            return JsonResponse(dict(busy=True, success=False))

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
            vectors_in_corpus=corpus.vectors_in_corpus,
            vectors_path=corpus.get_vectors_path(),
            words=_words,
            docs_per_feat=_docsperfeat,
            feats_per_doc=_featsperdoc
        )
        out = dict(success=False, retry=True, watch=True)
        out.update(availability)
        return JsonResponse(out)

    # todo(): review
    # return wraps(func, assigned=available_attrs(func))(wrapped_view)
    return wrapped_view
