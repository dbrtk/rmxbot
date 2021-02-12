
import os


HERE = os.path.abspath(__file__)

BASE_DIR = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir, os.pardir))

SCRIPTS = os.path.join(BASE_DIR, 'bin')

TEMPLATES = os.environ['TEMPLATES_FOLDER']

DEFAULT_CRAWL_DEPTH = 2


# Configurations that are related to the corpus and its data storage
# DATA_ROOT is the path to the directory that will store corpora and data
# generated by rmxbot
DATA_ROOT = os.environ.get('DATA_ROOT')

# the tmp directory used by rmxbot when processing files, etc...
# TMP_DATA_DIR = '/data/tmp'
TMP_DATA_DIR = os.environ.get('TMP_DATA_DIR')

EXTRACTXT_ENDPOINT = os.environ.get('EXTRACTXT_ENDPOINT')

EXTRACTXT_FILES_UPLOAD_URL = '{}/upload-files'.format(EXTRACTXT_ENDPOINT)

# The path to the directory where corpora along with matrices are stored.
CORPUS_ROOT = os.path.join(DATA_ROOT, 'container')
TEXT_FOLDER = 'text'
MATRIX_FOLDER = 'matrix'

CORPUS_MAX_SIZE = 500

# DATABASE configuration - MONGODB

MONGODB_LOCATION = os.environ.get('MONGODB_LOCATION')
MONGODB_NAME = os.environ.get('DATABASE_NAME')
MONGO_PORT = os.environ.get('MONGO_PORT')
MONGODB_USER = os.environ.get('DATABASE_USERNAME')
MONGODB_PASS = os.environ.get('DATABASE_PASSWORD')

# names given to the mongodb collections
DATA_COLL = 'data'
IMAGE_COLL = 'image'
CORPUS_COLL = 'corpus'
CLUSTER_COLL = 'cluster'


# monitor the crawl every 5 seconds
CRAWL_MONITOR_COUNTDOWN = 5
# wait 10 s before starting to monitor
CRAWL_START_MONITOR_COUNTDOWN = 10

CRAWL_MONITOR_MAX_ITER = 150

REQUEST_MAX_RETRIES = 5
# time to wait in seconds after the last call made inside the crawler.
# after that the container is set as ready
SECONDS_AFTER_LAST_CALL = 30

# REDIS CONFIG
# celery, redis (auth access) configuration
BROKER_HOST_NAME = os.environ.get('BROKER_HOST_NAME')
REDIS_PASS = os.environ.get('REDIS_PASS')
REDIS_DB_NUMBER = os.environ.get('REDIS_DB_NUMBER')
REDIS_PORT = os.environ.get('REDIS_PORT')

# RabbitMQ configuration
# rabbitmq rpc queue name
RPC_QUEUE_NAME = os.environ.get('RPC_QUEUE_NAME', 'rmxbot')
RPC_PUBLISH_QUEUES = {
    'nlp': 'nlp',
    'scrasync': 'scrasync',
    'rmxgrep': 'rmxgrep',
    'extractxt': 'extractxt'
}
# RabbitMQ login credentials
RPC_PASS = os.environ.get('RABBITMQ_DEFAULT_PASS')
RPC_USER = os.environ.get('RABBITMQ_DEFAULT_USER')
RPC_VHOST = os.environ.get('RABBITMQ_DEFAULT_VHOST')

# the host to which the rpc broker (rabbitmq) is deployed
RPC_HOST = os.environ.get('RABBITMQ_HOST')
RPC_PORT = os.environ.get('RABBITMQ_PORT', 5672)


# configurations for prometheus
PROMETHEUS_HOST = os.environ.get('PROMETHEUS_HOST')
PROMETHEUS_PORT = os.environ.get('PROMETHEUS_PORT')
PROMETHEUS_URL = f'{PROMETHEUS_HOST}:{PROMETHEUS_PORT}/api/v1'
