import hashlib
import os
from typing import List

from ..apps.data.models import DataModel
from ..apps.corpus.models import insert_urlobj
from ..app import celery


@celery.task
def call_data_create(**kwds):
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


@celery.task
def delete_data(dataids: List[str] = None, corpusid: str = None):

    response = DataModel.delete_many(dataids=dataids)
    del response
    # todo(): process response
    return corpusid


@celery.task
def create(corpusid: str = None,
           fileid: str = None,
           path: str = None,
           encoding: str = None,
           file_name: str = None,
           success: bool = False
           ):
    """ Creating a data object for a file that exists.

    :param corpusid:
    :param fileid:
    :param path:
    :param encoding:
    :param file_name:
    :return:
    """
    doc, fileid = DataModel.create_empty(
        corpusid=corpusid,
        title=file_name,
        fileid=fileid
    )
    hasher = hashlib.md5()

    with open(path, 'r') as _file:
        for line in _file.readlines():
            hasher.update(bytes(line, encoding=encoding))

    _hash = hasher.hexdigest()
    try:
        doc.set_hashtxt(value=_hash)
    except ValueError:
        doc.rm_doc()
        if os.path.exists(path):
            os.remove(path)
    return {
        'corpusid': corpusid,
        'data_id': str(doc.get_id()),
        'file_id': fileid,
        'file_name': file_name,
        'success': success,
    }
