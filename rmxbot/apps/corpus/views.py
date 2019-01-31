import json
import os
import re
import shutil
import tempfile
from urllib.parse import urlencode
import uuid

import bson
from django.http import (Http404, HttpResponse,
                         HttpResponseRedirect, JsonResponse)
from django.template.loader import get_template
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.views import View
import pymongo
import requests

from ...config import (DEFAULT_CRAWL_DEPTH,
                       EXTRACTXT_FILES_UPLOAD_URL, SCRASYNC_CRAWL_READY)
from ...contrib.db.models.fields.urlfield import validate_url_list
from ...contrib.rmxjson import RmxEncoder
from ..data.models import (
    DataModel, LIST_SCREENPLAYS_PROJECT, LISTURLS_PROJECT)

from ..data.tasks import file_uploads_to_data
from .decorators import check_availability
from .models import CorpusModel, request_availability, set_crawl_ready
from .tasks import (crawl_async, file_extract_callback, nlp_callback_success,
                    test_task)
from . import scripts


ERR_MSGS = dict(corpus_does_not_exist='A corpus with id: "{}" does not exist.')


class CreateFormView(TemplateView):

    template_name = "corpus/new.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@csrf_exempt
def create(request):
    if not request.method == 'POST':
        raise RuntimeError("The request method should be POST, got %s "
                           "instead." % request.method)
    request_dict = request.POST
    if not any(_ in request_dict for _ in ['urls', 'endpoint']):
        raise ValueError("The url is missing.")

    url_list = request_dict.get("urls", '')
    if url_list:
        url_list = list(_.strip() for _ in url_list.split('\n'))
        url_list = list(validate_url_list(url_list))
    else:
        endpoint = request_dict.get("endpoint").strip()
        url_list = [endpoint]

    the_name = request_dict.get("name")
    crawl = request_dict.get("crawl", True)
    crawl = True if crawl else crawl

    docid = str(CorpusModel.inst_new_doc(name=the_name))
    corpus = CorpusModel.inst_by_id(docid)
    corpus.set_corpus_type(data_from_the_web=True)

    corpus_file_path = corpus.corpus_files_path()

    depth = DEFAULT_CRAWL_DEPTH if crawl else 0

    # todo(): pass the corpus file path to the crawler.
    crawl_async.delay(url_list, corpus_id=docid, crawl=crawl, depth=depth,
                      corpus_file_path=corpus_file_path)

    return HttpResponseRedirect(
        '/corpus/{}/?{}'.format(
            str(docid), urlencode(dict(status='newly-created'))))


@csrf_exempt
def create_from_upload(request):
    """Creating an empty corpus, with a name as given."""

    data = json.loads(request.body)
    the_name = data.get('name')
    file_objects = data.get('file_objects')
    docid = str(CorpusModel.inst_new_doc(name=the_name))
    corpus = CorpusModel.inst_by_id(docid)

    corpus['expected_files'] = file_objects

    # todo(): set status to busy
    corpus.set_corpus_type(data_from_files=True)

    corpus.save()

    return JsonResponse({
        'corpusid': docid,
        'corpus_path': corpus.get_corpus_path(),
        'corpus_files_path': corpus.corpus_files_path()
    })


@csrf_exempt
def file_extract_callback_view(request):
    """
    :param request:
    :return:
    """
    kwds = request.POST.dict()

    file_extract_callback.delay(**kwds)
    return JsonResponse({'success': True})


class CorpusBase(TemplateView):
    """Base class for views that retrieve corpus data."""
    def get(self, request, *args, **kwds):

        if not CorpusModel.inst_by_id(kwds.get('docid')).get('crawl_ready'):
            if not request.GET.get('status', None) == 'newly-created':
                return HttpResponseRedirect(
                    '/corpus/{}/?status=newly-created'.format(kwds.get('docid')))
        return super().get(request, *args, **kwds)


class CorpusDataView(CorpusBase):

    template_name = "corpus/data.html"

    def get_context_data(self, **kwds):

        corpus = CorpusModel.inst_by_id(kwds.get('docid'))

        context = super().get_context_data(**kwds)
        if not corpus:
            context['errors'] = [
                ERR_MSGS.get('corpus_does_not_exist').format(kwds.get('docid'))
            ]
            return context
        if corpus.get('screenplay'):
            context['datatype'] = 'screenplay'
            context['titles'] = [
                _.get('title') for _ in corpus.get('urls')[:10]]
            context['data'] = DataModel.query_data_project(
                query={'_id': {
                    '$in': [
                        bson.ObjectId(_.get('data_id'))
                        for _ in corpus.get('urls')
                    ][:10]
                }},
                project=LIST_SCREENPLAYS_PROJECT
            )
        else:
            context['datatype'] = 'crawl'
        context['available_feats'] = corpus.get_features_count()
        context['corpus_name'] = corpus.get('name')
        context['urls_length'] = len(corpus.get('urls'))
        context['urls'] = [_.get('url') for _ in corpus.get('urls')[:10]]
        return context


class IndexView(TemplateView):
    """
    """
    template_name = "corpus/index.html"

    def get_context_data(self, **kwds):
        context = super().get_context_data(**kwds)
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

            if '_id' in item:
                item['id'] = item['_id']
                del item['_id']
            out.append(item)
        context['data'] = out
        return context


def context_to_json(string: str = None):

    pattern = r"([a-z0-9]+)\:(.*)"
    data = re.findall(pattern, string)

    out = {}
    for docid, txt in data:

        if docid not in out:
            out[docid] = []
        else:
            if txt in out[docid]:
                continue
        out[docid].append(txt)

    return out


def tag_words_corpus(matchwords: list = None, txt: str = None):

    return re.sub(
        r"\b({})\b".format('|'.join(matchwords)),
        r'<span class="match">\1</span>',
        txt,
        flags=re.IGNORECASE
    )


def lemma_context(request, corpusid: str = None):

    obj = request.GET
    corpus = CorpusModel.inst_by_id(corpusid)
    lemma_to_words, lemma = corpus.get_lemma_words(obj.get('lemma'))

    matchwords = []
    for i in lemma:
        try:
            mapping = next(_ for _ in lemma_to_words if _.get('lemma') == i)
            matchwords.extend(mapping.get('words'))
        except StopIteration:
            matchwords.append(i)

    result = scripts.words_context(lemma=matchwords, corpus=corpus)

    result = tag_words_corpus(matchwords, result)
    data = context_to_json(result)

    return JsonResponse({
        'success': True,
        'data': data
    })


class CorpusTextFilesView(TemplateView):

    template_name = "corpus/data-view.html"

    def get_context_data(self, **kwds):
        corpus = CorpusModel.inst_by_id(kwds.get('docid'))

        context = super().get_context_data(**kwds)
        if not corpus:
            context['errors'] = [
                ERR_MSGS.get('corpus_does_not_exist').format(kwds.get('docid'))
            ]
            return context
        dataids = corpus.get_dataids()
        context['datatype'] = 'screenplay'
        context['corpusid'] = corpus.get('_id')
        context['name'] = corpus.get('name')
        context['data'] = DataModel.query_data_project(
            query={'_id': {'$in': dataids}},
            project=LIST_SCREENPLAYS_PROJECT,
            direct=1)

        return context


class CorpusDataEditView(TemplateView):

    template_name = "corpus/data-view-edit.html"

    def get_context_data(self, **kwds):
        corpus = CorpusModel.inst_by_id(kwds.get('docid'))

        context = super().get_context_data(**kwds)
        if not corpus:
            context['errors'] = [
                ERR_MSGS.get('corpus_does_not_exist').format(kwds.get('docid'))
            ]
            return context
        dataids = corpus.get_dataids()
        context['datatype'] = 'screenplay'
        context['corpusid'] = corpus.get('_id')
        context['name'] = corpus.get('name')
        context['data'] = DataModel.query_data_project(
            query={'_id': {'$in': dataids}},
            project=LIST_SCREENPLAYS_PROJECT,
            direct=1)
        return context


class CorpusUrlsView(CorpusBase):

    template_name = "corpus/data-view.html"

    def get_context_data(self, **kwds):
        corpus = CorpusModel.inst_by_id(kwds.get('docid'))

        context = super().get_context_data(**kwds)
        if not corpus:
            context['errors'] = [
                ERR_MSGS.get('corpus_does_not_exist').format(kwds.get('docid'))
            ]
            return context
        dataids = corpus.get_dataids()
        context['files_upload_endpoint'] = EXTRACTXT_FILES_UPLOAD_URL.strip(
            '/')
        context['datatype'] = 'crawl'
        context['corpusid'] = corpus.get('_id')
        context['name'] = corpus.get('name')
        context['data'] = DataModel.query_data_project(
            query={'_id': {'$in': dataids}},
            project=LISTURLS_PROJECT,
            direct=1)

        return context


def features_to_html(feats, corpusid):
    feat_tpl = get_template('corpus/features.html')
    return feat_tpl.render(dict(features=feats, corpusid=corpusid))


def documents_to_html(docs):

    doc_tpl = get_template('corpus/documents.html')
    return doc_tpl.render(dict(documents=docs))


@check_availability
def request_features(reqobj):

    corpus = reqobj.get('corpus')
    del reqobj['corpus']

    features, docs = corpus.get_features(**reqobj)
    return JsonResponse(dict(
        success=True,
        features=features,
        docs=docs
    ))


@check_availability
def request_features_html(reqobj):
    corpus = reqobj.get('corpus')
    features, _ = corpus.get_features(**reqobj)
    return JsonResponse(
        dict(
            features=features_to_html(features, str(corpus.get('_id')))
        )
    )


def get_text_file(request, corpusid, dataid):
    if not request.method == 'GET':
        raise RuntimeError("The request method should be POST, got %s "
                           "instead." % request.method)
    corpus = CorpusModel.inst_by_id(corpusid)
    try:
        doc = corpus.get_url_doc(dataid)
    except (RuntimeError, ):
        raise Http404('Requested file does not exist.')
    fileid = doc.get('file_id')
    txt = ''
    with open(
            os.path.join(corpus.get_corpus_path(), 'corpus', fileid)
    ) as _file:
        _file.readline()
        while True:
            _ = _file.readline()
            if not _.strip():
                continue
            else:
                txt += _
                break
        for _ in _file.readlines():
            txt += _
    return HttpResponse(txt, content_type='text/plain')


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

    return JsonResponse(
        dict(
            links=links, nodes=nodes, corpusid=str(corpus.get('_id'))
        )
    )


def request_kmeans(request, docid):

    if not request.method == 'GET':
        raise RuntimeError("The request method should be POST, got %s "
                           "instead." % request.method)
    return JsonResponse(dict(success=True, msg='Not implemented!'))


def is_ready(request, corpusid, feats):
    """ Checking if the features were computed for a given number.
        Replacing the messages sent through WebSockets.
    """

    feats = int(feats)
    availability = request_availability(corpusid, dict(features=feats))
    availability.update(dict(features=feats))
    return JsonResponse(availability)


def crawl_is_ready(request, docid):
    """ Checking if the crawl is ready. """

    corpus = CorpusModel.inst_by_id(docid)
    if not corpus:
        raise Http404

    if corpus.get('crawl_ready'):
        return JsonResponse({
            'ready': True,
            'corpusid': docid
        })
    if corpus['data_from_the_web']:
        endpoint = '{}/'.format(
            '/'.join(s.strip('/') for s in [SCRASYNC_CRAWL_READY, docid]))

        resp = requests.get(endpoint).json()

        if resp.get('ready'):
            set_crawl_ready(docid, True)
    return JsonResponse({
        'ready': False,
        'corpusid': docid
    })


def corpus_from_files_ready(request, docid):

    corpus = CorpusModel.inst_by_id(docid)
    if not corpus:
        raise Http404

    if corpus.get('crawl_ready'):
        return JsonResponse({
            'ready': True,
            'corpusid': docid
        })
    return JsonResponse({
        'ready': False,
        'corpusid': docid
    })



def test_celery_task(request):
    """Testing celery."""
    res = test_task.delay(1, 2)
    return JsonResponse({'success': True, 'result': res.get()})


@csrf_exempt
def nlp_callback(request):

    obj = json.loads(request.POST.get('payload'))
    corpus = CorpusModel.inst_by_id(obj.get('corpusid'))

    shutil.unpack_archive(
        request.FILES['file'].temporary_file_path(),
        corpus.wf_path,
        'zip'
    )

    error = obj.get('error')
    if error:
        pass
    else:
        nlp_callback_success.apply_async(kwargs=obj)

    return JsonResponse({'success': True})


@csrf_exempt
def compute_matrices_callback(request):

    kwds = json.loads(request.body)
    corpusid = kwds.get('corpusid')
    feats = kwds.get('feats')

    corpus = CorpusModel.inst_by_id(corpusid)
    corpus.del_status_feats(feats=feats)

    return JsonResponse({'success': True})


class CreateFromTextFiles(TemplateView):

    template_name = "corpus/create-from-text-files.html"

    def get_context_data(self, **kwds):
        context = super().get_context_data(**kwds)
        context['files_upload_endpoint'] = EXTRACTXT_FILES_UPLOAD_URL
        return context


def create_corpus_upload(request):
    """ Creating a corpus from uploaded files. """
    # this is the old fundtion/ view that handles the creation of a corpus from
    # upload.
    # todo(): review and delete.

    files = request.FILES.getlist('files')

    the_name = request.POST.get('name')
    # the_id = request.POST.get('id', None)

    docid = str(CorpusModel.inst_new_doc(name=the_name, screenplay=True))
    corpus = CorpusModel.inst_by_id(docid)

    corpus_file_path = corpus.corpus_files_path()
    encoding = "utf-8"

    files_obj = {}
    for _file in files:
        # todo(): delete
        # outf_name = None
        file_name = _file.name
        with tempfile.NamedTemporaryFile(delete=False) as outf:
            outf_name = outf.name
            for line in _file.readlines():
                outf.write(line)
        _file.close()
        files_obj[file_name] = outf_name

    file_uploads_to_data.delay(
        corpusid=docid, files=files_obj, encoding=encoding,
        corpus_file_path=corpus_file_path)

    return HttpResponseRedirect(
        '/corpus/{}/?{}'.format(
            str(docid), urlencode(dict(status='newly-created'))))


def update_corpus_upload(request):

    corpusid = request.POST.get('corpusid')

    return HttpResponse('ok')


@csrf_exempt
def sync_matrices(request):
    """Synchronizing matrices after these have been computed and returned by
       NLP.
    """
    params = request.POST.dict()
    path = request.FILES['file'].temporary_file_path()
    corpus = CorpusModel.inst_by_id(params.get('corpusid'))

    shutil.unpack_archive(path, corpus.matrix_path)

    if os.path.exists(path):
        os.remove(path)

    corpus.del_status_feats(feats=int(params.get('feats')))
    return JsonResponse({'success': True, 'corpusid': params.get('corpusid')})


def corpus_data(request):

    corpusid = request.GET.get('corpusid')
    corpus = CorpusModel.inst_by_id(corpusid)
    if not corpus:
        raise Http404

    return JsonResponse({
        'success': True,
        'corpusid': corpusid,
        'vectors_path': corpus.get_vectors_path(),
        'corpus_files_path': corpus.corpus_files_path(),
        # 'lemma_path': corpus.get_lemma_path(),
        'matrix_path': corpus.matrix_path,
        'wf_path': corpus.wf_path,
    })


class ExpectedFiles(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """
        https://docs.djangoproject.com/en/2.1/topics/class-based-views/intro/
        decorating-the-class
        :param args:
        :param kwargs:
        :return:
        """
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        """Saving expected_files."""

        req_obj = request.POST.dict()

        corpusid = req_obj.get('corpusid')
        file_objects = json.loads(req_obj.get('file_objects'))

        CorpusModel.update_expected_files(
            corpusid=corpusid, file_objects=file_objects)

        return JsonResponse({'corpusid': corpusid, 'success': True})

