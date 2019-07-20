
from ..app import celery
from ..tasks.celeryconf import NLP_TASKS


def get_available_features(corpusid, corpus_path):
    """Retrieves available features from nlp"""

    result = celery.send_task(
        NLP_TASKS['available_features'],
        kwargs={'corpusid': corpusid, 'path': corpus_path}).get()
    return result


