
from ..config import BROKER_HOST_NAME

BROKER_URL = 'redis://{}:6379/0'.format(BROKER_HOST_NAME)
CELERY_RESULT_BACKEND = 'redis://{}:6379/0'.format(BROKER_HOST_NAME)

# BROKER_URL = f"amqp://rmxuser:rmxpass@{BROKER_HOST_NAME}:5672/rmxvhost"
# CELERY_RESULT_BACKEND = 'rpc://'

CELERY_IMPORTS = ('rmxbot.tasks.container', 'rmxbot.tasks.data')

CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_ROUTES = {

    'rmxbot.tasks.*': {'queue': 'rmxbot'},

    'scrasync.*': {'queue': 'scrasync'},

    'nlp.*': {'queue': 'nlp'},

}

SCRASYNC_TASKS = {

    'create':  'scrasync.scraper.start_crawl',

    'crawl_ready': 'scrasync.tasks.crawl_ready',

}

NLP_TASKS = {

    'compute_matrices': 'nlp.task.compute_matrices',

    'factorize_matrices': 'nlp.task.factorize_matrices',

    'integrity_check': 'nlp.task.integrity_check',

    'available_features': 'nlp.task.available_features',

    'features_and_docs': 'nlp.task.get_features_and_docs',

}
