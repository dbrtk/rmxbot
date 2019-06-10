

import shlex
import subprocess

from ...config import SEARCH_CORPUS_SH
from .models import CorpusModel


def words_context(lemma: list = None, corpus: CorpusModel = None,
                  corpusid: str = None):

    corpus = corpus if corpus else CorpusModel.inst_by_id(corpusid)
    path = corpus.corpus_files_path()

    try:
        results = subprocess.run(
            shlex.split("sh {} {} {}".format(
                SEARCH_CORPUS_SH,
                path,
                '|'.join(lemma)
            )),
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            encoding="utf-8",
            # this works in python3.7
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as err:
        # the command exits with a non-zero exit code.
        raise

    return results.stdout
