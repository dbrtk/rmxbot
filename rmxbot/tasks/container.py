
import os
from typing import List

from ..apps.container.models import (
    ContainerModel, container_status, insert_urlobj,
    integrity_check_ready,
    set_integrity_check_in_progress,
    set_crawl_ready)
from ..config import CRAWL_MONITOR_COUNTDOWN, CRAWL_MONITOR_MAX_ITER
from .data import delete_data
from ..tasks.celeryconf import NLP_TASKS, SCRASYNC_TASKS, RMXBOT_TASKS

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
    corpus = ContainerModel.inst_by_id(corpusid)
    corpus.set_status_feats(busy=True, feats=feats, task_name=self.name,
                            task_id=self.request.id)
    kwds = {
        'corpusid': corpusid,
        'feats': int(feats),
        'words': words,
        'docs_per_feat': int(docs_per_feat),
        'feats_per_doc': int(feats_per_doc),
        'path': corpus.get_folder_path(),
    }
    if os.path.isfile(vectors_path):
        celery.send_task(NLP_TASKS['factorize_matrices'], kwargs=kwds)
    else:
        celery.send_task(NLP_TASKS['compute_matrices'], kwargs=kwds)


@celery.task
def crawl_async(url_list: list = None, corpus_id=None, depth=1):
    """Starting the crawler in scrasync. Starting the task that will monitor
       the crawler.
    """
    celery.send_task(SCRASYNC_TASKS['create'], kwargs={
        'endpoint': url_list,
        'corpusid': corpus_id,
        'depth': depth
    })
    celery.send_task(
        RMXBOT_TASKS['monitor_crawl'],
        kwargs={
            'corpusid': corpus_id
        },
        countdown=CRAWL_MONITOR_COUNTDOWN
    )

    # monitor_crawl.apply_async((corpus_id,), countdown=CRAWL_MONITOR_COUNTDOWN)


@celery.task
def nlp_callback_success(**kwds):
    """Called when a nlp callback is sent to proximitybot.

       This task is called by the nlp container.
    """
    corpus = ContainerModel.inst_by_id(kwds.get('corpusid'))
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
    doc = ContainerModel.file_extract_callback(
        containerid=corpusid, unique_file_id=file_id)

    if not doc['expected_files']:
        if doc.matrix_exists:

            celery.send_task(
                RMXBOT_TASKS['integrity_check'],
                kwargs={
                    'corpusid': corpusid
                }
            )

            # integrity_check.delay(corpusid=corpusid)
        else:
            set_crawl_ready(corpusid, True)


@celery.task
def integrity_check(corpusid: str = None):

    set_integrity_check_in_progress(corpusid, True)

    celery.send_task(NLP_TASKS['integrity_check'], kwargs={
        'corpusid': corpusid,
        'path': ContainerModel.inst_by_id(corpusid).get_folder_path(),
    })


@celery.task
def integrity_check_callback(corpusid: str = None):

    integrity_check_ready(corpusid)


@celery.task(bind=True)
def delete_data_from_container(
        self, corpusid: str = None, data_ids: List[str] = None):

    corpus = ContainerModel.inst_by_id(corpusid)

    corpus_files_path = corpus.texts_path()
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

    celery.send_task(
        RMXBOT_TASKS['delete_data'],
        **params
    )

    # delete_data.apply_async(**params)


@celery.task
def expected_files(corpusid: str = None, file_objects: list = None):
    """Updates the container with expected files that are processed."""
    ContainerModel.update_expected_files(
        containerid=corpusid, file_objects=file_objects)

    corpus = ContainerModel.inst_by_id(corpusid)
    return {
        'corpusid': corpusid,
        # 'vectors_path': corpus.get_vectors_path(),
        'corpus_files_path': corpus.texts_path(),
        # 'matrix_path': corpus.matrix_path,
        # 'wf_path': corpus.wf_path,
    }


@celery.task
def create_from_upload(name: str = None, file_objects: list = None):
    """Creating a container from file upload."""
    docid = str(ContainerModel.inst_new_doc(name=name))
    corpus = ContainerModel.inst_by_id(docid)
    corpus['expected_files'] = file_objects
    corpus['data_from_files'] = True

    # todo(): set status to busy
    corpus.save()

    return {
        'corpusid': docid,
        # 'corpus_path': corpus.get_corpus_path(),
        'corpus_files_path': corpus.texts_path()
    }


@celery.task
def process_crawl_resp(resp, corpusid, iter: int = 0):
    """
    Processing the crawl response.
    :param resp:
    :param corpusid:
    :param iter:
    :return:
    """
    crawl_status = container_status(corpusid)
    if resp.get('ready'):

        if not crawl_status['integrity_check_in_progress']:

            celery.send_task(
                RMXBOT_TASKS['integrity_check'],
                kwargs={'corpusid': corpusid}
            )

            # integrity_check.delay(corpusid)
    else:
        if iter < CRAWL_MONITOR_MAX_ITER:
            celery.send_task(
                RMXBOT_TASKS['monitor_crawl'],
                args=[corpusid],
                kwargs={'iter': iter},
                countdown=CRAWL_MONITOR_COUNTDOWN
            )
            # monitor_crawl.apply_async(
            #     (corpusid, ),
            #     {'iter': iter},
            #     countdown=CRAWL_MONITOR_COUNTDOWN)


@celery.task
def monitor_crawl(corpusid, iter: int = 0):
    """This task takes care of the crawl callback.

       The first parameter is empty becasue it is called as a linked task
       receiving a list of endpoints from the scrapper.
    """
    iter += 1

    celery.send_task(
        SCRASYNC_TASKS['crawl_ready'],
        kwargs={'corpusid': corpusid},
        link=process_crawl_resp.s(corpusid, iter)
    )
