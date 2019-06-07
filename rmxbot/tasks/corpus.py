
import os
from typing import List

from ..apps.corpus.models import (CorpusModel, get_urls_length, insert_urlobj,
                                  set_crawl_ready)
from ..config import CORPUS_MAX_SIZE
from .data import delete_data
from ..tasks.celeryconf import NLP_TASKS, SCRASYNC_TASKS

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
        'feats': int(feats),
        'words': words,
        'docs_per_feat': int(docs_per_feat),
        'feats_per_doc': int(feats_per_doc),
        'path': corpus.get_corpus_path(),
    }
    if os.path.isfile(vectors_path):
        celery.send_task(NLP_TASKS['factorize_matrices'], kwargs=kwds)
        # compute_features_weights.delay(vectors_in_corpus, **kwds)
    else:
        celery.send_task(NLP_TASKS['compute_matrices'], kwargs=kwds)
        # compute_matrices.delay(**kwds)


@celery.task
def crawl_async(url_list: list = None, corpus_id=None, crawl=False,
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


@celery.task
def nlp_callback_success(**kwds):
    """Called when a nlp callback is sent to proximitybot.

       This task is called by the nlp container.
    """
    corpus = CorpusModel.inst_by_id(kwds.get('corpusid'))
    corpus.update_on_nlp_callback(feats=kwds.get('feats'))


@celery.task
def test_task(a: int = None, b: int = None) -> int:
    """This is a test task."""
    return a + b


@celery.task
def file_extract_callback(kwds: dict = None):
    """ Called after creating a data object from an uploaded file.

    :param kwds:
    :return:
    """
    corpusid = kwds.get('corpusid')
    data_id = kwds.get('data_id')
    file_id = kwds.get('file_id')
    file_name = kwds.get('file_name')
    success = kwds.get('success')
    texthash = kwds.get('texthash')
    if success and data_id:
        insert_urlobj(
            corpusid,
            {
                'data_id': data_id,
                'file_id': file_id,
                'texthash': texthash,
                'title': file_name,
            }
        )
    doc = CorpusModel.file_extract_callback(
        corpusid=corpusid, unique_file_id=file_id)

    if not doc['expected_files']:
        if doc.matrix_exists:
            integrity_check.delay(corpusid=corpusid)
        else:
            set_crawl_ready(corpusid, True)


@celery.task
def integrity_check(corpusid: str = None):

    celery.send_task(NLP_TASKS['integrity_check'], kwargs={
        'corpusid': corpusid,
        'path': CorpusModel.inst_by_id(corpusid).get_corpus_path(),
    })


@celery.task
def integrity_check_callback(corpusid: str = None):

    set_crawl_ready(corpusid, True)


@celery.task(bind=True)
def delete_data_from_corpus(
        self, corpusid: str = None, data_ids: List[str] = None):

    corpus = CorpusModel.inst_by_id(corpusid)

    corpus_files_path = corpus.corpus_files_path()
    dataid_fileid = corpus.dataid_fileid(data_ids=data_ids)

    corpus.del_data_objects(data_ids=data_ids)

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


@celery.task
def expected_files(corpusid: str = None, file_objects: list = None):
    """Updates the corpus with expected files that are processed."""
    CorpusModel.update_expected_files(
        corpusid=corpusid, file_objects=file_objects)

    corpus = CorpusModel.inst_by_id(corpusid)
    return {
        'corpusid': corpusid,
        # 'vectors_path': corpus.get_vectors_path(),
        'corpus_files_path': corpus.corpus_files_path(),
        # 'matrix_path': corpus.matrix_path,
        # 'wf_path': corpus.wf_path,
    }


@celery.task
def create_from_upload(name: str = None, file_objects: list = None):
    """Creating a corpus from file upload."""
    docid = str(CorpusModel.inst_new_doc(name=name))
    corpus = CorpusModel.inst_by_id(docid)
    corpus['expected_files'] = file_objects

    # todo(): set status to busy
    corpus.set_corpus_type(data_from_files=True)
    corpus.save()

    return {
        'corpusid': docid,
        # 'corpus_path': corpus.get_corpus_path(),
        'corpus_files_path': corpus.corpus_files_path()
    }




