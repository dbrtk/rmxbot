

import shlex
import subprocess

from ...config import SEARCH_CORPUS_SH
from .models import ContainerModel


# todo(): delete!

def words_context(lemma: list = None, corpus: ContainerModel = None,
                  corpusid: str = None):

    corpus = corpus if corpus else ContainerModel.inst_by_id(corpusid)
    path = corpus.texts_path()

    try:
        results = subprocess.run(
            shlex.split("sh {} {} {}".format(
                SEARCH_CORPUS_SH,
                path,
                '|'.join(lemma)
            )),
            encoding="utf-8",
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as err:
        # the command exits with a non-zero exit code.
        raise

    return results.stdout
