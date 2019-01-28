

from django.conf.urls import url
from django.urls import path
from rmxbot.apps.data import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'thesite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # url(r'^$', 'rmxbot.apps.data.views.get_data'),

    path('', views.index, name='data_index'),

    path('create/', views.create, name='create_data'),
    path('create-data-object/', views.create, name='create_data_object'),

    path('create-from-file/', views.create_from_file, name='create_from_file'),

    path('data-to-corpus/', views.data_to_corpus, name='data_to_corpus'),
    path('edit-many/', views.edit_many, name='edit_many'),

    url(r'^webpage/(?P<docid>[0-9a-zA-Z]*)/$', views.webpage),

    url(r'^text/(?P<docid>[0-9a-zA-Z]*)/$', views.text),
]
