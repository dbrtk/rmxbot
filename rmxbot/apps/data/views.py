""" views to the DataModel model
"""
import json

from django.contrib import messages
from django.http import (HttpResponse, HttpResponseRedirect, JsonResponse)
from django.http import QueryDict
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from . import tasks as data_tasks

from rmxbot.contrib import rmxjson

from .models import DataModel, update_many


@csrf_exempt
def create(request):
    """Creates a data object. This endpoint is called from scrasync for every
       scraped page.
    """
    request_dict = json.loads(request.body.decode("utf-8"))

    data_tasks.call_data_create.delay(**request_dict)
    return JsonResponse({'success': True})


def index(request):
    """The page serving the data index that shows scrapped pages."""
    request_dict = request.GET
    data = DataModel.get_directory(
        start=request_dict.get('start', 0),
        limit=request_dict.get('limit', 100)
    )
    storage = messages.get_messages(request)
    context = dict(
        success=True,
        data=data,
        errors=[msg.message for msg in storage if msg.level_tag == 'error']
    )
    return render(request, "data.html", context=context)


def webpage(request, docid=None):
    """ displays the page - the doc and its structure.
    """
    document = DataModel.inst_by_id(docid)
    if not isinstance(document, DataModel):
        return JsonResponse(dict(success=False, msg='No doc found.'))
    return JsonResponse(dict(document), encoder=rmxjson.RmxEncoder)


def data_to_corpus(request):

    # todo(): review this method.
    obj = QueryDict(request.body).dict()

    docid = obj.get('docid')
    path = obj.get('path')

    doc = DataModel.inst_by_id(docid)
    doc.data_to_corpus(path, id_as_head=True)
    _id = doc.purge_data()

    return JsonResponse(dict(success=True, docid=str(_id)))


def text(request, docid: str = None):

    doc = DataModel.inst_by_id(docid)

    txt = ''

    # todo(): implement in order to replace the same endpoint on the level of
    # the corpus
    return HttpResponse('')


def create_from_txt(request):
    """Creating a corpus from uploaded text files. """
    pass


@csrf_exempt
def edit_many(request):

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
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
