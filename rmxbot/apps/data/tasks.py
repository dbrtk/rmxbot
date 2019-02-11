from typing import List

import bson
from celery import shared_task

from .models import DataModel
from ..corpus.models import insert_urlobj


@shared_task(bind=True)
def call_data_create(self, **kwds):
    """ Task called within DataModel.create.
    expected kwds:
    {
        'links': list,
        'corpus_file_path': /corpus/file/path,
        'data': list[str],
        'endpoint': endpoint,
        'corpus_id': str
    }
    """
    doc, file_id = DataModel.create(**kwds)
    if isinstance(doc, DataModel) and file_id:
        insert_urlobj(
            kwds.get('corpus_id'),
            {
                'data_id': str(doc.get('_id')),
                'url': doc.get('url'),
                'texthash': doc.get('hashtxt'),
                'file_id': file_id,
                'title': doc.get('title') or doc.get('url')
            })
        return str(doc.get_id()), file_id
    return None, None


@shared_task(bind=True)
def delete_data(self, dataids: List[str] = None, corpusid: str = None):

    response = DataModel.delete_many(dataids=dataids)
    del response
    # todo(): process response
    return corpusid
