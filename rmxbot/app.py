import os

from celery import Celery
from flask import Flask
from flask_graphql import GraphQLView

from .tasks import celeryconf


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'data')


STATIC_FOLDER = os.environ.get('STATIC_FOLDER')
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

def make_celery(app):

    celery = Celery(app.import_name,
                    include=['rmxbot.tasks.data', 'rmxbot.tasks.corpus'],
                    broker=app.config['BROKER_URL'],
                    backend=app.config['CELERY_RESULT_BACKEND'])

    celery.conf.update(app.config)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery


def create_app(static_folder: str = STATIC_FOLDER):
    """Building up the flask applicaiton."""
    app = Flask(__name__,
                static_folder=static_folder,
                static_url_path='/static'
                )
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    from rmxbot.contrib.utils.urls import ObjectidConverter
    from rmxbot.contrib.rmxjson import RmxEncoder

    app.url_map.converters['objectid'] = ObjectidConverter

    app.json_encoder = RmxEncoder

    # app.config.from_object('conf')
    app.config.update(
        BROKER_URL='redis://localhost:6379/0',
        CELERY_RESULT_BACKEND='redis://localhost:6379/0'
    )

    with app.app_context():
        from .apps.corpus.routes import corpus_app
        from .apps.home.routes import home_app
        from .apps.data.routes import data_app

        # from .apps.graph import graph_app
        from .schema import rmx_schema

        app.register_blueprint(corpus_app, url_prefix='/corpus')
        app.register_blueprint(data_app, url_prefix='/data')
        # app.register_blueprint(graph_app, url_prefix='/graph')
        app.register_blueprint(home_app)

        app.add_url_rule(
            '/graph',
            view_func=GraphQLView.as_view(
                'graph',
                schema=rmx_schema,
                graphiql=True  # for having the GraphiQL interface
            )
        )

    return app


celery = Celery('rmxbot')
celery.config_from_object(celeryconf)
