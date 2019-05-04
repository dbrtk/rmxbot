
import os

from rmxbot.app import create_app

# # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#
# print(BASE_DIR)
# print(os.path.isdir(BASE_DIR))
#
# DATA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'data')
# STATIC_FOLDER = os.path.join(BASE_DIR, 'static')
#
# os.environ['RMX_SEARCH_CORPUS_SCRIPT'] = os.path.join(BASE_DIR, 'bin')
# os.environ['NLP_ENDPOINT'] = 'http://localhost:8001'
# os.environ['SCRASYNC_ENDPOINT'] = 'http://localhost:8002'
# os.environ['EXTRACTXT_ENDPOINT'] = 'http://localhost:8003'
#
# os.environ['DATA_ROOT'] = DATA_ROOT
# os.environ['TMP_DATA_DIR'] = os.path.join(DATA_ROOT, 'tmp')
# os.environ['MONGODB_LOCATION'] = 'localhost'
# os.environ['REDIS_HOST_NAME'] = 'localhost'
# os.environ['TEMPLATES_FOLDER'] = os.path.join(BASE_DIR, 'templates')

app = create_app()
