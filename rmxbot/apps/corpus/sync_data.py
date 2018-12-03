

import os
import shutil
import tempfile

from ...config import DATA_ROOT


def zip_corpus(corpusid):
    """Creating a zip file that contains the corpus."""
    tmp_dir = tempfile.mkdtemp()
    return shutil.make_archive(
        os.path.join(tmp_dir, corpusid),
        'zip',
        DATA_ROOT,
        base_dir=corpusid
    ), tmp_dir


def zip_vectors(corpusid, vectors_path):
    """Creating a zip file that contains the vectors.npy file."""
    tmp_dir = tempfile.mkdtemp()
    return shutil.make_archive(
        os.path.join(tmp_dir, corpusid),
        'zip',
        DATA_ROOT,
        base_dir=vectors_path
    ), tmp_dir
