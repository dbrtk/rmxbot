
import os


HERE = os.path.abspath(__file__)

BASE_DIR = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir, os.pardir))

SCRIPTS = os.path.join(BASE_DIR, 'bin')

TEMPLATES = os.environ['TEMPLATES_FOLDER']

REDIS_HOST_NAME = os.environ.get('REDIS_HOST_NAME')

# SEARCH_CORPUS_SH - the grep script that searches the corpus
SEARCH_CORPUS_SH = os.environ['RMX_SEARCH_CORPUS_SCRIPT']

DEFAULT_CRAWL_DEPTH = 2


# Configurations that are related to the corpus and its data storage
# DATA_ROOT is the path to the directory that will store corpora and data
# generated by rmxbot
DATA_ROOT = os.environ.get('DATA_ROOT')

# todo(): delete
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

# the tmp directory used by rmxbot when processing files, etc...
# TMP_DATA_DIR = '/data/tmp'
TMP_DATA_DIR = os.environ.get('TMP_DATA_DIR')

EXTRACTXT_ENDPOINT = os.environ.get('EXTRACTXT_ENDPOINT')

EXTRACTXT_FILES_UPLOAD_URL = '{}/upload-files'.format(EXTRACTXT_ENDPOINT)

# The path to the directory where corpora along with matrices are stored.
CORPUS_ROOT = os.path.join(DATA_ROOT, 'corpus')

CORPUS_MAX_SIZE = 400

# DATABASE configuration - MONGODB
MONGODB_NAME = os.environ.get('MONGODB_NAME')
# MONGODB_LOCATION = '127.0.0.1'

MONGODB_LOCATION = os.environ.get('MONGODB_LOCATION')
MONGODB_PORT = 27017
# MONGODB_USER = os.environ.get('MONGODB_USER')
# MONGODB_PASS = os.environ.get('MONGODB_PASS')

# names given to the mongodb collections
DATA_COLL = 'data'
IMAGE_COLL = 'image'
CORPUS_COLL = 'corpus'
CLUSTER_COLL = 'cluster'


CRAWL_MONITOR_COUNTDOWN = 3

CRAWL_MONITOR_MAX_ITER = 150

RMXGREP_ENDPOINT = os.environ.get('RMXGREP_ENDPOINT')
REQUEST_MAX_RETRIES = 5
