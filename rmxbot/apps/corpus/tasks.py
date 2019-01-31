
import json
import os
import shlex
import shutil
import subprocess

from celery import shared_task
import requests

from ...config import (CORPUS_MAX_SIZE, NLP_COMPUTE_MATRICES,
                       NLP_GENERATE_FEATURES_WEIGTHS, SCRASYNC_CREATE)
from .models import CorpusModel, DataObject, get_urls_length, insert_urlobj
from . import sync_data


class Error(Exception):
    pass


class __Error(Error):
    pass


# todo(): cleanup!!!


@shared_task(bind=True)
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


@shared_task(bind=True)
def compute_matrices(self, **kwds):
    """ Calling compute matrice son the nlp server. """

    path_to_zip, tmp_dir = sync_data.zip_corpus(kwds.get('corpusid'))

    requests.post(NLP_COMPUTE_MATRICES,
                  data={'params': json.dumps(kwds)},
                  files={'file': open(path_to_zip, 'rb')})
    shutil.rmtree(tmp_dir)


@shared_task(bind=True)
def compute_features_weights(self, vectors_in_corpus, **kwds):

    path_to_zip, tmp_dir = sync_data.zip_vectors(
        kwds.get('corpusid'), vectors_in_corpus)

    requests.post(NLP_GENERATE_FEATURES_WEIGTHS, data={
        'payload': json.dumps(kwds)
    }, files={'file': open(path_to_zip, 'rb')})
    shutil.rmtree(tmp_dir)


@shared_task(bind=True)
def crawl_async(self, url_list: list = None, corpus_id=None, crawl=False,
                depth=1, corpus_file_path: str = None):

    if get_urls_length(corpus_id) >= CORPUS_MAX_SIZE:
        return False
    corpus = CorpusModel.inst_by_id(corpus_id)
    path, file_id = corpus.create_file_path()
    requests.post(SCRASYNC_CREATE, json={
        'endpoint': url_list,
        'corpusid': corpus_id,
        'depth': depth,
        'corpus_file_path': corpus_file_path
    })


@shared_task(bind=True)
def nlp_callback_success(self, **kwds):
    """Caled when a nlp callback is sent to proximitybot."""
    corpus = CorpusModel.inst_by_id(kwds.get('corpusid'))
    corpus.update_on_nlp_callback(feats=kwds.get('feats'))


def empty_corpus(path):
    path = os.path.normpath(path)
    command = shlex.split('/opt/bin/rmxrsync.sh {}'.format(path))
    try:
        subprocess.call(command)
    except (subprocess.CalledProcessError,) as err:
        raise RuntimeError(err)


@shared_task(bind=True)
def test_task(self, a, b):
    """This is a test task."""
    return a + b


@shared_task(bind=True)
def file_extract_callback(self, **kwds):

    insert_urlobj(
        kwds.get('corpusid'),
        {
            'data_id': kwds.get('data_id'),
            'file_id': kwds.get('file_id'),
            'texthash': '',
            'title': kwds.get('file_name')
        })
    CorpusModel.file_extract_callback(
        corpusid=kwds.get('corpusid'), unique_file_id=kwds.get('unique_id'))
