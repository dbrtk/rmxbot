

from ..config import RPC_HOST, RPC_PASS, RPC_PORT, RPC_USER, RPC_VHOST

# redis config imports
from ..config import BROKER_HOST_NAME, REDIS_DB_NUMBER, REDIS_PASS, REDIS_PORT


# broker_url = 'amqp://myuser:mypassword@localhost:5672/myvhost'
_url = f'amqp://{RPC_USER}:{RPC_PASS}@{RPC_HOST}:{RPC_PORT}/{RPC_VHOST}'

broker_url = _url

# result_backend = 'rpc://'

# redis result backend
result_backend = f'redis://:{REDIS_PASS}@{BROKER_HOST_NAME}:{REDIS_PORT}/{REDIS_DB_NUMBER}'

result_persistent = True

imports = ('rmxbot.tasks.container', 'rmxbot.tasks.data')

result_expires = 30
timezone = 'UTC'

accept_content = ['json', 'msgpack', 'yaml']
task_serializer = 'json'
result_serializer = 'json'

task_routes = {

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

    'monitor_crawl': 'rmxbot.tasks.container.monitor_crawl',

}

SCRASYNC_TASKS = {

    'create':  'scrasync.scraper.start_crawl',

    'crawl_ready': 'scrasync.tasks.crawl_ready',
    
    # todo(): delete after devel
    'test_monitor': 'scrasync.tasks.test_monitor',

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
