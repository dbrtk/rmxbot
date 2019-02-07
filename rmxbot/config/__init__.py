
import os
import stat

from django.conf import settings

HERE = os.path.abspath(__file__)

# PROXIMITY_BOT_PROJ is specific to the local deployment of proximity-bot.
# this is a configuration used when rmxbot is ran locally. Delete in
# production!
PROXIMITY_BOT_PROJ = settings.PROJECT_DIR

SCRIPTS = os.path.abspath(os.path.join(
    HERE, os.pardir, os.pardir, os.pardir, 'bin'))
if not os.path.isdir(SCRIPTS):
    raise RuntimeError(SCRIPTS)

SEARCH_CORPUS_SH = os.path.join(SCRIPTS, 'search_corpus.sh')
os.chmod(SEARCH_CORPUS_SH, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)


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

EXTRACTXT_ENDPOINT = 'http://localhost:8003'

EXTRACTXT_FILES_UPLOAD_URL = '{}/upload-files/'.format(EXTRACTXT_ENDPOINT)
# EXTRACTXT_FILES_UPLOAD_URL = '/corpus/create-corpus-upload/'
# configurations that are related to the corpus and its data storage
# DATA_ROOT = '/data'
DATA_ROOT = os.path.join(PROXIMITY_BOT_PROJ, 'data', 'rmxbot')

CORPUS_ROOT = os.path.normpath(DATA_ROOT)

CORPUS_MAX_SIZE = 400

CORPUS_STATUS = (
    'newly-created',
    'file-upload',
)

# DATABASE configuration - MONGODB
MONGODB_NAME = 'rmx'
MONGODB_LOCATION = '127.0.0.1'
MONGODB_PORT = 27017
MONGODB_USR = 'dbuser_if_any'
MONGODB_PWD = 'password_if_any'

# names given to the mongodb collections
DATA_COLL = 'data'
IMAGE_COLL = 'image'
CORPUS_COLL = 'corpus'
CLUSTER_COLL = 'cluster'
