

from .apps.corpus.routes import corpus_app
from .apps.home.routes import home_app

# from .apps.data.routes import data_app


def register_apps(app):

    app.register_blueprint(corpus_app, url_prefix='/corpus')
    app.register_blueprint(home_app)
