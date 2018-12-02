

import os
import shutil
import tempfile

from ..config import DATA_ROOT


def zip_corpus(corpusid):

    tmp_dir = tempfile.mkdtemp()
    return shutil.make_archive(
        os.path.join(tmp_dir, corpusid),
        'zip',
        DATA_ROOT,
        base_dir=corpusid
    ), tmp_dir


def zip_vectors(corpusid, vectors_path):

    return shutil.make_archive(
        os.path.join(tempfile.mkdtemp(), corpusid),
        'zip',
        DATA_ROOT,
        base_dir=os.path.join(DATA_ROOT, vectors_path)
    )
