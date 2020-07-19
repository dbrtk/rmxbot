
from ..config import BROKER_HOST_NAME

BROKER_URL = 'redis://{}:6379/0'.format(BROKER_HOST_NAME)
CELERY_RESULT_BACKEND = 'redis://{}:6379/0'.format(BROKER_HOST_NAME)

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

    'rmxgrep.*': {'queue': 'rmxgrep'},

    'rmxcluster.*': {'queue': 'rmxcluster'},

}

RMXBOT_TASKS = {

    'delete_data': 'rmxbot.tasks.data.delete_data',

    'delete_data_from_container': 'rmxbot.tasks.container.delete_data_from_container',

    'monitor_crawl': 'rmxbot.tasks.container.monitor_crawl'
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

    'kmeans_cluster': 'nlp.task.kmeans_cluster',

    'kmeans_files': 'nlp.task.kmeans_files',

}

RMXGREP_TASK = {

    'search_text': 'rmxgrep.task.search_text'
}

RMXCLUSTER_TASKS = {

    'kmeans_groups': 'rmxcluster.task.kmeans_groups'
}
