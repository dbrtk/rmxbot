
import json
import os
import shlex
import subprocess

from celery import shared_task
import requests

from ...config import (CORPUS_MAX_SIZE, NLP_COMPUTE_MATRICES,
                       NLP_GENERATE_FEATURES_WEIGTHS, SCRASYNC_CREATE)
from .models import CorpusModel, get_urls_length


class Error(Exception):
    pass


class __Error(Error):
    pass


# @shared_task(bind=True)
# def generate_matrices(self, corpus_id, features, words, documents):
#     """ Generating matrices. """
#
#     # todo(): delete - this isn't used
#     # todo(): review and delete!
#
#     corpus = CorpusModel.inst_by_id(corpus_id)
#     corpus.set_status_feats(busy=True, feats=features, task_name=self.name,
#                             task_id=self.request.id)
#     try:
#         features, docs = corpus.get_features(
#             feats=features,
#             words=words,
#             docs_per_feat=documents
#         )
#     except __Error as err:  # (IndexError, Exception, ) as err:
#         corpus.cleanup_on_error(featcount=features)
#     corpus.del_status_feats(feats=features)


@shared_task(bind=True)
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
    # todo(): review this method
    corpus = CorpusModel.inst_by_id(corpusid)
    corpus.set_status_feats(busy=True, feats=feats, task_name=self.name,
                            task_id=self.request.id)
    kwds = {
        'corpusid': corpusid,
        'feats': feats,
        'words': words,
        'path': corpus.get_corpus_path(),
        'docs_per_feat': docs_per_feat,
        'feats_per_doc': feats_per_doc
    }
    if os.path.isfile(vectors_path):
        compute_features_weights.delay(vectors_path, **kwds)
    else:
        compute_matrices.delay(**kwds)


@shared_task(bind=True)
def compute_matrices(self, **kwds):
    """ Calling compute matrice son the nlp server. """
    requests.post(NLP_COMPUTE_MATRICES, json=kwds)


@shared_task(bind=True)
def compute_features_weights(self, vectors_path, **kwds):

    # arr = numpy.load(vectors_path)
    # kwds.update({
    #     'dtype': arr.dtype.name,
    #     'shape': arr.shape
    # })

    requests.post(NLP_GENERATE_FEATURES_WEIGTHS, data={
        'payload': json.dumps(kwds)
    })  # , files={'file': arr.tobytes()})
    # del arr


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


# @shared_task(bind=True)
# def nlp_callback_success_old(self, **kwds):
#     """Called when features and weights are returned from the nlp server."""
#
#     # todo(): delete - this isn't used
#
#     corpusid = kwds.get('corpusid')
#     feats = kwds.get('feats')
#
#     corpus = CorpusModel.inst_by_id(corpusid)
#     tmp_path = kwds.get('tmp_path')
#
#     dest = os.path.join(corpus.get_corpus_path(), 'matrix', 'wf')
#     dest = os.path.join(dest, '%d' % feats)
#
#     os.makedirs(dest)
#     os.chmod(dest, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
#
#     command = 'tar -xf %s -C %s' % (tmp_path, dest)
#
#     subprocess.run(
#         shlex.split(command),
#         stdout=subprocess.PIPE,
#         stderr=subprocess.PIPE,
#         check=True
#     )
#
#     os.remove(tmp_path)
#     if os.path.isfile(tmp_path):
#         raise RuntimeError(tmp_path)
#     corpus.del_status_feats(feats=kwds.get('feats'))


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
