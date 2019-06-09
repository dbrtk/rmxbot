import hashlib
import os
from typing import List

from ..apps.data.models import DataModel
from ..apps.corpus.models import insert_urlobj
from ..app import celery


@celery.task
def create_from_webpage(corpusid: str = None,
                        endpoint: str = None,
                        title: str = None,
                        texthash: str = None,
                        data: str = None,
                        links: list = None):
    """ Task called within DataModel.create."""
    doc, fileid = DataModel.create(
        data=data,
        corpus_id=corpusid,
        links=links,
        title=title,
        endpoint=endpoint
    )
    if isinstance(doc, DataModel) and fileid:
        insert_urlobj(
            corpusid,
            {
                'data_id': str(doc.get('_id')),
                'url': endpoint,
                'texthash': texthash or doc.get('hashtxt'),
                'file_id': fileid,
                'title': doc.get('title') or doc.get('url')
            })
        return str(doc.get_id()), fileid
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
           success: bool = False,
           hashtxt: str = None,
           ):
    """ Creating a data object for a file that exists. This is used when
        uploading files.

    :param corpusid:
    :param fileid:
    :param path:
    :param encoding:
    :param file_name:
    :param success:
    :param hashtxt:
    :return:
    """
    doc, fileid = DataModel.create_empty(
        corpusid=corpusid,
        title=file_name,
        fileid=fileid
    )
    if not hashtxt:
        hasher = hashlib.md5()
        with open(path, 'r') as _file:
            for line in _file.readlines():
                hasher.update(bytes(line, encoding=encoding))

        hashtxt = hasher.hexdigest()
    out = {
        'corpusid': corpusid,
        'data_id': str(doc.get_id()),
        'file_id': fileid,
        'file_name': file_name,
        'success': success,
    }
    try:
        doc.set_hashtxt(value=hashtxt)
        out['texthash'] = hashtxt
    except ValueError:
        doc.rm_doc()
        if os.path.exists(path):
            os.remove(path)
        out['success'] = False
    else:
        doc.prepend_id_file(corpusid=corpusid)
    return out
