
# from ..config import BROKER_HOST_NAME, REDIS_PASS

from ..config import RPC_HOST, RPC_PASS, RPC_PORT, RPC_USER, RPC_VHOST
# imports related to the omngodb rpc backend
from ..config import (MONGODB_LOCATION, MONGODB_USER, MONGODB_PASS, 
                      RPC_DATABASE)

# broker_url = 'amqp://myuser:mypassword@localhost:5672/myvhost'
_url = f'amqp://{RPC_USER}:{RPC_PASS}@{RPC_HOST}:{RPC_PORT}/{RPC_VHOST}'

#_url = f'redis://:{REDIS_PASS}@{BROKER_HOST_NAME}:6379/0'

BROKER_URL = _url
# CELERY_RESULT_BACKEND = _url
CELERY_RESULT_BACKEND = 'mongodb://'
CELERY_MONGODB_BACKEND_SETTINGS = {
    'host': MONGODB_LOCATION,
    'user': MONGODB_USER,
    'password': MONGODB_PASS,
    'database_name': RPC_DATABASE
}

CELERY_RESULT_PERSISTENT = True

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

    'create_from_webpage': 'rmxbot.tasks.data.create_from_webpage',

    'create': 'rmxbot.tasks.data.create',


    'test_task': 'rmxbot.tasks.container.test_task',

    'generate_matrices_remote':
        'rmxbot.tasks.container.generate_matrices_remote',

    'crawl_async': 'rmxbot.tasks.container.crawl_async',

    'nlp_callback_success': 'rmxbot.tasks.container.nlp_callback_success',

    'file_extract_callback': 'rmxbot.tasks.container.file_extract_callback',

    'integrity_check': 'rmxbot.tasks.container.integrity_check',

    'integrity_check_callback':
        'rmxbot.tasks.container.integrity_check_callback',

    'delete_data_from_container':
        'rmxbot.tasks.container.delete_data_from_container',

    'expected_files': 'rmxbot.tasks.container.expected_files',

    'create_from_upload': 'rmxbot.tasks.container.create_from_upload',

    'process_crawl_resp': 'rmxbot.tasks.container.process_crawl_resp',

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
