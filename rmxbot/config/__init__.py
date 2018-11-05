
import os

from django.conf import settings

HERE = os.path.abspath(__file__)

# PROXIMITY_BOT_PROJ is specific to the local deployment of proximity-bot.
PROXIMITY_BOT_PROJ = settings.PROJECT_DIR

SCRIPTS = os.path.abspath(os.path.join(
    HERE, os.pardir, os.pardir, os.pardir, 'bin'))
if not os.path.isdir(SCRIPTS):
    raise RuntimeError(SCRIPTS)

SEARCH_CORPUS_SH = os.path.join(SCRIPTS, 'search_corpus.sh')

DEFAULT_CRAWL_DEPTH = 2

NLP_REMOTE_WORKER = True

# NLP_ENDPOINT = 'http://nlp.proximity-bot.net'
NLP_ENDPOINT = 'http://localhost:8001'
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

# NLP_FEATURES_COUNT = '/'.join(
#     s.strip('/') for s in [NLP_ENDPOINT, 'nlp', 'features-count'])
# NLP_REMOVE_FEATURE = '/'.join(
#     s.strip('/') for s in [NLP_ENDPOINT, 'nlp', 'remove-feature'])


SCRASYNC_REMOTE_WORKER = True

# SCRASYNC_ENDPOINT = 'http://scrasync.proximity-bot.net'
SCRASYNC_ENDPOINT = 'http://localhost:8002'

SCRASYNC_CREATE = '/'.join(
    s for s in [SCRASYNC_ENDPOINT, 'scrasync', 'create'])
if not SCRASYNC_CREATE.endswith('/'):
    SCRASYNC_CREATE = '{}/'.format(SCRASYNC_CREATE)

SCRASYNC_CRAWL_READY = '/'.join(
    s for s in [SCRASYNC_ENDPOINT, 'scrasync', 'crawl-ready'])
if not SCRASYNC_CRAWL_READY.endswith('/'):
    SCRASYNC_CRAWL_READY = '{}/'.format(SCRASYNC_CRAWL_READY)

# configurations that are related to the corpus and its data storage
# DATA_ROOT = '/data'
DATA_ROOT = os.path.join(PROXIMITY_BOT_PROJ, 'data', 'rmxbot')

CORPUS_ROOT = os.path.normpath(DATA_ROOT)

CORPUS_MAX_SIZE = 400

# DATABASE configuration
# MONGODB
MONGODB_NAME = 'rmx'
# The location of the mongodb server.
# the hoset can be se to: '127.0.0.1'  # 'http://proximity-bot.net'
# in the case of a docker container (that runs mongodb), it will be:
# os.environ['DB_PORT_27017_TCP_ADDR']
MONGODB_LOCATION = os.environ['DB_PORT_27017_TCP_ADDR']  # 'proximitybot.com'
MONGODB_PORT = 27017
MONGODB_USR = 'dbuser_if_any'
MONGODB_PWD = 'password_if_any'

# names given to the mongodb collections
DATA_COLL = 'data'
IMAGE_COLL = 'image'
CORPUS_COLL = 'corpus'
CLUSTER_COLL = 'cluster'


