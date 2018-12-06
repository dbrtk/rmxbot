
import os


HERE = os.path.abspath(__file__)

SCRIPTS = os.path.abspath(os.path.join(
    HERE, os.pardir, os.pardir, os.pardir, 'bin'))
if not os.path.isdir(SCRIPTS):
    raise RuntimeError(SCRIPTS)

# SEARCH_CORPUS_SH - the grep script that searches the corpus
SEARCH_CORPUS_SH = os.environ['RMX_SEARCH_CORPUS_SCRIPT']

print(SEARCH_CORPUS_SH)

DEFAULT_CRAWL_DEPTH = 2

NLP_REMOTE_WORKER = True

# the endpoint of the server that runs nlp.
# NLP_ENDPOINT = 'http://nlp.proximity-bot.net'
NLP_ENDPOINT = os.environ['NLP_ENDPOINT']

print('nlp endpoint: %r' % NLP_ENDPOINT)

NLP_DENDOGRAM = '/'.join(
    s for s in [NLP_ENDPOINT, 'nlp', 'dendogram'])

NLP_GENERATE_MATRICES = '/'.join(
    s for s in [NLP_ENDPOINT, 'nlp', 'generate-matrices'])

NLP_GENERATE_FEATURES_WEIGTHS = '/'.join(
    s for s in [NLP_ENDPOINT, 'nlp', 'generate-features-weights'])
NLP_COMPUTE_MATRICES = '/'.join(
    s for s in [NLP_ENDPOINT, 'nlp', 'compute-matrices'])

NLP_GENERATE_ALL = '/'.join(
    s for s in [NLP_ENDPOINT, 'nlp', 'generate-all'])

NLP_FEATURES_AND_DOCS_ENDPOINT = '/'.join(
    s for s in [NLP_ENDPOINT, 'nlp', 'features-docs'])

SCRASYNC_REMOTE_WORKER = True

# SCRASYNC_ENDPOINT = 'http://scrasync.proximity-bot.net'
SCRASYNC_ENDPOINT = os.environ.get('SCRASYNC_ENDPOINT')

SCRASYNC_CREATE = '/'.join(
    s for s in [SCRASYNC_ENDPOINT, 'scrasync', 'create'])
if not SCRASYNC_CREATE.endswith('/'):
    SCRASYNC_CREATE = '{}/'.format(SCRASYNC_CREATE)

SCRASYNC_CRAWL_READY = '/'.join(
    s for s in [SCRASYNC_ENDPOINT, 'scrasync', 'crawl-ready'])
if not SCRASYNC_CRAWL_READY.endswith('/'):
    SCRASYNC_CRAWL_READY = '{}/'.format(SCRASYNC_CRAWL_READY)

# Configurations that are related to the corpus and its data storage
# DATA_ROOT is the path to the directory that will store corpora and data
# generated by rmxbot
DATA_ROOT = os.environ.get('DATA_ROOT')

# the tmp directory used by rmxbot when processing files, etc...
# TMP_DATA_DIR = '/data/tmp'
TMP_DATA_DIR = os.environ.get('TMP_DATA_DIR')

# The path to the directory where corpora along with matrices are stored.
CORPUS_ROOT = os.path.join(DATA_ROOT, 'corpus')

CORPUS_MAX_SIZE = 400

# DATABASE configuration - MONGODB
MONGODB_NAME = 'rmx'
# MONGODB_LOCATION = '127.0.0.1'

MONGODB_LOCATION = os.environ.get('MONGODB_LOCATION')
MONGODB_PORT = 27017
MONGODB_USR = 'dbuser_if_any'
MONGODB_PWD = 'password_if_any'

# names given to the mongodb collections
DATA_COLL = 'data'
IMAGE_COLL = 'image'
CORPUS_COLL = 'corpus'
CLUSTER_COLL = 'cluster'
