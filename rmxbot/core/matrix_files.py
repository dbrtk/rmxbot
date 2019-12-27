
from ..app import celery
from ..tasks.celeryconf import NLP_TASKS


def get_available_features(containerid, folder_path):
    """Retrieves available features from nlp"""

    result = celery.send_task(
        NLP_TASKS['available_features'],
        kwargs={'corpusid': containerid, 'path': folder_path}).get()
    return result


