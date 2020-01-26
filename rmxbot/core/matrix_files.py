import os

from ..app import celery
from ..tasks.celeryconf import NLP_TASKS


def get_available_features(containerid, folder_path):
    """Retrieves available features from nlp"""
    result = celery.send_task(
        NLP_TASKS['available_features'],
        kwargs={'corpusid': containerid, 'path': folder_path}).get()
    return result


def get_available_features_local(containerid: str, folder_path: str):
    """

    :param containerid:
    :param folder_path:
    :return:
    """
    if not folder_path.endswith(containerid):
        raise ValueError(f'{containerid} - {folder_path}')
    path = os.path.join(folder_path, 'matrix', 'wf')
    if not os.path.isdir(path):
        return []
    dirs = os.listdir(path)
    out = []
    for _ in dirs:
        featcount = int(_)
        # todo(): delete the snippet below
        # if not int(_) == numpy.shape(self.feat)[1]:
        #     raise RuntimeError(numpy.shape(self.feat))
        _path = os.path.join(path, _)
        out.append(dict(
            featcount=featcount,
            path=_path,
            feat=os.path.join(_path, 'feat.npy'),
            weights=os.path.join(_path, 'weights.npy')
        ))
    return out

