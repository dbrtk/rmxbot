
from django.conf.urls import url
from django.urls import path, re_path

from . import views


urlpatterns = [

    # todo(): delete - moved to flask
    # path('', views.IndexView.as_view(), name='corpora_index'),

    # todo(): delete - moved to flask
    # path('create/', views.create),

    path('create-from-upload/', views.create_from_upload),

    # todo(): delete - moved to flask
    # path('new/', views.CreateFormView.as_view(), name='new_corpus'),

    # todo(): delete - moved to flask
    # path('create-from-text-files/',
    #      views.CreateFromTextFiles.as_view(),
    #      name='corpus_from_text_files'),


    # todo(): delete!
    # re_path(r'^create-from-text-files/(?P<corpusid>[0-9a-z]*)/$',
    #      views.CreateFromTextFiles.as_view(),
    #      name='corpus_from_text_files'),


    # todo(): delete - moved to flask
    # path('file-extract-callback/',
    #      views.file_extract_callback_view, name="file_extract_callback"),

    # todo(): delete - moved to flask
    # path('sync-matrices/', views.sync_matrices),



    # todo(): delete - moved to flask
    # re_path(r'^(?P<corpusid>[0-9a-zA-Z]*)/$',
    #         views.CorpusDataView.as_view(), name='data_corpus'),

    # todo(): delete - moved to flask
    # re_path(r'^(?P<corpusid>[0-9a-zA-Z]*)/data/$',
    #         views.Texts.as_view(), name='corpus_data'),

    # todo(): delete - moved to flask
    # re_path(r'^(?P<corpusid>[0-9a-zA-Z]*)/data/edit/$',
    #         views.TextsEdit.as_view(), name='corpus_data_edit'),

    # todo(): delete - moved to flask
    # re_path(r'^(?P<corpusid>[0-9a-zA-Z]*)/data/delete-texts/$',
    #         views.TextsDelete.as_view(), name='corpus_data_delete'),

    # todo(): delete - moved to flask
    # re_path(r'^(?P<corpusid>[0-9a-zA-Z]*)/file/(?P<dataid>[0-9a-zA-Z]*)/$',
    #         views.get_text_file),

    # todo(): delete - moved to flask
    # url(r'^(?P<corpusid>[0-9a-zA-Z]*)/context/', views.lemma_context),



    # todo(): delete - moved to flask
    # path('nlp-callback/', views.nlp_callback),

    # todo(): delete - moved to flask
    # path('compute-matrices-callback/', views.compute_matrices_callback),

    path('test-task/', views.test_celery_task),

    # todo(): delete - moved to flask
    # url(r'^(?P<docid>[0-9a-zA-Z]*)/features/$', views.request_features),

    # todo(): delete - moved to flask
    # url(r'^(?P<docid>[0-9a-zA-Z]*)/features-html/$',
    #     views.request_features_html),

    # todo(): delete - moved to flask
    # re_path(r'^(?P<docid>[0-9a-zA-Z]*)/force-directed-graph/$',
    #         views.force_directed_graph),


    # todo(): delete - moved to flask
    # re_path(r'^(?P<corpusid>[0-9a-zA-Z]*)/is-ready/(?P<feats>\d*)',
    #         views.is_ready),

    # todo(): delete - moved to flask
    # re_path(r'^(?P<corpusid>[0-9a-zA-Z]*)/corpus-crawl-ready/',
    #         views.crawl_is_ready),

    # todo(): delete - moved to flask
    # re_path(r'^(?P<corpusid>[0-9a-zA-Z]*)/corpus-from-files-ready/',
    #      views.corpus_from_files_ready),

    # todo(): delete - moved to flask
    # path('corpus-data/', views.corpus_data, name="corpus_data"),

    path('expected-files/', views.ExpectedFiles.as_view(),
         name="expected_files"),

    # todo(): delete
    # path('integrity-check-callback/', views.integrity_check_callback),

]
