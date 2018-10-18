

from django.apps import AppConfig
# from .tasks import create_corpus


class CorpusConfig(AppConfig):
    """ configuration for the data app """
    name = 'rmxbot.apps.corpus'
    verbose_name = "Rmxbot' Corpus app"

    # def ready(self):
    #     """ overriding ready to register signals """
    #     import rmxbot.apps.data.signals.handlers
