
from django.conf.urls import url
from django.urls import path, re_path

from . import views


urlpatterns = [

    path('', views.IndexView.as_view(), name='corpora_index'),

    url(r'^create/$', views.create),
    url(r'^create-from-upload/$', views.create_from_upload),

    url(r'^new/$', views.CreateFormView.as_view(), name='new_corpus'),

    path('create-from-text-files/',
         views.CreateFromTextFiles.as_view(),
         name='corpus_from_text_files'),

    path('create-from-text-files/<slug:corpusid>/',
         views.CreateFromTextFiles.as_view(),
         name='corpus_from_text_files'),

    path('file-extract-callback/',
         views.file_extract_callback_view, name="file_extract_callback"),

    path('create-corpus-upload/', views.create_corpus_upload),

    url(r'^(?P<docid>[0-9a-zA-Z]*)/$',
        views.CorpusDataView.as_view(), name='data_corpus'),


    path('sync-matrices/', views.sync_matrices),

    url(r'^(?P<corpusid>[0-9a-zA-Z]*)/file/(?P<dataid>[0-9a-zA-Z]*)/$',
        views.get_text_file),

    url(r'^(?P<corpusid>[0-9a-zA-Z]*)/context/', views.lemma_context),

    url(r'^nlp-callback/$', views.nlp_callback),
    url(r'^compute-matrices-callback/$', views.compute_matrices_callback),


    url(r'^test-task/$', views.test_celery_task),

    url(r'^(?P<docid>[0-9a-zA-Z]*)/urls/$',
        views.CorpusUrlsView.as_view(), name='corpus_urls'),

    url(r'^(?P<docid>[0-9a-zA-Z]*)/data/$',
        views.CorpusTextFilesView.as_view(), name='corpus_urls'),

    url(r'^(?P<docid>[0-9a-zA-Z]*)/data/edit/$',
        views.CorpusDataEditView.as_view(), name='corpus_urls'),


    url(r'^(?P<docid>[0-9a-zA-Z]*)/features/$', views.request_features),

    url(r'^(?P<docid>[0-9a-zA-Z]*)/features-html/$',
        views.request_features_html),


    url(r'^(?P<docid>[0-9a-zA-Z]*)/force-directed-graph/$',
        views.force_directed_graph),

    url(r'^(?P<docid>[0-9a-zA-Z]*)/kmeans/$', views.request_kmeans),

    url(r'^(?P<corpusid>[0-9a-zA-Z]*)/is-ready/(?P<feats>\d*)',
        views.is_ready),

    path('<slug:docid>/corpus-crawl-ready', views.crawl_is_ready),

    path('<slug:docid>/corpus-from-files-ready/',
         views.corpus_from_files_ready),

    path('corpus-data/', views.corpus_data, name="corpus_data"),

    path('expected-files/', views.ExpectedFiles.as_view(),
         name="expected_files"),

]
