
import json
import os
import shutil
from typing import List

import requests

from ..apps.corpus.models import (CorpusModel, get_urls_length, insert_urlobj,
                                  set_crawl_ready)
from ..apps.corpus import sync_data
from ..config import (CORPUS_MAX_SIZE, NLP_COMPUTE_MATRICES,
                      NLP_GENERATE_FEATURES_WEIGTHS, NLP_INTEGRITY_CHECK)
from .data import delete_data
from ..tasks.celeryconf import SCRASYNC_TASKS

from ..app import celery


class Error(Exception):
    pass


class __Error(Error):
    pass


@celery.task(bind=True)
def generate_matrices_remote(
        self,
        corpusid: str = None,
        feats: int = 10,
        words: int = 6,
        vectors_path: str = None,
        vectors_in_corpus: str = None,
        docs_per_feat: int = 0,
        feats_per_doc: int = 3):
    """ Generating matrices on the remote server. This is used when nlp lives
        on its own machine.
    """
    corpus = CorpusModel.inst_by_id(corpusid)
    corpus.set_status_feats(busy=True, feats=feats, task_name=self.name,
                            task_id=self.request.id)
    kwds = {
        'corpusid': corpusid,
        'feats': feats,
        'words': words,

        # todo(): remove path!
        # 'path': corpus.get_corpus_path(),

        'docs_per_feat': docs_per_feat,
        'feats_per_doc': feats_per_doc
    }
    if os.path.isfile(vectors_path):
        compute_features_weights.delay(vectors_in_corpus, **kwds)
    else:
        compute_matrices.delay(**kwds)


@celery.task
def compute_matrices(**kwds):
    """ Calling compute matrice son the nlp server. """

    path_to_zip, tmp_dir = sync_data.zip_corpus(kwds.get('corpusid'))

    requests.post(NLP_COMPUTE_MATRICES,
                  data={'params': json.dumps(kwds)},
                  files={'file': open(path_to_zip, 'rb')})
    shutil.rmtree(tmp_dir)


@celery.task(bind=True)
def compute_features_weights(self, vectors_in_corpus, **kwds):

    path_to_zip, tmp_dir = sync_data.zip_vectors(
        kwds.get('corpusid'), vectors_in_corpus)

    requests.post(NLP_GENERATE_FEATURES_WEIGTHS, data={
        'payload': json.dumps(kwds)
    }, files={'file': open(path_to_zip, 'rb')})
    shutil.rmtree(tmp_dir)


@celery.task(bind=True)
def crawl_async(self, url_list: list = None, corpus_id=None, crawl=False,
                depth=1, corpus_file_path: str = None):

    if get_urls_length(corpus_id) >= CORPUS_MAX_SIZE:
        return False
    corpus = CorpusModel.inst_by_id(corpus_id)
    path, file_id = corpus.create_file_path()

    celery.send_task(SCRASYNC_TASKS['create'], kwargs={
        'endpoint': url_list,
        'corpusid': corpus_id,
        'depth': depth,
        'corpus_file_path': corpus_file_path,
    })

    # todo(): delete
    # requests.post(SCRASYNC_CREATE, json={
    #     'endpoint': url_list,
    #     'corpusid': corpus_id,
    #     'depth': depth,
    #     'corpus_file_path': corpus_file_path
    # })


@celery.task(bind=True)
def nlp_callback_success(self, **kwds):
    """Caled when a nlp callback is sent to proximitybot."""
    corpus = CorpusModel.inst_by_id(kwds.get('corpusid'))
    corpus.update_on_nlp_callback(feats=kwds.get('feats'))


@celery.task(bind=True)
def test_task(self, a: int = None, b: int = None) -> int:
    """This is a test task."""
    return a + b


@celery.task(bind=True)
def file_extract_callback(self, **kwds):
    """

    :param self:
    :param kwds:
    :return:
    """
    corpusid = kwds.get('corpusid')
    if kwds.get('success') and kwds.get('data_id'):
        insert_urlobj(
            kwds.get('corpusid'),
            {
                'data_id': kwds.get('data_id'),
                'file_id': kwds.get('file_id'),
                'texthash': '',
                'title': kwds.get('file_name')
            }
        )
    doc = CorpusModel.file_extract_callback(
        corpusid=corpusid, unique_file_id=kwds.get('unique_id'))

    if not doc['expected_files']:
        if doc.matrix_exists:
            integrity_check.delay(corpusid=corpusid)
        else:
            set_crawl_ready(corpusid, True)


@celery.task(bind=True)
def integrity_check(self, corpusid: str = None):

    # if not CorpusModel.inst_by_id(corpusid).matrix_exists:
    #     return
    path_to_zip, tmp_dir = sync_data.zip_corpus(corpusid)

    requests.post(NLP_INTEGRITY_CHECK, data={
        'payload': json.dumps({'corpusid': corpusid})
    }, files={'file': open(path_to_zip, 'rb')})

    shutil.rmtree(tmp_dir)


@celery.task(bind=True)
def delete_data_from_corpus(
        self, corpusid: str = None, data_ids: List[str] = None):

    corpus = CorpusModel.inst_by_id(corpusid)

    corpus_files_path = corpus.corpus_files_path()
    dataid_fileid = corpus.dataid_fileid(data_ids=data_ids)
    resp = corpus.del_data_objects(data_ids=data_ids)

    for _path in [os.path.join(corpus_files_path, _[1])
                  for _ in dataid_fileid]:
        if not os.path.exists(_path):
            raise RuntimeError(_path)
        os.remove(_path)

    params = {
        'kwargs': {'corpusid': corpusid, 'dataids': data_ids}
    }
    if corpus.matrix_exists:
        params['link'] = integrity_check.s()

    delete_data.apply_async(**params)
